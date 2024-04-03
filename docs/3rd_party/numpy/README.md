# Numpy

Numpy is a Python library that offers a large collection of mathematical functions to operate on arrays and matrices.

## Usage

```python
import numpy as np

# Create a matrix
matrix_a = np.array([[1, 2], [5, 3], [4, 6]])

# Get the maximum value of each row
print(f"Maximum values: {matrix_a.max(axis=1)}")

# Matrix multiplication
matrix_b = np.array([[5, 6], [7, 8]])
result = np.dot(matrix_a, matrix_b)

print(f"Matrix multiplication result: {result}")
```


> AI/LLM's are quite good with `numpy`.  
> 👉 Try asking [ReMark](https://chat.robocorp.com)

###### Various [snippets](snippets)

- [Find duplicate records in array](snippets/find_duplicate_records.py)

## Links and references

- [PyPI](https://pypi.org/project/numpy/)
- [Documentation](https://numpy.org/doc/)
- [Api referance](https://numpy.org/doc/stable/reference/index.html#reference)
