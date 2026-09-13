"""Check-digit math for ISBN-10, ISBN-13/EAN-13, EAN-8, ISSN, and UPC-A.

Everything here takes and returns plain strings. No exceptions get
raised for "this looks invalid" - that's what the is_valid functions
are for. ValueError is only for calls that are malformed by contract
(wrong length prefix passed to a check-digit calculator).
"""


def _clean(code: str) -> str:
    return code.replace("-", "").replace(" ", "")


def _alternating_sum(digits: str, first_weight: int) -> int:
    # ISBN-13/EAN-13 and UPC-A both use weights that alternate between
    # 1 and 3; they differ only in which one comes first.
    total = 0
    weight = first_weight
    for ch in digits:
        total += int(ch) * weight
        weight = 4 - weight
    return total


def isbn10_check_digit(prefix: str) -> str:
    if len(prefix) != 9 or not prefix.isdigit():
        raise ValueError("ISBN-10 prefix must be exactly 9 digits")
    total = sum((10 - i) * int(d) for i, d in enumerate(prefix))
    remainder = (11 - total % 11) % 11
    return "X" if remainder == 10 else str(remainder)


def isbn10_is_valid(code: str) -> bool:
    cleaned = _clean(code)
    if len(cleaned) != 10 or not cleaned[:9].isdigit():
        return False
    last = cleaned[9]
    if last not in "0123456789Xx":
        return False
    total = sum((10 - i) * int(d) for i, d in enumerate(cleaned[:9]))
    total += 10 if last in "Xx" else int(last)
    return total % 11 == 0


def ean13_check_digit(prefix: str) -> str:
    if len(prefix) != 12 or not prefix.isdigit():
        raise ValueError("EAN-13/ISBN-13 prefix must be exactly 12 digits")
    total = _alternating_sum(prefix, first_weight=1)
    return str((10 - total % 10) % 10)


def ean13_is_valid(code: str) -> bool:
    cleaned = _clean(code)
    if len(cleaned) != 13 or not cleaned.isdigit():
        return False
    return _alternating_sum(cleaned, first_weight=1) % 10 == 0


# ISBN-13 is EAN-13 with a Bookland (978/979) prefix; the arithmetic
# is identical, so these are just names for the same functions.
isbn13_check_digit = ean13_check_digit
isbn13_is_valid = ean13_is_valid


def ean8_check_digit(prefix: str) -> str:
    if len(prefix) != 7 or not prefix.isdigit():
        raise ValueError("EAN-8 prefix must be exactly 7 digits")
    total = _alternating_sum(prefix, first_weight=3)
    return str((10 - total % 10) % 10)


def ean8_is_valid(code: str) -> bool:
    cleaned = _clean(code)
    if len(cleaned) != 8 or not cleaned.isdigit():
        return False
    return _alternating_sum(cleaned, first_weight=3) % 10 == 0


def issn_check_digit(prefix: str) -> str:
    if len(prefix) != 7 or not prefix.isdigit():
        raise ValueError("ISSN prefix must be exactly 7 digits")
    total = sum((8 - i) * int(d) for i, d in enumerate(prefix))
    remainder = (11 - total % 11) % 11
    return "X" if remainder == 10 else str(remainder)


def issn_is_valid(code: str) -> bool:
    cleaned = _clean(code)
    if len(cleaned) != 8 or not cleaned[:7].isdigit():
        return False
    last = cleaned[7]
    if last not in "0123456789Xx":
        return False
    total = sum((8 - i) * int(d) for i, d in enumerate(cleaned[:7]))
    total += 10 if last in "Xx" else int(last)
    return total % 11 == 0


def upca_check_digit(prefix: str) -> str:
    if len(prefix) != 11 or not prefix.isdigit():
        raise ValueError("UPC-A prefix must be exactly 11 digits")
    total = _alternating_sum(prefix, first_weight=3)
    return str((10 - total % 10) % 10)


def upca_is_valid(code: str) -> bool:
    cleaned = _clean(code)
    if len(cleaned) != 12 or not cleaned.isdigit():
        return False
    return _alternating_sum(cleaned, first_weight=3) % 10 == 0


def is_valid(code: str) -> bool:
    """Validate a code whose type isn't known ahead of time, by length.

    EAN-8 and ISSN are both 8 digits and use different arithmetic, so
    there's no length to dispatch on for them here; call
    ean8_is_valid or issn_is_valid directly.
    """
    cleaned = _clean(code)
    if len(cleaned) == 10:
        return isbn10_is_valid(cleaned)
    if len(cleaned) == 12:
        return upca_is_valid(cleaned)
    if len(cleaned) == 13:
        return ean13_is_valid(cleaned)
    return False
