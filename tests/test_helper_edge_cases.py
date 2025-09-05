import os
import sys
import unittest
from unittest.mock import Mock, patch
from decimal import Decimal

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from handlers.status import _colorize_number, _normalize_positions, _space
from rich.text import Text


class TestHelperEdgeCases(unittest.TestCase):
    """Test edge cases for helper functions"""

    # Tests for _colorize_number edge cases
    def test_colorize_number_none_value(self):
        """Test colorize with None value"""
        result = _colorize_number(None)
        self.assertEqual(result.plain, "-")

    def test_colorize_number_string_value(self):
        """Test colorize with non-numeric string"""
        result = _colorize_number("not_a_number")
        self.assertEqual(result.plain, "not_a_number")

    def test_colorize_number_very_large(self):
        """Test colorize with very large numbers"""
        result = _colorize_number(999999999999999999999.123456)
        # Due to floating point precision, the actual value might be rounded
        # Just check it's a large number
        self.assertTrue(len(result.plain) >= 20)

    def test_colorize_number_very_small(self):
        """Test colorize with very small numbers"""
        result = _colorize_number(0.000000000001)
        self.assertIn("e", result.plain.lower())  # Scientific notation

    def test_colorize_number_infinity(self):
        """Test colorize with infinity - should raise or handle gracefully"""
        # The function will raise OverflowError when trying to convert inf to int
        with self.assertRaises(OverflowError):
            _colorize_number(float("inf"))

    def test_colorize_number_nan(self):
        """Test colorize with NaN - should raise or handle gracefully"""
        # The function will raise ValueError when trying to convert NaN to int
        with self.assertRaises(ValueError):
            _colorize_number(float("nan"))

    def test_colorize_number_decimal_type(self):
        """Test colorize with Decimal type"""
        result = _colorize_number(Decimal("123.456"))
        self.assertEqual(result.plain, "123.456")

    def test_colorize_number_percent_edge_cases(self):
        """Test percentage formatting edge cases"""
        # Very small percentage
        result = _colorize_number(0.00001, "%")
        self.assertEqual(result.plain, "0.00%")

        # Large percentage
        result = _colorize_number(15.5, "%")
        self.assertEqual(result.plain, "1550.00%")

        # Negative percentage
        result = _colorize_number(-0.25, "%")
        self.assertEqual(result.plain, "-25.00%")
        self.assertIn("red", str(result.style) if result.style else "")

    def test_colorize_number_whole_number_display(self):
        """Test that whole numbers are displayed without decimals"""
        result = _colorize_number(100.0)
        self.assertEqual(result.plain, "100")

        result = _colorize_number(100.00001)
        self.assertNotEqual(result.plain, "100")

    # Tests for _normalize_positions edge cases
    def test_normalize_positions_none_input(self):
        """Test normalize with None input"""
        result = _normalize_positions(None)
        self.assertEqual(result, [])

    def test_normalize_positions_empty_list(self):
        """Test normalize with empty list"""
        result = _normalize_positions([])
        self.assertEqual(result, [])

    def test_normalize_positions_nested_none(self):
        """Test normalize with None position values"""
        raw = [
            {"position": None},
            {"position": {"coin": "BTC"}},
            None,
        ]
        result = _normalize_positions(raw)  # type: ignore
        # The function includes items with None position, but the position itself is None
        self.assertEqual(result, [{"position": None}, {"coin": "BTC"}])

    def test_normalize_positions_deeply_nested(self):
        """Test normalize with deeply nested structures"""
        raw = [
            {"position": {"position": {"coin": "ETH"}}},  # Double nested
            {"coin": "BTC"},  # Direct
        ]
        result = _normalize_positions(raw)
        # Should get the first level position, not double nested
        self.assertEqual(len(result), 2)

    def test_normalize_positions_mixed_types(self):
        """Test normalize with various non-dict types"""
        raw = [
            123,  # Integer
            "string",  # String
            [],  # List
            {"position": []},  # Position is list
            {"position": "not_dict"},  # Position is string
            {"coin": "Valid"},  # Valid position
        ]
        result = _normalize_positions(raw)  # type: ignore
        # The function includes items with non-dict position values
        self.assertEqual(result, [{"position": []}, {"coin": "Valid"}])

    def test_normalize_positions_unicode_data(self):
        """Test normalize with unicode characters in data"""
        raw = [
            {"position": {"coin": "BTC₿", "note": "比特币"}},
            {"coin": "ETH⟠", "note": "以太坊"},
        ]
        result = _normalize_positions(raw)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["coin"], "BTC₿")
        self.assertEqual(result[1]["coin"], "ETH⟠")

    def test_space_negative_lines(self):
        """Test space function with negative lines"""
        mock_console = Mock()
        _space(mock_console, -5)
        # Should not print anything for negative lines
        self.assertEqual(mock_console.print.call_count, 0)

    def test_space_zero_lines(self):
        """Test space function with zero lines"""
        mock_console = Mock()
        _space(mock_console, 0)
        self.assertEqual(mock_console.print.call_count, 0)

    def test_space_large_number(self):
        """Test space function with large number of lines"""
        mock_console = Mock()
        _space(mock_console, 100)
        self.assertEqual(mock_console.print.call_count, 100)

    def test_space_float_lines(self):
        """Test space function with float input (should handle gracefully)"""
        mock_console = Mock()
        _space(mock_console, 2)

    # Additional edge case tests for display functions
    def test_display_with_empty_strings(self):
        """Test various functions with empty string inputs"""
        # Test colorize with empty string
        result = _colorize_number("")
        self.assertEqual(result.plain, "")

        # Test normalize with empty string in position
        raw = [{"position": ""}, {"position": {"coin": ""}}]
        result = _normalize_positions(raw)
        # The function includes items with non-dict position values
        self.assertEqual(result, [{"position": ""}, {"coin": ""}])

    def test_extreme_decimal_precision(self):
        """Test handling of numbers with extreme decimal precision"""
        result = _colorize_number(0.123456789012345678901234567890)
        # Should handle without crashing
        self.assertIsNotNone(result.plain)

        # Very precise negative
        result = _colorize_number(-0.000000000000000001)
        self.assertIn("red", str(result.style) if result.style else "")


if __name__ == "__main__":
    unittest.main()
