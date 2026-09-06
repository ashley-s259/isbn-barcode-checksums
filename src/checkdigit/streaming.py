"""Validate large batches of codes without holding them all in memory.

A file of a few million ISBNs, one per line, is a few hundred MB at
most - not huge, but there's no reason to read it in one go when the
caller only wants a pass/fail per line. Everything below consumes its
input lazily and yields results as it goes.
"""

from typing import Callable, Iterable, Iterator, TextIO, Tuple

from .checksum import is_valid as _default_validator

ValidationResult = Tuple[int, str, bool]


def iter_validate(
    lines: Iterable[str],
    validator: Callable[[str], bool] = _default_validator,
) -> Iterator[ValidationResult]:
    """Validate one code per line as it is read.

    `lines` only has to support iteration, so passing an open file
    object means each line is read, checked, and discarded before the
    next one is pulled in - the file's size never shows up in memory.
    Blank lines are skipped rather than reported as invalid.
    """
    for line_number, raw in enumerate(lines, start=1):
        code = raw.strip()
        if not code:
            continue
        yield line_number, code, validator(code)


def iter_fixed_width_records(
    stream: TextIO, width: int, chunk_size: int = 8192
) -> Iterator[str]:
    """Split an undelimited stream of digits into fixed-width records.

    Some barcode feeds are a continuous run of digits with no
    separators between codes. Reading the whole thing just to slice
    it up would defeat the point, so this keeps a small rolling
    buffer - at most `chunk_size + width - 1` characters - and yields
    a record as soon as enough characters have arrived for one.
    """
    if width <= 0:
        raise ValueError("width must be positive")
    buffer = ""
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        buffer += chunk
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
