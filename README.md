# checkdigit

ISBN-10, ISBN-13, EAN-13, and UPC-A all end in a check digit computed
from the digits before it. That's how a scanner or an ISBN field
catches a mistyped or misscanned number before it ever hits a
database: recompute the check digit from the rest and compare it to
the one printed on the code. This library is that arithmetic, plus
some helpers for running it over large inputs.

No dependencies, standard library only.

## Install

Not published anywhere yet. For now, clone it and either install it
editable or point `PYTHONPATH` at `src/`:

```
pip install -e .
```

## Usage

```python
from checkdigit import isbn10_is_valid, isbn13_is_valid, is_valid

isbn10_is_valid("0-306-40615-2")   # True
isbn13_is_valid("978-0-306-40615-7")  # True
is_valid("036000291452")           # True (UPC-A, type detected by length)
```

Computing a check digit instead of just checking one:

```python
from checkdigit import isbn13_check_digit

isbn13_check_digit("978030640615")  # "7"
```

## Validating a large file

The point of `streaming.py` is that none of these functions need the
whole input in memory at once. `iter_validate` takes anything
iterable line by line - an open file is the common case - and yields
results as it goes, so a file with ten million codes is processed one
line at a time:

```python
from checkdigit import iter_validate

with open("codes.txt") as f:
    for line_number, code, ok in iter_validate(f):
        if not ok:
            print(f"line {line_number}: bad check digit: {code}")
```

Some barcode feeds have no delimiters at all, just a continuous run
of digits. `iter_fixed_width_records` handles that case by reading
the stream in fixed-size chunks and only ever keeping a small rolling
buffer around, not the full stream:

```python
from checkdigit import iter_fixed_width_records, is_valid

with open("raw_feed.txt") as f:
    for code in iter_fixed_width_records(f, width=13):
        if not is_valid(code):
            print(f"bad code: {code}")
```

## Supported formats

- ISBN-10 (`isbn10_check_digit`, `isbn10_is_valid`)
- ISBN-13 / EAN-13 (`isbn13_check_digit`, `isbn13_is_valid`, and the
  `ean13_*` names, which are the same functions)
- UPC-A (`upca_check_digit`, `upca_is_valid`)
- `is_valid(code)` picks the format by cleaned length (10/12/13
  digits) when the caller doesn't know or care which it is

## License

MIT, see LICENSE.
