import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from handlers import place_order as po


class TestPlaceOrderValidations(unittest.TestCase):
    @patch("handlers.place_order.Console")
    def test_new_order_negative_price(self, MockConsole):
        # price <= 0 should print error and return before calling setup
        po.new_order_run(
            coin="BTC",
            is_buy=True,
            size=1.0,
            price=0.0,
            private_key=None,
            production=False,
            account_address=None,
            time_in_force="Gtc",
            client_order_id=None,
            post_only=False,
            reduce_only=False,
        )
        # Ensure an error was printed
        self.assertTrue(MockConsole.return_value.print.called)
        printed_arg = str(MockConsole.return_value.print.call_args[0][0])
        self.assertIn("Price must be positive", printed_arg)

    @patch("handlers.place_order.Console")
    def test_new_order_negative_size(self, MockConsole):
        po.new_order_run(
            coin="ETH",
            is_buy=False,
            size=0.0,
            price=1000.0,
            private_key=None,
            production=False,
            account_address=None,
            time_in_force="Gtc",
            client_order_id=None,
            post_only=False,
            reduce_only=False,
        )
        self.assertTrue(MockConsole.return_value.print.called)
        printed_arg = str(MockConsole.return_value.print.call_args[0][0])
        self.assertIn("Size must be positive", printed_arg)

    @patch("handlers.place_order.Console")
    def test_modify_requires_params(self, MockConsole):
        # Should print error and return early without calling setup
        po.modify_order_run(
            oid_or_cloid="123",
            coin=None,
            size=None,
            price=None,
            private_key=None,
            production=False,
            account_address=None,
            time_in_force=None,
            client_order_id=None,
            reduce_only=None,
        )
        self.assertTrue(MockConsole.return_value.print.called)
        printed_arg = str(MockConsole.return_value.print.call_args[0][0])
        self.assertIn("Must specify at least one parameter to modify", printed_arg)


if __name__ == "__main__":
    unittest.main()
