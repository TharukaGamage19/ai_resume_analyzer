import pdfplumber
import docx
import io


def extract_text(uploaded_file) -> str:
    """
    Extract text from uploaded file.
    Supports PDF, DOCX, and TXT formats.
    """
    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):
        return _extract_pdf(uploaded_file)
    elif filename.endswith(".docx"):
        return _extract_docx(uploaded_file)
    elif filename.endswith(".txt"):
        return _extract_txt(uploaded_file)
    else:
        raise ValueError(f"Unsupported file type: {filename}")


def _extract_pdf(uploaded_file) -> str:
    """Extract text from PDF using pdfplumber."""
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def _extract_docx(uploaded_file) -> str:
    """Extract text from DOCX using python-docx."""
    file_bytes = io.BytesIO(uploaded_file.read())
    doc = docx.Document(file_bytes)
    text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    return text.strip()


def _extract_txt(uploaded_file) -> str:
    """Extract text from plain TXT file."""
    return uploaded_file.read().decode("utf-8").strip()