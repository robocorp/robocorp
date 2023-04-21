from pprint import PrettyPrinter
from pathlib import Path

from robo.libs.robocorp import create_output_work_item, get_inputs, get_outputs, iter_input_work_items
from robo.libs.excel import open_workbook


pp = PrettyPrinter(indent=4)


def task_produce():
    for item in iter_input_work_items():
        pp.pprint(item)
        path = Path(item.get_file("orders.xlsx"))
        groups = (
            open_workbook(path).worksheet(0).as_table(header=True).group_by_column("Name")
        )
        for customer in groups:
            name = customer.get_cell(0, "Name")
            address = customer.get_cell(0, "Zip")
            orders = customer.get_column("Item", as_list=True)
            create_output_work_item({"Name": name, "Zip": address, "Items": orders}, save=True)


if __name__ == "__main__":
    task_produce()
    pp.pprint(f"INPUTS: {get_inputs()}")
    pp.pprint(f"OUTPUTS: {get_outputs()}")
