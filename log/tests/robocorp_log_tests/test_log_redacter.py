def test_log_redacter() -> None:
    from robocorp.log._log_redacter import LogRedacter

    log_redacter = LogRedacter()
    config = log_redacter.config

    config.dont_hide_strings.add("Some")
    log_redacter.hide_from_output("Some")

    assert log_redacter.redact("Some") == "Some"

    log_redacter.hide_from_output("Something")
    assert log_redacter.redact("Something") == "<redacted>"

    config.dont_hide_strings.add("Something")
    assert log_redacter.redact("Something") == "Something"

    config.dont_hide_strings.discard("Something")
    config.dont_hide_strings.add("Something")
    config.dont_hide_strings.discard("Something")
    config.dont_hide_strings.add("Something")
    config.dont_hide_strings.discard("Something")
    assert log_redacter.redact("Something") == "<redacted>"

    config.dont_hide_strings_smaller_or_equal_to = 4
    config.hide_strings.add("mm")
    assert log_redacter.redact("mm") == "mm"

    config.dont_hide_strings_smaller_or_equal_to = 2
    assert log_redacter.redact("mm") == "mm"

    config.dont_hide_strings_smaller_or_equal_to = 1
    assert log_redacter.redact("mm") == "<redacted>"
