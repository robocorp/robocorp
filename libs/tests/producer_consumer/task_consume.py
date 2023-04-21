from pprint import PrettyPrinter

from robo.libs.robocorp import iter_input_work_items, release_input_work_item, get_inputs, get_outputs, State, Error

from consumer import process_workitem


pp = PrettyPrinter(indent=4)


def task_consume():

    try:
        for item in iter_input_work_items():
            process_workitem(item)
    except Exception as err:
        release_input_work_item(State.FAILED, Error.APPLICATION, "UNCAUGHT_ERROR", err)


if __name__ == "__main__":
    task_consume()
    pp.pprint(f"INPUTS: {get_inputs()}")
    pp.pprint(f"OUTPUTS: {get_outputs()}")
