import os
import sys
import unittest

# Ensure 'src' is on sys.path for direct test runs
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from handlers.setup import parse_cloid


class TestParseCloid(unittest.TestCase):
    def test_valid_decimal(self):
        self.assertEqual(str(parse_cloid("123456")).startswith("0x"), True)
        self.assertEqual(len(str(parse_cloid("123456"))), 34)

    def test_valid_hex_with_prefix(self):
        val = parse_cloid("0x1e240")
        self.assertTrue(str(val).startswith("0x"))
        self.assertEqual(len(str(val)), 34)

    def test_zero_values(self):
        self.assertEqual(str(parse_cloid("0")), "0x" + ("0" * 32))
        self.assertEqual(str(parse_cloid("0x0")), "0x" + ("0" * 32))

    def test_max_16_byte(self):
        max_hex = "0xffffffffffffffffffffffffffffffff"
        max_dec = str((1 << 128) - 1)
        self.assertEqual(len(str(parse_cloid(max_hex))), 34)
        self.assertEqual(len(str(parse_cloid(max_dec))), 34)

    def test_over_max_raises(self):
        over_hex = "0x100000000000000000000000000000000"
        over_dec = str(1 << 128)
        with self.assertRaises(ValueError):
            parse_cloid(over_hex)
        with self.assertRaises(ValueError):
            parse_cloid(over_dec)

    def test_invalid_formats(self):
        for s in ["", "invalid", "0xGHI", "123abc", "abc123", "1e240"]:
            with self.assertRaises(ValueError, msg=f"expected ValueError for {s}"):
                parse_cloid(s)


if __name__ == "__main__":
    unittest.main()
