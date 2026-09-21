"""Validate large batches of codes without holding them all in memory.

A file of a few million ISBNs, one per line, is a few hundred MB at
most - not huge, but there's no reason to read it in one go when the
caller only wants a pass/fail per line. Everything below consumes its
input lazily and yields results as it goes.
"""

from typing import BinaryIO, Callable, Iterable, Iterator, TextIO, Tuple, Union

from .checksum import is_valid as _default_validator

ValidationResult = Tuple[int, str, bool]


def _decode(raw: Union[str, bytes]) -> str:
    # Binary-mode files (e.g. opened "rb" because the caller doesn't
    # know the encoding up front, or is reading off a socket) yield
    # bytes lines/chunks instead of str. Codes are ASCII digits and
    # separators, so utf-8 is a safe, unsurprising default.
    return raw.decode("utf-8") if isinstance(raw, bytes) else raw


def iter_validate(
    lines: Iterable[Union[str, bytes]],
    validator: Callable[[str], bool] = _default_validator,
) -> Iterator[ValidationResult]:
    """Validate one code per line as it is read.

    `lines` only has to support iteration, so passing an open file
    object means each line is read, checked, and discarded before the
    next one is pulled in - the file's size never shows up in memory.
    Blank lines are skipped rather than reported as invalid. Works
    with both text-mode and binary-mode files.
    """
    for line_number, raw in enumerate(lines, start=1):
        code = _decode(raw).strip()
        if not code:
            continue
        yield line_number, code, validator(code)


def iter_fixed_width_records(
    stream: Union[TextIO, BinaryIO], width: int, chunk_size: int = 8192
) -> Iterator[str]:
    """Split an undelimited stream of digits into fixed-width records.

    Some barcode feeds are a continuous run of digits with no
    separators between codes. Reading the whole thing just to slice
    it up would defeat the point, so this keeps a small rolling
    buffer - at most `chunk_size + width - 1` characters - and yields
    a record as soon as enough characters have arrived for one.
    Accepts a binary-mode stream as well as a text-mode one.
    """
    if width <= 0:
        raise ValueError("width must be positive")
    buffer = ""
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        buffer += _decode(chunk)
        while len(buffer) >= width:
            yield buffer[:width]
            buffer = buffer[width:]
    remainder = buffer.strip()
    if remainder:
        raise ValueError(
            f"stream ended with {len(remainder)} leftover characters, "
            f"not a multiple of {width}"
        )


def count_invalid(
    lines: Iterable[str],
    validator: Callable[[str], bool] = _default_validator,
) -> int:
    """Count invalid codes in a stream, e.g. as a quick import sanity check."""
    return sum(1 for _, _, ok in iter_validate(lines, validator) if not ok)
