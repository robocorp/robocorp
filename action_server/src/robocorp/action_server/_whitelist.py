import fnmatch


def _normalize_name(name):
    """
    Normalizes action names to handle hyphens and underscores interchangeably.
    """
    return name.replace("-", "_").strip()


def accept_action(pattern: str, package_name: str, action_name: str) -> bool:
    """
    Determines whether an action should be accepted based on the whitelist pattern.

    Args:
      pattern: The whitelist pattern to match against.
      package_name: The name of the package containing the action (can be empty).
      action_name: The name of the action.

    Returns:
      True if the action matches the whitelist pattern, False otherwise.
    """
    package_name = _normalize_name(package_name)
    action_name = _normalize_name(action_name)
    pattern = _normalize_name(pattern)

    for single_pattern in pattern.split(","):
        # Check if the pattern includes a package name separated by '/'
        if "/" in single_pattern:
            package_pattern, action_pattern = single_pattern.split("/", 1)
        else:
            package_pattern = "*"
            action_pattern = single_pattern

        # Check if the package name matches the package pattern (if provided)
        if fnmatch.fnmatch(package_name, package_pattern):
            # Match the action name against the action pattern
            if fnmatch.fnmatch(action_name, action_pattern):
                return True

    return False


def accept_action_package(pattern: str, package_name: str) -> bool:
    """
    Determines whether an action package should be accepted based on the whitelist pattern.

    Args:
      pattern: The whitelist pattern to match against.
      package_name: The name of the package containing the action (can be empty).
      action_name: The name of the action.

    Returns:
      True if the action matches the whitelist pattern, False otherwise.
    """
    package_name = _normalize_name(package_name)
    pattern = _normalize_name(pattern)

    for single_pattern in pattern.split(","):
        # Check if the pattern includes a package name separated by '/'
        if "/" in single_pattern:
            package_pattern, _action_pattern = single_pattern.split("/", 1)
        else:
            package_pattern = "*"

        # Check if the package name matches the package pattern (if provided)
        if fnmatch.fnmatch(package_name, package_pattern):
            return True

    return False
