from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser


def extract_pdf_metadata(pdf_file):
    """
    Extracts metadata from a PDF file using PDFMiner.six.

    Args:
        pdf_file: Path to the PDF file.

    Returns:
        A dictionary containing PDF metadata.
    """
    metadata = {}
    with open(pdf_file, "rb") as f:
        parser = PDFParser(f)
        document = PDFDocument(parser)

        doc_info = document.info
        # Extract metadata
        metadata = {
            "Title": doc_info.get("Title"),
            "Author": doc_info.get("Author"),
            "Subject": doc_info.get("Subject"),
            "Keywords": doc_info.get("Keywords"),
            "Producer": doc_info.get("Producer"),
            "Creator": doc_info.get("Creator"),
            "CreationDate": doc_info.get("CreationDate"),
        }

    return metadata
