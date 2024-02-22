from fpdf import FPDF

CENTER = "C"


def create_custom_invoice(
    title: str,
    subtitle: str,
    items: list[tuple[str, int, int]],
    filename: str = "invoice.pdf",
):
    """
    Creates a custom invoice PDF document using fpdf2.

    Args:
        title: Title of the invoice.
        subtitle: Subtitle of the invoice.
        items: List of tuples containing item details (name, quantity, price).
        filename: Name of the output PDF file.

    Example:
    >>> create_custom_invoice(
    ...     "Invoice",
    ...     "Number #123",
    ...     [
    ...         ("Software Development 1", 1, 5500),
    ...         ("Consultancy 2", 1, 1000),
    ...         ("Equipment", 3, 300),
    ...     ]
    ... )
    """
    pdf = FPDF()

    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=title, ln=True, align=CENTER)
    pdf.cell(200, 10, txt=subtitle, ln=True, align=CENTER)
    pdf.ln(10)

    col_width = 60
    row_height = 10

    for item in items:
        for element in item:
            pdf.cell(col_width, row_height, txt=str(element), border=1)
        pdf.ln(row_height)

    pdf.output(filename)
