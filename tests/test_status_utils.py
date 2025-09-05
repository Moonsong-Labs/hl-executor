import os
import sys
import unittest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from handlers import status as st


class TestStatusUtils(unittest.TestCase):
    def test_colorize_number_positive_negative_zero(self):
        self.assertEqual(st._colorize_number(5).plain, "5")
        self.assertIn("green", st._colorize_number(5).style or "")

        self.assertEqual(st._colorize_number(-3).plain, "-3")
        self.assertIn("red", st._colorize_number(-3).style or "")

        self.assertEqual(st._colorize_number(0).plain, "0")
        self.assertEqual(st._colorize_number(0).style, "")

    def test_colorize_number_percent(self):
        txt = st._colorize_number(0.1234, "%")
        self.assertEqual(txt.plain, "12.34%")

    def test_normalize_positions(self):
        raw = [
            {"position": {"coin": "BTC", "sz": 1}},
            {"coin": "ETH", "sz": 2},
            "bad",
            {"position": "also bad"},
        ]
        out = st._normalize_positions(raw)
        self.assertEqual(out, [{"coin": "BTC", "sz": 1}, {"coin": "ETH", "sz": 2}])


if __name__ == "__main__":
    unittest.main()
