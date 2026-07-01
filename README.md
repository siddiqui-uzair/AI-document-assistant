# Beginner AI Document Assistant

A simple beginner project built with Python and Streamlit to test how an AI API can help with basic document tasks.

## Features

- Upload PDF or TXT files
- Summarize document content
- Ask basic questions from the document
- Extract simple action points
- Draft a short email

## Tech Used

- Python
- Streamlit
- Groq API
- Llama model
- PyPDF

## How to Run

Install the required packages:

```bash
pip install -r requirements.txt

Create a .env file and add your Groq API key:
GROQ_API_KEY=your_api_key_here

streamlit run app.py

A sample file is included in sample_docs/sample_project_note.txt for testing.

## Note

This is a beginner learning project and is not production-ready. Do not upload confidential or sensitive documents.

A sample file is included in `sample_docs/sample_project_note.txt` for testing.