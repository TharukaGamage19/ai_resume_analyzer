import pdfplumber
import docx
import tempfile
import os


def extract_text(uploaded_file) -> str:
    """
    Extract text from uploaded Streamlit file.
    Supports PDF, DOCX, and TXT formats.
    """
    filename = uploaded_file.name.lower()
    suffix = os.path.splitext(uploaded_file.name)[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    try:
        if filename.endswith(".pdf"):
            return _extract_pdf(tmp_path)
        elif filename.endswith(".docx"):
            return _extract_docx(tmp_path)
        elif filename.endswith(".txt"):
            return _extract_txt(tmp_path)
        else:
            raise ValueError(f"Unsupported file type: {filename}")
    finally:
        os.unlink(tmp_path)


def _extract_pdf(path: str) -> str:
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def _extract_docx(path: str) -> str:
    doc = docx.Document(path)
    text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    return text.strip()


def _extract_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()