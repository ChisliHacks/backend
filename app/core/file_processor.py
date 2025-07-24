import os
from pathlib import Path
from typing import Optional

try:
    import PyPDF2
    PYPDF_AVAILABLE = True
except ImportError:
    try:
        import pypdf
        PYPDF_AVAILABLE = True
        PyPDF2 = pypdf  # Use pypdf as fallback
    except ImportError:
        PYPDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


class FileProcessor:
    """Service for extracting text content from various file types"""

    @staticmethod
    def extract_text_from_file(file_path: str) -> Optional[str]:
        """
        Extract text content from uploaded files
        Supports: PDF, DOCX, TXT, MD
        """
        if not os.path.exists(file_path):
            return None

        file_path_obj = Path(file_path)
        file_extension = file_path_obj.suffix.lower()

        try:
            if file_extension == '.pdf':
                return FileProcessor._extract_from_pdf(file_path)
            elif file_extension == '.docx' and DOCX_AVAILABLE:
                return FileProcessor._extract_from_docx(file_path)
            elif file_extension in ['.txt', '.md']:
                return FileProcessor._extract_from_text(file_path)
            else:
                return f"File type {file_extension} not supported or required dependencies not installed"
        except Exception as e:
            print(f"Error extracting text from {file_path}: {e}")
            return None

    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        if not PYPDF_AVAILABLE:
            # For now, return a placeholder message when PDF libraries are not available
            return "PDF uploaded successfully. PDF text extraction requires PyPDF2 or pypdf library. Please install dependencies and try again, or the content will be summarized from the description."

        try:
            text = ""
            with open(file_path, 'rb') as file:
                # Try PyPDF2 first, then fallback to pypdf
                if hasattr(PyPDF2, 'PdfReader'):
                    # Using PyPDF2 or newer pypdf
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                else:
                    # Using older PyPDF2
                    pdf_reader = PyPDF2.PdfFileReader(file)
                    for page_num in range(pdf_reader.numPages):
                        page = pdf_reader.getPage(page_num)
                        text += page.extractText() + "\n"
            return text.strip()
        except Exception as e:
            return f"Error extracting text from PDF: {str(e)}. The file was uploaded successfully, but text extraction failed."

    @staticmethod
    def _extract_from_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        if not DOCX_AVAILABLE:
            return "DOCX processing not available - python-docx not installed"

        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()

    @staticmethod
    def _extract_from_text(file_path: str) -> str:
        """Extract text from plain text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read().strip()

    @staticmethod
    def get_supported_extensions() -> list:
        """Return list of supported file extensions - prioritize PDF"""
        # Always include PDF as primary format
        extensions = ['.pdf']

        # Add other formats if dependencies are available
        extensions.extend(['.txt', '.md'])  # Always supported

        if DOCX_AVAILABLE:
            extensions.append('.docx')

        return extensions
