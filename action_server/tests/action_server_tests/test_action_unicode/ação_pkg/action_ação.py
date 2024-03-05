from robocorp.actions import action


@action
def unicode_ação_Σ(ação: str) -> str:
    assert isinstance(ação, str)
    return ação
