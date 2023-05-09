import os
from robocorp.excel import open_workbook
from robocorp.tasks import task
from robocorp.workitems import Error, inputs, outputs


@task
def producer():
    with inputs.reserve() as item:
        path = item.get_file("orders.xlsx")
        groups = (
            open_workbook(path)
            .worksheet(0)
            .as_table(header=True)
            .group_by_column("Name")
        )

        for customer in groups:
            name = customer.get_cell(0, "Name")
            address = customer.get_cell(0, "Zip")
            orders = customer.get_column("Item", as_list=True)
            outputs.create({"Name": name, "Zip": address, "Items": orders})


@task
def consumer():
    for item in inputs.iterate():
        try:
            name = item.payload["Name"]
            address = item.payload["Zip"]
            items = item.payload["Items"]
            print(f"Name: {name}, Address: {address}, Items: {items}")
            item.done()
        except KeyError as err:
            item.fail(Error.APPLICATION, "INVALID_PAYLOAD", str(err))
