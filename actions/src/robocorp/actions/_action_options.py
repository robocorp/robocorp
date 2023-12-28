from dataclasses import dataclass


@dataclass
class ActionOptions:
    is_consequential: bool = False
