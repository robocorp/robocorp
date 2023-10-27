from robocorp.tasks import task


@task
def no_args():
	print("Inside task")


@task
def with_args(number: int, toggle: bool) -> str:
	print(f"Got integer: {number}, and boolean: {toggle}")
	return "Some return value"
