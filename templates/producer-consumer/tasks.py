from robocorp.excel import open_workbook
from robocorp.tasks import task
from robocorp.workitems import ExceptionType, inputs, outputs


@task
def producer():
    """Split Excel rows into multiple work items"""
    with inputs.reserve() as item:
        path = item.get_file("orders.xlsx")
        orders = open_workbook(path).worksheet("Sheet1").as_table()

        for row in orders:
            payload = {
                "Name": row["Name"],
                "Zip": row["Zip"],
                "Item": row["Item"],
            }
            outputs.create(payload)


@task
def consumer():
    """Process all input work items"""
    for item in inputs.iterate():
        try:
            name = item.payload["Name"]
            address = item.payload["Zip"]
            item = item.payload["Item"]
            print(f"Processing order: {name}, {address}, {item}")
            item.done()
        except KeyError as err:
            item.fail(ExceptionType.APPLICATION, "MISSING_VALUE", str(err))
