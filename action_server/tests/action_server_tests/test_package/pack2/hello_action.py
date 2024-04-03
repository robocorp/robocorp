def nothing_here(name: str, title="Mr.") -> str:
    """
    Provides a greeting for a person.

    Args:
        name: The name of the person to greet.
        title: The title for the persor (Mr., Mrs., ...).

    Returns:
        The greeting for the person.
    """
    return f"Hello {title} {name}."
