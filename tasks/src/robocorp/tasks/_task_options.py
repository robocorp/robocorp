from dataclasses import dataclass


@dataclass
class TaskOptions:
    is_consequential: bool = False
