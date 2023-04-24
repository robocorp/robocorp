from pprint import PrettyPrinter
from pathlib import Path

from robo.libs.robocorp import get_inputs
from robo.libs.robocorp.workitems import inputs, outputs
from robo.libs.excel import open_workbook


pp = PrettyPrinter(indent=4)


def task_produce():
    # for item in inputs:
    item = next(inputs)
    pp.pprint(item)
    path = Path(item.get_file("orders.xlsx"))
    groups = (
        open_workbook(path).worksheet(0).as_table(header=True).group_by_column("Name")
    )
    for customer in groups:
        name = customer.get_cell(0, "Name")
        address = customer.get_cell(0, "Zip")
        orders = customer.get_column("Item", as_list=True)
        outputs.create({"Name": name, "Zip": address, "Items": orders}, save=True)
    item.done()


if __name__ == "__main__":
    task_produce()
    pp.pprint(f"INPUTS: {get_inputs()}")
    pp.pprint(f"OUTPUTS: {list(outputs)}")
