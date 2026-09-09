import io
import unittest

from checkdigit.streaming import count_invalid, iter_fixed_width_records, iter_validate


class IterValidateTest(unittest.TestCase):
    def test_validates_each_line(self):
        lines = ["0-306-40615-2", "0-306-40615-3"]
        results = list(iter_validate(lines))
        self.assertEqual(
            results,
            [(1, "0-306-40615-2", True), (2, "0-306-40615-3", False)],
        )

    def test_skips_blank_lines_without_renumbering(self):
        lines = ["0-306-40615-2", "", "   ", "036000291452"]
        results = list(iter_validate(lines))
        self.assertEqual(
            results,
            [(1, "0-306-40615-2", True), (4, "036000291452", True)],
        )

    def test_strips_line_endings(self):
        lines = ["0-306-40615-2\n", "036000291452\r\n"]
        results = list(iter_validate(lines))
        self.assertEqual(results[0][1], "0-306-40615-2")
        self.assertEqual(results[1][1], "036000291452")

    def test_custom_validator(self):
        lines = ["anything", "x"]
        results = list(iter_validate(lines, validator=lambda code: code == "x"))
        self.assertEqual(results, [(1, "anything", False), (2, "x", True)])

    def test_consumes_a_real_file_object(self):
        stream = io.StringIO("0-306-40615-2\n036000291452\n")
        results = list(iter_validate(stream))
        self.assertEqual(len(results), 2)
        self.assertTrue(all(ok for _, _, ok in results))


class IterFixedWidthRecordsTest(unittest.TestCase):
    def test_splits_evenly_sized_stream(self):
        stream = io.StringIO("036000291452" "978030640615")
        records = list(iter_fixed_width_records(stream, width=12, chunk_size=5))
        self.assertEqual(records, ["036000291452", "978030640615"])

    def test_small_chunk_size_still_reassembles_records(self):
        stream = io.StringIO("0306406152")
        records = list(iter_fixed_width_records(stream, width=10, chunk_size=3))
        self.assertEqual(records, ["0306406152"])

    def test_trailing_newline_is_not_leftover(self):
        stream = io.StringIO("036000291452\n")
        records = list(iter_fixed_width_records(stream, width=12))
        self.assertEqual(records, ["036000291452"])

    def test_uneven_length_raises(self):
        stream = io.StringIO("03600029145")
        with self.assertRaises(ValueError):
            list(iter_fixed_width_records(stream, width=12))

    def test_rejects_non_positive_width(self):
        with self.assertRaises(ValueError):
            list(iter_fixed_width_records(io.StringIO(""), width=0))

    def test_empty_stream_yields_nothing(self):
        records = list(iter_fixed_width_records(io.StringIO(""), width=10))
        self.assertEqual(records, [])


class CountInvalidTest(unittest.TestCase):
    def test_counts_only_invalid_codes(self):
        lines = ["0-306-40615-2", "0-306-40615-3", "036000291452", "036000291453"]
        self.assertEqual(count_invalid(lines), 2)

    def test_zero_when_all_valid(self):
        lines = ["0-306-40615-2", "036000291452"]
        self.assertEqual(count_invalid(lines), 0)

    def test_ignores_blank_lines(self):
        lines = ["", "0-306-40615-2", ""]
        self.assertEqual(count_invalid(lines), 0)


if __name__ == "__main__":
    unittest.main()
