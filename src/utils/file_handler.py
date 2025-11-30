import aiofiles
from pathlib import Path
from typing import BinaryIO, Optional
from io import BytesIO
import logging
import mimetypes

# Import libraries with proper error handling
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


async def read_file_async(file_path: Path) -> str:
    """Read a file asynchronously."""
    async with aiofiles.open(file_path, 'r') as f:
        return await f.read()


def read_file(file_path: Path) -> str:
    """Synchronous file reading for backward compatibility."""
    return file_path.read_text()


def extract_text_from_pdf(file: BinaryIO) -> str:
    """Extract text from PDF file."""
    if not PDF_AVAILABLE:
        raise ValueError(
            "PDF processing not available. Install PyPDF2: pip install PyPDF2")

    try:
        # Read the file content into BytesIO for compatibility
        content = file.read()
        if len(content) == 0:
            raise ValueError("PDF file is empty")

        file_like = BytesIO(content)
        pdf_reader = PyPDF2.PdfReader(file_like)

        if len(pdf_reader.pages) == 0:
            raise ValueError("PDF file has no pages")

        text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text.strip():
                    text += page_text + "\n"
            except Exception as e:
                logging.warning(
                    f"Failed to extract text from PDF page {page_num}: {e}")
                continue

        if not text.strip():
            raise ValueError("No text could be extracted from the PDF")

        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to process PDF file: {str(e)}")


def extract_text_from_docx(file: BinaryIO) -> str:
    """Extract text from DOCX file."""
    if not DOCX_AVAILABLE:
        raise ValueError(
            "DOCX processing not available. Install python-docx: pip install python-docx")

    try:
        # Read the file content into BytesIO for compatibility
        content = file.read()
        if len(content) == 0:
            raise ValueError("DOCX file is empty")

        file_like = BytesIO(content)
        doc = docx.Document(file_like)

        text_parts = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text.strip())

        if not text_parts:
            raise ValueError("No text content found in DOCX file")

        text = "\n".join(text_parts)
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to process DOCX file: {str(e)}")


def extract_text_from_txt(file: BinaryIO) -> str:
    """Extract text from TXT file with encoding detection."""
    try:
        content = file.read()
        if len(content) == 0:
            raise ValueError("Text file is empty")

        # Convert memoryview or bytearray to bytes first
        if isinstance(content, memoryview):
            content = bytes(content)
        elif isinstance(content, bytearray):
            content = bytes(content)

        if isinstance(content, bytes):
            # Try multiple encodings
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
            decoded_content: str = ""

            for encoding in encodings:
                try:
                    decoded_content = content.decode(encoding)
                    break
                except (UnicodeDecodeError, AttributeError):
                    continue

            if not decoded_content:
                raise ValueError(
                    "Could not decode text file with supported encodings")
            content = decoded_content

        # Ensure content is string
        if not isinstance(content, str):
            content = str(content)

        text = content.strip()
        if not text:
            raise ValueError("Text file contains no readable content")

        return text
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to process text file: {str(e)}")


def validate_file_type(filename: str) -> bool:
    """Validate if file type is supported."""
    allowed_extensions = {'.txt', '.pdf', '.docx'}
    file_extension = Path(filename).suffix.lower()
    return file_extension in allowed_extensions


def get_file_mime_type(file_content: bytes, filename: str) -> Optional[str]:
    """Get MIME type of file based on content and filename."""
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type


def validate_file_size(file_content: bytes, max_size_mb: int = 10) -> bool:
    """Validate file size is within limits."""
    max_size_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes
    return len(file_content) <= max_size_bytes


def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """
    Extract text from uploaded file based on extension with comprehensive validation.

    Args:
        file_content: Binary file content as bytes
        filename: Name of the file with extension

    Returns:
        Extracted text content

    Raises:
        ValueError: If file type is not supported or validation fails
    """
    if not filename:
        raise ValueError("Filename is required")

    # Validate file extension
    if not validate_file_type(filename):
        file_extension = Path(filename).suffix.lower()
        raise ValueError(
            f"Unsupported file type: {file_extension}. Supported types: .txt, .pdf, .docx")

    file_extension = Path(filename).suffix.lower()

    # Log file processing attempt
    logging.info(f"Processing file: {filename} (type: {file_extension})")

    try:
        # Convert bytes to BinaryIO
        file_like = BytesIO(file_content)

        if file_extension == '.pdf':
            return extract_text_from_pdf(file_like)
        elif file_extension == '.docx':
            return extract_text_from_docx(file_like)
        elif file_extension == '.txt':
            return extract_text_from_txt(file_like)
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")
    except Exception as e:
        logging.error(f"Failed to extract text from {filename}: {str(e)}")
        raise


async def process_input_folder_file(file_path: Path) -> dict:
    """
    Process a file from the input folder.

    Args:
        file_path: Path to the file in input folder

    Returns:
        Dict containing extracted text and metadata
    """
    if not file_path.exists():
        raise ValueError(f"File not found: {file_path}")

    if not validate_file_type(file_path.name):
        raise ValueError(f"Unsupported file type: {file_path.suffix}")

    # Read file content
    with open(file_path, 'rb') as f:
        file_content = f.read()

    content = extract_text_from_file(file_content, file_path.name)

    return {
        "filename": file_path.name,
        "content": content,
        "file_size": file_path.stat().st_size,
        "modified_time": file_path.stat().st_mtime,
        "file_type": file_path.suffix.lower()
    }


def scan_input_folder(input_dir):
    """Scan input folder for supported files."""
    from pathlib import Path
    if not input_dir.exists():
        input_dir.mkdir(parents=True, exist_ok=True)
        return []

    supported_files = []
    for file_path in input_dir.iterdir():
        if file_path.is_file() and validate_file_type(file_path.name):
            supported_files.append(file_path)

    return sorted(supported_files, key=lambda x: x.stat().st_mtime)


async def save_output_file(content, output_dir, filename_prefix="rewritten_email"):
    """Save processed content to output folder."""
    from datetime import datetime
    from pathlib import Path

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.txt"
    output_path = output_dir / filename

    async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
        await f.write(content)

    return output_path
