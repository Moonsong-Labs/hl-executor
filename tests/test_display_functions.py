import os
import sys
import unittest
from unittest.mock import Mock, patch, call
from datetime import datetime

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from handlers.place_order import (
    _display_order_status,
    _display_order_result,
    _display_cancel_result,
)
from handlers.deposit import _render_balances, _render_summary
from handlers.status import _render_positions, _render_open_orders, _space
from decimal import Decimal
from rich.text import Text


class TestDisplayFunctions(unittest.TestCase):
    """Test display and rendering functions"""

    def setUp(self):
        """Set up mock console for each test"""
        self.mock_console = Mock()

    # Tests for place_order display functions
    def test_display_order_status_basic(self):
        """Test basic order status display"""
        order_info = {
            "oid": 12345,
            "coin": "BTC",
            "side": "B",
            "sz": "0.5",
            "limitPx": "45000",
            "orderType": "limit",
            "tif": "Gtc",
            "reduceOnly": False,
        }

        with patch("handlers.place_order.click.echo"):
            _display_order_status(self.mock_console, order_info)

        # Verify console.print was called
        self.assertTrue(self.mock_console.print.called)
        # Verify a table was created and printed
        printed_obj = self.mock_console.print.call_args[0][0]
        self.assertIsNotNone(printed_obj)

    def test_display_order_status_with_cloid_and_timestamp(self):
        """Test order status display with client order ID and timestamp"""
        order_info = {
            "oid": 12345,
            "coin": "ETH",
            "side": "A",
            "sz": "2.0",
            "limitPx": "3000",
            "orderType": "limit",
            "tif": "Ioc",
            "reduceOnly": True,
            "cloid": "0x123456",
            "timestamp": 1609459200000,  # 2021-01-01 00:00:00 UTC
        }

        with patch("handlers.place_order.click.echo"):
            _display_order_status(self.mock_console, order_info)

        self.assertTrue(self.mock_console.print.called)

    def test_display_order_result_empty(self):
        """Test order result display with empty data"""
        _display_order_result(self.mock_console, [])
        # Should print "No results returned"
        self.assertTrue(self.mock_console.print.called)
        printed_text = str(self.mock_console.print.call_args[0][0])
        self.assertIn("No results", printed_text)

    def test_display_order_result_with_error(self):
        """Test order result display with error"""
        result_data = [{"error": "Insufficient margin"}]

        with patch("handlers.place_order.click.echo"):
            _display_order_result(self.mock_console, result_data)

        self.assertTrue(self.mock_console.print.called)

    def test_display_order_result_with_success(self):
        """Test order result display with successful order"""
        result_data = [{"oid": 54321, "status": "success"}]

        with patch("handlers.place_order.click.echo"):
            _display_order_result(self.mock_console, result_data)

        self.assertTrue(self.mock_console.print.called)

    def test_display_cancel_result_success(self):
        """Test cancel result display for successful cancellation"""
        result_data = ["success"]

        with patch("handlers.place_order.click.echo"):
            _display_cancel_result(self.mock_console, result_data, 12345)

        self.assertTrue(self.mock_console.print.called)

    def test_display_cancel_result_with_error(self):
        """Test cancel result display with error"""
        result_data = [{"error": "Order not found"}]

        with patch("handlers.place_order.click.echo"):
            _display_cancel_result(self.mock_console, result_data, 12345)

        self.assertTrue(self.mock_console.print.called)

    # Tests for deposit display functions
    def test_render_balances(self):
        """Test balance table rendering"""
        eth_balance = Decimal("1.234567")
        usdc_balance = Decimal("1000.123456")
        signer = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7"

        _render_balances(self.mock_console, eth_balance, usdc_balance, signer)

        # Verify console.print was called with a table
        self.assertTrue(self.mock_console.print.called)

    def test_render_summary_success(self):
        """Test deposit summary rendering for successful deposit"""
        requested = 100.0
        credited = 99.5
        final_balance = 199.5

        _render_summary(self.mock_console, requested, credited, final_balance)

        # Should print table with success status
        self.assertEqual(self.mock_console.print.call_count, 2)  # Newline + table

    def test_render_summary_partial(self):
        """Test deposit summary rendering for partial deposit"""
        requested = 100.0
        credited = 50.0
        final_balance = 150.0

        _render_summary(self.mock_console, requested, credited, final_balance)

        # Should print table with partial status
        self.assertEqual(self.mock_console.print.call_count, 2)

    # Tests for status display functions
    def test_render_positions_empty(self):
        """Test position rendering with no positions"""
        _render_positions(self.mock_console, [])

        # Should print "No open positions"
        self.assertTrue(self.mock_console.print.called)
        printed_text = str(self.mock_console.print.call_args[0][0])
        self.assertIn("No open positions", printed_text)

    def test_render_positions_with_data(self):
        """Test position rendering with position data"""
        positions = [
            {
                "coin": "BTC",
                "szi": "1.5",
                "leverage": {"value": 10},
                "entryPx": "45000",
                "positionValue": "67500",
                "unrealizedPnl": "500",
                "returnOnEquity": 0.05,
                "liquidationPx": "40000",
                "marginUsed": "6750",
            }
        ]

        _render_positions(self.mock_console, positions)

        # Verify table was created and printed
        self.assertTrue(self.mock_console.print.called)

    def test_render_open_orders_empty(self):
        """Test open orders rendering with no orders"""
        _render_open_orders(self.mock_console, [])

        # Should print "No open orders"
        self.assertTrue(self.mock_console.print.called)
        printed_text = str(self.mock_console.print.call_args[0][0])
        self.assertIn("No open orders", printed_text)

    def test_render_open_orders_with_data(self):
        """Test open orders rendering with order data"""
        orders = [
            {
                "coin": "ETH",
                "side": "B",
                "limitPx": "3000",
                "sz": "2.0",
                "oid": 98765,
                "cloid": "0xabc123",
                "timestamp": 1609459200000,
            }
        ]

        _render_open_orders(self.mock_console, orders)

        # Verify table was created and printed
        self.assertTrue(self.mock_console.print.called)

    def test_space_function(self):
        """Test _space helper function"""
        # Test with positive lines
        _space(self.mock_console, 3)
        self.assertEqual(self.mock_console.print.call_count, 3)

        # Reset mock
        self.mock_console.reset_mock()

        # Test with zero lines
        _space(self.mock_console, 0)
        self.assertEqual(self.mock_console.print.call_count, 0)

        # Test with negative lines (should print nothing)
        _space(self.mock_console, -1)
        self.assertEqual(self.mock_console.print.call_count, 0)


if __name__ == "__main__":
    unittest.main()
