import typing


def safe_write_to_stream(stream: typing.IO, contents: str) -> None:
    """
    Writes the given contents to the stream making sure that no `UnicodeEncodeError`
    happens.
    """
    try:
        stream.write(contents)
        return
    except UnicodeEncodeError:
        pass  # keep on going...

    # UnicodeEncodeError error happened. Most likely the contents do not match
    # the encoding needed by the stream.
    buffer = getattr(stream, "buffer", None)
    encoding = getattr(stream, "encoding", None)
    if not encoding:
        encoding = "utf-8"

    if buffer is not None:
        # If possible write to buffer which uses binary interface
        # (and shouldn't fail regardless of the bytes).
        bytes_to_write = contents.encode(encoding, errors="replace")
        buffer.write(bytes_to_write)
        return

    # No buffer available, let's try to make sure that we have the
    # proper contents for the given encoding.
    replaced = contents.encode(encoding, errors="replace").decode(encoding)
    try:
        stream.write(replaced)
        return
    except UnicodeEncodeError:
        pass  # keep on going

    # Last attempt: write as ascii.
    replaced = contents.encode("ascii", errors="replace").decode("ascii")
    stream.write(replaced)
