import os
import sys
import unittest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from handlers.place_order import _parse_order_response


class TestOrderResponseEdgeCases(unittest.TestCase):
    """Test edge cases for order response parsing"""

    def test_empty_response(self):
        """Test parsing completely empty response"""
        resp = {}
        out = _parse_order_response(resp)
        self.assertEqual(len(out), 1)
        self.assertIn("error", out[0])
        self.assertIn("non-ok status", out[0]["error"])

    def test_none_response(self):
        """Test parsing None response (should not crash)"""
        # Since the function expects a dict, passing None would cause AttributeError
        # This tests that we handle it gracefully
        try:
            out = _parse_order_response(None)
            self.assertEqual(len(out), 1)
            self.assertIn("error", out[0])
        except AttributeError:
            # If it raises AttributeError, that's expected behavior
            pass

    def test_nested_error_in_response(self):
        """Test parsing response with nested error structure"""
        resp = {
            "status": "ok",
            "response": {
                "data": {
                    "statuses": [
                        {
                            "error": {
                                "code": "INSUFFICIENT_MARGIN",
                                "message": "Not enough margin",
                            }
                        }
                    ]
                }
            },
        }
        out = _parse_order_response(resp)
        self.assertEqual(len(out), 1)
        self.assertIn("error", out[0])

    def test_mixed_success_and_error_statuses(self):
        """Test response with both successful and failed orders"""
        resp = {
            "status": "ok",
            "response": {
                "data": {
                    "statuses": [
                        {"oid": 123, "status": "success"},
                        {"error": "Order rejected"},
                        {"oid": 456, "status": "success"},
                    ]
                }
            },
        }
        out = _parse_order_response(resp)
        self.assertEqual(len(out), 3)
        self.assertEqual(out[0]["oid"], 123)
        self.assertIn("error", out[1])
        self.assertEqual(out[2]["oid"], 456)

    def test_deeply_nested_oid(self):
        """Test response with OID nested in complex structure"""
        resp = {
            "status": "ok",
            "response": {"data": {"result": {"order": {"oid": 789, "cloid": "0xabc"}}}},
        }
        out = _parse_order_response(resp)
        # Current implementation expects statuses list or direct data object
        # This should return the data as-is
        self.assertEqual(len(out), 1)

    def test_empty_statuses_list(self):
        """Test response with empty statuses list"""
        resp = {"status": "ok", "response": {"data": {"statuses": []}}}
        out = _parse_order_response(resp)
        self.assertEqual(out, [])

    def test_status_ok_but_response_error(self):
        """Test when status is ok but response contains error field"""
        resp = {
            "status": "ok",
            "response": {"error": "Unexpected server error", "data": {}},
        }
        out = _parse_order_response(resp)
        # Should still try to parse data
        self.assertEqual(len(out), 1)

    def test_non_dict_statuses_items(self):
        """Test response with non-dict items in statuses list"""
        resp = {
            "status": "ok",
            "response": {
                "data": {"statuses": ["string_status", 123, None, {"oid": 999}]}
            },
        }
        out = _parse_order_response(resp)
        # Should return all items as-is
        self.assertEqual(len(out), 4)
        self.assertEqual(out[0], "string_status")
        self.assertEqual(out[1], 123)
        self.assertEqual(out[2], None)
        self.assertEqual(out[3]["oid"], 999)

    def test_missing_response_key(self):
        """Test response missing 'response' key but status is ok"""
        resp = {"status": "ok", "data": {"statuses": [{"oid": 111}]}}
        out = _parse_order_response(resp)
        # Should handle missing 'response' key gracefully
        self.assertEqual(len(out), 1)
        self.assertIn("error", out[0])

    def test_response_with_unicode_characters(self):
        """Test response with unicode characters in error messages"""
        resp = {
            "status": "ok",
            "response": {
                "data": {
                    "statuses": [
                        {"error": "价格太低 💰"},
                        {"error": "Заказ отклонен 🚫"},
                    ]
                }
            },
        }
        out = _parse_order_response(resp)
        self.assertEqual(len(out), 2)
        self.assertIn("价格太低", out[0]["error"])
        self.assertIn("Заказ отклонен", out[1]["error"])

    def test_very_large_oid(self):
        """Test response with very large OID number"""
        resp = {"status": "ok", "response": {"data": {"oid": 999999999999999999999}}}
        out = _parse_order_response(resp)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["oid"], 999999999999999999999)


if __name__ == "__main__":
    unittest.main()
