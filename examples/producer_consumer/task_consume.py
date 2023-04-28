from pprint import PrettyPrinter

from robocorp.workitems import Error, WorkItem, inputs, outputs

pp = PrettyPrinter(indent=4)


def process_order(name, address, items):
    pp.pprint(f"Order: {items} Name: {name} Zip: {address}")


def process_workitem(item: WorkItem):
    try:
        name = item.payload["Name"]
        address = item.payload["Zip"]
        items = item.payload["Items"]

        process_order(name, address, items)
    except Exception as err:
        item.fail(Error.APPLICATION, "UNCAUGHT_ERROR", err)


def task_consume():
    input_items_info = []
    for item in inputs.iterate():
        process_workitem(item)
        input_items_info.append(item)
    return input_items_info


if __name__ == "__main__":
    input_items = task_consume()
    pp.pprint("INPUTS:")
    for item in input_items:
        pp.pprint(item)
    pp.pprint("OUTPUTS:")
    pp.pprint(outputs.show())
