# Reserving and releasing input items

When an execution in Control Room starts, the first input item is automatically
reserved. This first item is also loaded by the library when the task execution
starts.

After an item has been handled, it should be released as either passed or
failed. There can only be one reserved input item at a time.

Reserving can be done explicitly by calling the reserve method, which also acts
as a context manager:

```python
with workitems.inputs.reserve() as item:
    print("Handling item!")
```

Another option is to loop through all inputs, which implicitly reserves and
releases the corresponding items:

```python
for item in workitems.inputs:
    print("Handling item!")
```

Releasing can also be done explicitly to set specific errors, or to mark items
as done before exiting the block:

```python
for item in workitems.inputs:
    order_id = item.payload["order_id"]

    if not is_valid_id(order_id):
        item.fail(code="INVALID_ID", message=f"Invalid order id: {order_id}")

    ...

    item.done()
```
