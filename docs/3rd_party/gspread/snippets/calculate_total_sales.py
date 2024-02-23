import gspread

gc = gspread.service_account()


def authenticate_and_open_sheet(
    spreadsheet_title: str, worksheet_title: str
) -> gspread.worksheet.Worksheet:
    # Set up the credentials
    gc = gspread.service_account()

    # Open the specified spreadsheet and worksheet
    spreadsheet = gc.open(spreadsheet_title)
    worksheet = spreadsheet.worksheet(worksheet_title)

    return worksheet


def calculate_total_sales(worksheet):
    # Get all records from the worksheet
    # Worksheet must have quantity and price headers in the first row
    data = worksheet.get_all_records()

    for row in data:
        quantity = row["quantity"]
        price = row["price"]
        total_sales = quantity * price
        row["total_sales"] = total_sales

    # Add a summary row at the end with total sales
    total_sales_summary = sum(row["total_sales"] for row in data)
    worksheet.append_row(["Total Sales", "", total_sales_summary])
