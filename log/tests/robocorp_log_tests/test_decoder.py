def test_decoder_location():
    from io import StringIO

    from robocorp.log._decoder import iter_decoded_log_format

    s = StringIO(
        """
M a:"my-name"
M b:"my-libname"
M c:"my-source"
M d:"my-doc"
M e:"METHOD"
P x:a|b|c|d|123
SE x|e|0.012
"""
    )
    msgs = list(iter_decoded_log_format(s))
    assert msgs == [
        {
            "message_type": "SE",
            "name": "my-name",
            "libname": "my-libname",
            "source": "my-source",
            "doc": "my-doc",
            "lineno": 123,
            "type": "METHOD",
            "time_delta_in_seconds": 0.012,
        }
    ]


def test_decoder_info():
    from io import StringIO

    from robocorp.log._decoder import iter_decoded_log_format

    s = StringIO(
        """
I "my-name"
"""
    )
    msgs = list(iter_decoded_log_format(s))
    assert msgs == [{"message_type": "I", "info": "my-name"}]
