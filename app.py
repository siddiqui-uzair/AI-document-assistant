import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader


APP_TITLE = "Beginner AI Document Assistant"
MODEL_NAME = "llama-3.1-8b-instant"
MAX_DOCUMENT_CHARS = 4000


load_dotenv()

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📄",
    layout="wide"
)

groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key) if groq_api_key else None


def read_pdf(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        pages = []

        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)

        return "\n".join(pages).strip()

    except Exception as error:
        return f"Error reading PDF file: {error}"


def read_txt(uploaded_file):
    try:
        return uploaded_file.read().decode("utf-8").strip()
    except Exception as error:
        return f"Error reading text file: {error}"


def trim_document(text):
    if len(text) <= MAX_DOCUMENT_CHARS:
        return text

    return text[:MAX_DOCUMENT_CHARS]


def demo_reply(prompt):
    prompt = prompt.lower()

    if "summarize" in prompt:
        return """
## Demo Summary

The document was uploaded and processed successfully.

In API mode, this section would show a generated summary with key points, risks, and suggested next steps.

This demo response is only used when the API key is missing or unavailable.
"""

    if "action point" in prompt:
        return """
| Action Point | Owner | Deadline | Priority |
|---|---|---|---|
| Review the document | Not specified | Not specified | Medium |
| Note important points | Not specified | Not specified | Medium |

This is a demo response because the AI API is currently unavailable.
"""

    if "email" in prompt:
        return """
Dear Team,

Please review the uploaded document and note the important points and action items.

This is a demo email because the AI API is currently unavailable.

Kind regards,
"""

    return """
This is a demo response because the AI API is currently unavailable.

In API mode, the assistant would answer using the uploaded document.
"""


def get_ai_response(prompt):
    if client is None:
        return (
            "## API Key Missing\n\n"
            "Groq API key was not found, so demo mode is being used.\n\n"
            + demo_reply(prompt)
        )

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant. Keep answers clear and simple. "
                        "Use only the document content provided by the user. "
                        "Do not make up details."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.3,
            max_tokens=800,
        )

        return completion.choices[0].message.content

    except Exception as error:
        error_text = str(error).lower()

        if "429" in error_text or "rate limit" in error_text or "quota" in error_text:
            return (
                "## API Limit Reached\n\n"
                "The Groq API limit was reached, so demo mode is being used.\n\n"
                + demo_reply(prompt)
            )

        if "401" in error_text or "authentication" in error_text or "invalid api key" in error_text:
            return (
                "## API Authentication Issue\n\n"
                "The Groq API key is missing, invalid, or restricted, so demo mode is being used.\n\n"
                + demo_reply(prompt)
            )

        return f"Error calling Groq API: {error}"


def summarize_document(document_text):
    prompt = f"""
Summarize the document below in a simple business-friendly format.

Include:
1. Short summary
2. Key points
3. Important risks or concerns
4. Suggested next steps

Rules:
- Do not invent information.
- If something is not mentioned, say it is not mentioned.

Document:
{trim_document(document_text)}
"""
    return get_ai_response(prompt)


def extract_actions(document_text):
    prompt = f"""
Extract action points from the document below.

Return the result in this table format:

| Action Point | Owner | Deadline | Priority |
|---|---|---|---|

Rules:
- Use only details from the document.
- Do not invent owners or deadlines.
- If owner, deadline, or priority is missing, write "Not specified".

Document:
{trim_document(document_text)}
"""
    return get_ai_response(prompt)


def create_email_draft(document_text):
    prompt = f"""
Draft a simple professional email based on the document below.

The email should:
- Be clear and polite
- Summarize the main message
- Mention key action points if available
- Ask the receiver to review or respond where needed
- Not include fake names unless they are mentioned in the document
- Not include placeholders like [Your Name], [Recipient Name], or [Company Name]
- End with "Kind regards,"

Document:
{trim_document(document_text)}
"""
    return get_ai_response(prompt)


def answer_document_question(document_text, question):
    prompt = f"""
Answer the question using only the document content.

If the answer is not available, say:
"The document does not mention this."

Document:
{trim_document(document_text)}

Question:
{question}

Answer:
"""
    return get_ai_response(prompt)


st.title(APP_TITLE)

st.write(
    "A small learning project for summarizing documents, asking basic questions, "
    "extracting action points, and drafting simple emails using an AI API."
)

st.warning(
    "Privacy Note: This is a learning project. Do not upload confidential, legal, "
    "financial, HR, or sensitive company documents."
)

uploaded_file = st.file_uploader(
    "Upload a PDF or TXT file",
    type=["pdf", "txt"]
)

document_text = ""

if uploaded_file:
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".pdf"):
        document_text = read_pdf(uploaded_file)
    elif file_name.endswith(".txt"):
        document_text = read_txt(uploaded_file)

    if document_text:
        st.success("Document text extracted successfully.")

        with st.expander("View extracted text"):
            st.text_area("Extracted Text", document_text, height=300)

        st.subheader("AI Actions")

        summary_col, actions_col, email_col = st.columns(3)

        with summary_col:
            if st.button("Summarize Document"):
                with st.spinner("Generating summary..."):
                    st.markdown(summarize_document(document_text))

        with actions_col:
            if st.button("Extract Action Points"):
                with st.spinner("Extracting action points..."):
                    st.markdown(extract_actions(document_text))

        with email_col:
            if st.button("Draft Email"):
                with st.spinner("Drafting email..."):
                    st.markdown(create_email_draft(document_text))

        st.subheader("Ask a Question")

        question = st.text_input("Ask something about the uploaded document")

        if st.button("Get Answer"):
            if question.strip():
                with st.spinner("Finding answer..."):
                    st.markdown(answer_document_question(document_text, question))
            else:
                st.error("Please enter a question first.")

else:
    st.info("Upload a PDF or TXT file to begin.")