import unittest

from checkdigit.checksum import (
    ean8_check_digit,
    ean8_is_valid,
    ean13_check_digit,
    ean13_is_valid,
    is_valid,
    isbn10_check_digit,
    isbn10_is_valid,
    isbn13_check_digit,
    isbn13_is_valid,
    issn_check_digit,
    issn_is_valid,
    upca_check_digit,
    upca_is_valid,
)


class Isbn10Test(unittest.TestCase):
    def test_check_digit_numeric(self):
        self.assertEqual(isbn10_check_digit("030640615"), "2")

    def test_check_digit_x(self):
        self.assertEqual(isbn10_check_digit("080442957"), "X")

    def test_check_digit_rejects_wrong_length(self):
        with self.assertRaises(ValueError):
            isbn10_check_digit("03064061")

    def test_check_digit_rejects_non_digits(self):
        with self.assertRaises(ValueError):
            isbn10_check_digit("03064061X")

    def test_is_valid_plain(self):
        self.assertTrue(isbn10_is_valid("0306406152"))

    def test_is_valid_with_separators(self):
        self.assertTrue(isbn10_is_valid("0-306-40615-2"))
        self.assertTrue(isbn10_is_valid("0 306 40615 2"))

    def test_is_valid_lowercase_x(self):
        self.assertTrue(isbn10_is_valid("080442957x"))
        self.assertTrue(isbn10_is_valid("080442957X"))

    def test_is_valid_wrong_check_digit(self):
        self.assertFalse(isbn10_is_valid("0306406153"))

    def test_is_valid_wrong_length(self):
        self.assertFalse(isbn10_is_valid("030640615"))
        self.assertFalse(isbn10_is_valid("03064061522"))

    def test_is_valid_non_digit_prefix(self):
        self.assertFalse(isbn10_is_valid("030640615X"))

    def test_is_valid_bad_trailing_character(self):
        self.assertFalse(isbn10_is_valid("030640615Y"))


class Ean13Isbn13Test(unittest.TestCase):
    def test_check_digit(self):
        self.assertEqual(ean13_check_digit("978030640615"), "7")

    def test_isbn13_check_digit_is_ean13_check_digit(self):
        self.assertIs(isbn13_check_digit, ean13_check_digit)

    def test_check_digit_rejects_wrong_length(self):
        with self.assertRaises(ValueError):
            ean13_check_digit("97803064061")

    def test_check_digit_rejects_non_digits(self):
        with self.assertRaises(ValueError):
            ean13_check_digit("97803064061X")

    def test_is_valid_plain(self):
        self.assertTrue(ean13_is_valid("9780306406157"))

    def test_is_valid_with_separators(self):
        self.assertTrue(ean13_is_valid("978-0-306-40615-7"))

    def test_isbn13_is_valid_is_ean13_is_valid(self):
        self.assertIs(isbn13_is_valid, ean13_is_valid)

    def test_is_valid_wrong_check_digit(self):
        self.assertFalse(ean13_is_valid("9780306406158"))

    def test_is_valid_wrong_length(self):
        self.assertFalse(ean13_is_valid("978030640615"))


class UpcATest(unittest.TestCase):
    def test_check_digit(self):
        self.assertEqual(upca_check_digit("03600029145"), "2")

    def test_check_digit_rejects_wrong_length(self):
        with self.assertRaises(ValueError):
            upca_check_digit("0360002914")

    def test_is_valid_plain(self):
        self.assertTrue(upca_is_valid("036000291452"))

    def test_is_valid_wrong_check_digit(self):
        self.assertFalse(upca_is_valid("036000291453"))

    def test_is_valid_wrong_length(self):
        self.assertFalse(upca_is_valid("03600029145"))


class Ean8Test(unittest.TestCase):
    def test_check_digit(self):
        self.assertEqual(ean8_check_digit("4017072"), "5")

    def test_check_digit_rejects_wrong_length(self):
        with self.assertRaises(ValueError):
            ean8_check_digit("401707")

    def test_check_digit_rejects_non_digits(self):
        with self.assertRaises(ValueError):
            ean8_check_digit("401707X")

    def test_is_valid_plain(self):
        self.assertTrue(ean8_is_valid("40170725"))
        self.assertTrue(ean8_is_valid("96385074"))

    def test_is_valid_with_separators(self):
        self.assertTrue(ean8_is_valid("4017-0725"))

    def test_is_valid_wrong_check_digit(self):
        self.assertFalse(ean8_is_valid("40170726"))

    def test_is_valid_wrong_length(self):
        self.assertFalse(ean8_is_valid("4017072"))
        self.assertFalse(ean8_is_valid("401707255"))


class IssnTest(unittest.TestCase):
    def test_check_digit_numeric(self):
        self.assertEqual(issn_check_digit("0378595"), "5")

    def test_check_digit_x(self):
        self.assertEqual(issn_check_digit("1050124"), "X")

    def test_check_digit_rejects_wrong_length(self):
        with self.assertRaises(ValueError):
            issn_check_digit("037859")

    def test_check_digit_rejects_non_digits(self):
        with self.assertRaises(ValueError):
            issn_check_digit("037859X")

    def test_is_valid_plain(self):
        self.assertTrue(issn_is_valid("03785955"))

    def test_is_valid_with_separator(self):
        self.assertTrue(issn_is_valid("0378-5955"))

    def test_is_valid_x_check_digit(self):
        self.assertTrue(issn_is_valid("1050-124X"))
        self.assertTrue(issn_is_valid("1050-124x"))

    def test_is_valid_wrong_check_digit(self):
        self.assertFalse(issn_is_valid("03785956"))

    def test_is_valid_wrong_length(self):
        self.assertFalse(issn_is_valid("0378595"))
        self.assertFalse(issn_is_valid("037859555"))

    def test_is_valid_bad_trailing_character(self):
        self.assertFalse(issn_is_valid("0378595Y"))


class DispatchIsValidTest(unittest.TestCase):
    def test_dispatches_isbn10(self):
        self.assertTrue(is_valid("0-306-40615-2"))

    def test_dispatches_upca(self):
        self.assertTrue(is_valid("036000291452"))

    def test_dispatches_ean13(self):
        self.assertTrue(is_valid("978-0-306-40615-7"))

    def test_unknown_length_is_false(self):
        self.assertFalse(is_valid("123"))

    def test_eight_digits_not_dispatched(self):
        # EAN-8 and ISSN are both 8 digits and use different arithmetic,
        # so is_valid deliberately doesn't guess between them.
        self.assertFalse(is_valid("40170725"))

    def test_empty_string_is_false(self):
        self.assertFalse(is_valid(""))


if __name__ == "__main__":
    unittest.main()
