import os
from dotenv import load_dotenv

import streamlit as st
from pypdf import PdfReader
from google import genai


# -----------------------------
# Basic Setup
# -----------------------------
load_dotenv()

st.set_page_config(
    page_title="Beginner AI Document Assistant",
    page_icon="📄",
    layout="wide"
)

api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None

MODEL_NAME = "gemini-2.0-flash"


# -----------------------------
# Helper Functions
# -----------------------------
def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF file."""
    try:
        reader = PdfReader(uploaded_file)
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        return text.strip()

    except Exception as e:
        return f"Error reading PDF: {e}"


def extract_text_from_txt(uploaded_file):
    """Extract text from uploaded TXT file."""
    try:
        return uploaded_file.read().decode("utf-8").strip()
    except Exception as e:
        return f"Error reading TXT file: {e}"


def limit_text(text, max_chars=12000):
    """
    Limit text sent to AI to keep the beginner app simple.
    This is not advanced RAG. It only prevents very large prompts.
    """
    if len(text) > max_chars:
        return text[:max_chars]
    return text


def ask_ai(prompt):
    """Send prompt to Gemini API and return response."""
    if client is None:
        return "Gemini API key is missing. Please add it to your .env file."

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text

    except Exception as e:
        return f"Error calling Gemini API: {e}"


def summarize_document(document_text):
    prompt = f"""
You are a helpful AI assistant. Summarize documents clearly and simply.
Do not invent information. If something is not mentioned, say it is not mentioned.

Please summarize the following document in a simple business-friendly format.

Include:
1. Short summary
2. Key points
3. Important risks or concerns
4. Suggested next steps

Document:
{limit_text(document_text)}
"""
    return ask_ai(prompt)


def extract_action_points(document_text):
    prompt = f"""
You are a helpful AI assistant. Extract action points from text.
Only use information available in the document. Do not invent owners or deadlines.

Extract action points from the following document.

Return the output in this format:

| Action Point | Owner | Deadline | Priority |
|---|---|---|---|

If owner, deadline, or priority is not mentioned, write "Not specified".

Document:
{limit_text(document_text)}
"""
    return ask_ai(prompt)


def draft_email(document_text):
    prompt = f"""
You are a helpful AI assistant. Draft professional and clear business emails.
Keep the tone polite and simple.

Based on the document below, draft a simple professional email.

The email should:
- Be clear and polite
- Summarize the main message
- Mention key action points if available
- Ask the receiver to review or respond where needed

Do not include a fake recipient name unless mentioned in the document.

Document:
{limit_text(document_text)}
"""
    return ask_ai(prompt)


def answer_question(document_text, question):
    prompt = f"""
You are a helpful AI assistant answering questions based on a document.
Use only the document content. If the answer is not available, say:
"The document does not mention this."

Document:
{limit_text(document_text)}

Question:
{question}

Answer the question clearly and simply.
"""
    return ask_ai(prompt)


# -----------------------------
# App UI
# -----------------------------
st.title("Beginner AI Document Assistant")

st.write(
    "A beginner learning project to understand how AI can summarize documents, "
    "answer basic questions, extract action points, and draft simple emails."
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

if uploaded_file is not None:
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".pdf"):
        document_text = extract_text_from_pdf(uploaded_file)
    elif file_name.endswith(".txt"):
        document_text = extract_text_from_txt(uploaded_file)

    if document_text:
        st.success("Document text extracted successfully.")

        with st.expander("View extracted text"):
            st.text_area(
                "Extracted Text",
                document_text,
                height=300
            )

        st.subheader("AI Actions")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Summarize Document"):
                with st.spinner("Generating summary..."):
                    result = summarize_document(document_text)
                    st.markdown(result)

        with col2:
            if st.button("Extract Action Points"):
                with st.spinner("Extracting action points..."):
                    result = extract_action_points(document_text)
                    st.markdown(result)

        with col3:
            if st.button("Draft Email"):
                with st.spinner("Drafting email..."):
                    result = draft_email(document_text)
                    st.markdown(result)

        st.subheader("Ask a Question")

        question = st.text_input("Ask something about the uploaded document")

        if st.button("Get Answer"):
            if question.strip():
                with st.spinner("Finding answer..."):
                    result = answer_question(document_text, question)
                    st.markdown(result)
            else:
                st.error("Please enter a question first.")

else:
    st.info("Upload a PDF or TXT file to begin.")