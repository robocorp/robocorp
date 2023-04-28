from pathlib import Path
from pprint import PrettyPrinter

from robocorp.excel import open_workbook
from robocorp.workitems.workitems import inputs, outputs

pp = PrettyPrinter(indent=4)


def print_items(input_items):
    pp.pprint("INPUTS:")
    for input_item in input_items:
        pp.pprint(input_item)
    pp.pprint("OUTPUTS:")
    for output_item in outputs.show():
        pp.pprint(output_item)


def task_produce():
    input_items = []
    # for item in inputs:
    print_items(input_items)
    input_item = inputs.reserve()
    input_items.append(input_item)
    pp.pprint("Take next")
    print_items(input_items)
    path = Path(input_item.get_file("orders.xlsx"))
    groups = (
        open_workbook(path).worksheet(0).as_table(header=True).group_by_column("Name")
    )
    for customer in groups:
        name = customer.get_cell(0, "Name")
        address = customer.get_cell(0, "Zip")
        orders = customer.get_column("Item", as_list=True)
        # outputs.create({"Name": name, "Zip": address, "Items": orders}, save=True)
        inputs.create_output({"Name": name, "Zip": address, "Items": orders}, save=True)
    input_item.done()
    return input_items


if __name__ == "__main__":
    input_items = task_produce()
    print_items(input_items)
