import numpy as np


def find_duplicate_records(arr: np.ndarray) -> np.ndarray:
    """Returns duplicate records from a numpy array
    Example:
        >>> arr = np.array([1, 2, 3, 2, 4, 5, 6, 3, 7, 8, 1, 9, 2, 3])
    """
    unique_elements, counts = np.unique(arr, return_counts=True)

    return unique_elements[counts > 1]
