from pprint import PrettyPrinter
from robo.libs.robocorp import WorkItem


pp = PrettyPrinter(indent=4)


def process_order(name, address, items):
    pp.pprint(f"Order: {items} Name: {name} Zip: {address}")
    if name == "Gregg Arroyo":
        raise ValueError("Unacceptable name")


def process_workitem(item: WorkItem):
    name = item.payload["Name"]
    address = item.payload["Zip"]
    items = item.payload["Items"]

    process_order(name, address, items)
