from pypdf import PdfReader


def extract_images_from_first_page(pdf_file: str, output_dir: str) -> None:
    """
    Extracts images from the first page of a PDF file using PyPDF.

    Args:
        pdf_file: Path to the PDF file.
        output_dir: Path dir to save the extracted images.
    """
    reader = PdfReader(pdf_file)

    for page_num, page in enumerate(reader.pages):
        count = 0

        for image_file_object in page.images:
            with open(f"{output_dir}/page_{page_num}_image_{count}.png", "wb") as fp:
                fp.write(image_file_object.data)
                count += 1
