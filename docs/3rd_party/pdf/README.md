# PDFs

In this section we are going to tackle a few libraries and tools that can be used to work with PDF files.

### PyPDF
Perform common tasks like merging, splitting and adding watermarks to PDF documents.

### PDFMiner.six
Get detailed access to the internal structure of PDF documents, such as extracting text with precise positioning,
extracting images, or navigating complex document structures.

### fpdf2
The library is specifically designed for creating PDF files from scratch.

## Usage

### PyPDF

```python
from pypdf import PdfReader

reader = PdfReader("example.pdf")

print(len(reader.pages))
```

### PDFMiner.six

```python
from pdfminer.high_level import extract_text

print(extract_text('samples/simple1.pdf'))
```

### fpdf2

```python
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=25)

# create a cell
pdf.cell(200, 10, txt="Hello World!", ln=1, align='C')

pdf.output("info.pdf")
```

> AI/LLM's are quite good with `pdfs`.  
> 👉 Try asking [ReMark](https://chat.robocorp.com)

###### Various [snippets](snippets)

- [Create an invoice PDF](snippets/fpdf2/create_invoice.py)
- [Extract PDF metadata](snippets/pdfminer/extract_metadata.py)
- [Extract images from PDF](snippets/pypdf/extract_images.py)

## Links and references

### PyPDF
- [PyPI](https://pypi.org/project/pypdf/)
- [Documentation](https://pypdf.readthedocs.io/en/latest/)

### PDFMiner.six
- [PyPI](https://pypi.org/project/pdfminer.six/)
- [Documentation](https://pdfminersix.readthedocs.io/en/latest/)

### fpdf2
- [PyPI](https://pypi.org/project/fpdf2/)
- [Documentation](https://py-pdf.github.io/fpdf2/)
- [API reference](https://py-pdf.github.io/fpdf2/fpdf/)
