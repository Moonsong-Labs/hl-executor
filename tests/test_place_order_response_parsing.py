import os
import sys
import unittest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from handlers import place_order as po


class TestParseOrderResponse(unittest.TestCase):
    def test_status_not_ok(self):
        resp = {"status": "error", "response": {"data": {}}}
        out = po._parse_order_response(resp)
        self.assertEqual(len(out), 1)
        self.assertIn("error", out[0])

    def test_statuses_list(self):
        resp = {
            "status": "ok",
            "response": {"data": {"statuses": [{"oid": 1}, {"status": "success"}]}},
        }
        out = po._parse_order_response(resp)
        self.assertEqual(out, [{"oid": 1}, {"status": "success"}])

    def test_single_data_object(self):
        resp = {"status": "ok", "response": {"data": {"oid": 42}}}
        out = po._parse_order_response(resp)
        self.assertEqual(out, [{"oid": 42}])

    def test_malformed(self):
        resp = {"status": "ok", "response": {}}
        out = po._parse_order_response(resp)
        self.assertEqual(len(out), 1)
        self.assertIn("error", out[0])


if __name__ == "__main__":
    unittest.main()
