from robocorp.excel import open_workbook
from robocorp.tasks import task
from robocorp import workitems


@task
def producer():
    """Split Excel rows into multiple work items"""
    for item in workitems.inputs:
        path = item.download_file("orders.xlsx")
        worksheet = open_workbook(path).worksheet(0)

        for row in worksheet.as_table(header=True):
            payload = {
                "Name": row["Name"],
                "Zip": row["Zip"],
                "Product": row["Item"],
            }
            workitems.outputs.create(payload)


@task
def consumer():
    """Process all input work items"""
    for item in workitems.inputs:
        try:
            name = item.payload["Name"]
            zipcode = item.payload["Zip"]
            product = item.payload["Product"]
            print(f"Processing order: {name}, {zipcode}, {product}")
            assert 1000 <= zipcode <= 9999, "Invalid ZIP code"
            item.done()
        except AssertionError as err:
            item.fail("BUSINESS", code="INVALID_ORDER", message=str(err))
        except KeyError as err:
            item.fail("APPLICATION", message=str(err))
