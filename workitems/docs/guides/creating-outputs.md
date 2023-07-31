# Creating outputs

For each input work item, you can create any amount of output work items.
These will be forwarded to the next step of a process, or set as the final
result if there are no further steps.

In most cases, it's enough to create an output item directly using
the `outputs` object:

```python
workitems.outputs.create(
    payload={"key": "value"},
    files=["path/to/file.txt"],
)
```

Internally, Control Room keeps a relationship between the parent and child
work items. The above example always uses the currently reserved item as the
parent, but it's also possible to create an output explicitly from
the input item:

```python
with workitems.inputs.reserve() as item:
    out = item.create_output()
    out.payload = {"key": "value"}
    out.save()
```

In some cases, it's also useful to create an output item and then modify it
before saving:

```python
item = workitems.outputs.create(save=False)

for index, path in enumerate(directory.glob("*.pdf")):
    item.add_file(path, name=f"document-{index}")

item.save()
```
