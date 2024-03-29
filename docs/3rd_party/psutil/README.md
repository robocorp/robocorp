# Psutil

Psutil is a Python library for accessing system and process information, offering functionalities for monitoring CPU, memory, disk, and network usage.

## Usage

```python
import psutil

# List all processes running on the local machine
for proc in psutil.process_iter(['pid', 'name', 'username']):
    print(proc.info)
```

> AI/LLM's are quite good with `psutil`.  
> 👉 Try asking [ReMark](https://chat.robocorp.com)

###### Various [snippets](snippets)

- [Monitor CPU threshold](snippets/monitor_cpu_threshold.py)

## Links and references

- [PyPI](https://pypi.org/project/psutil/)
- [Documentation](https://psutil.readthedocs.io/en/latest/)
