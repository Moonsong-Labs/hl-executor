import os
import sys
import unittest
from unittest.mock import patch
import click

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from handlers.setup import _resolve_private_key, _resolve_account_address


class TestSetupResolution(unittest.TestCase):
    """Test private key and account address resolution logic"""

    # Tests for _resolve_private_key
    @patch.dict(os.environ, {"PRIVATE_KEY": "env_private_key"})
    def test_resolve_private_key_cli_precedence(self):
        """CLI parameter should override environment variable"""
        result = _resolve_private_key("cli_private_key")
        self.assertEqual(result, "cli_private_key")

    @patch.dict(os.environ, {"PRIVATE_KEY": "env_private_key"})
    def test_resolve_private_key_env_fallback(self):
        """Should use environment variable when CLI param is None"""
        result = _resolve_private_key(None)
        self.assertEqual(result, "env_private_key")

    @patch.dict(os.environ, {"PRIVATE_KEY": ""})
    def test_resolve_private_key_empty_env(self):
        """Empty env var should be treated as missing"""
        with self.assertRaises(click.ClickException) as ctx:
            _resolve_private_key(None)
        self.assertIn("Missing private key", str(ctx.exception))

    @patch.dict(os.environ, {}, clear=True)
    def test_resolve_private_key_missing_raises(self):
        """Should raise ClickException when both CLI and env are missing"""
        with self.assertRaises(click.ClickException) as ctx:
            _resolve_private_key(None)
        self.assertIn("Missing private key", str(ctx.exception))

    # Tests for _resolve_account_address
    @patch.dict(
        os.environ, {"ACCOUNT_ADDRESS": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7"}
    )
    def test_resolve_account_address_cli_precedence(self):
        """CLI parameter should override environment variable"""
        cli_address = "0x5aAeb6053f3E94C9b9A09f33669435E7Ef1BeAed"
        result = _resolve_account_address(cli_address)
        # Should return checksummed version of CLI address
        self.assertEqual(result, "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed")

    @patch.dict(
        os.environ, {"ACCOUNT_ADDRESS": "0x742d35cc6634c0532925a3b844bc9e7595f0beb7"}
    )
    def test_resolve_account_address_env_fallback(self):
        """Should use environment variable when CLI param is None"""
        result = _resolve_account_address(None)
        # Should return checksummed version
        self.assertEqual(result, "0x742D35Cc6634C0532925A3B844bC9e7595f0bEB7")

    @patch.dict(
        os.environ, {"ACCOUNT_ADDRESS": "0x742d35cc6634c0532925a3b844bc9e7595f0beb7"}
    )
    def test_resolve_account_address_checksum_conversion(self):
        """Should convert non-checksummed address to checksummed format"""
        result = _resolve_account_address(None)
        # Verify it's properly checksummed (mixed case)
        self.assertTrue(any(c.isupper() for c in result[2:]))
        self.assertTrue(any(c.islower() for c in result[2:]))

    @patch.dict(os.environ, {"ACCOUNT_ADDRESS": ""})
    def test_resolve_account_address_empty_env(self):
        """Empty env var should be treated as missing"""
        with self.assertRaises(click.ClickException) as ctx:
            _resolve_account_address(None)
        self.assertIn("Missing account address", str(ctx.exception))

    @patch.dict(os.environ, {}, clear=True)
    def test_resolve_account_address_missing_raises(self):
        """Should raise ClickException when both CLI and env are missing"""
        with self.assertRaises(click.ClickException) as ctx:
            _resolve_account_address(None)
        self.assertIn("Missing account address", str(ctx.exception))

    def test_resolve_account_address_lowercase_cli(self):
        """Should handle lowercase addresses from CLI"""
        lowercase_addr = "0x742d35cc6634c0532925a3b844bc9e7595f0beb7"
        result = _resolve_account_address(lowercase_addr)
        self.assertEqual(result, "0x742D35Cc6634C0532925A3B844bC9e7595f0bEB7")

    def test_resolve_account_address_uppercase_cli(self):
        """Should handle uppercase addresses from CLI"""
        uppercase_addr = "0x742D35CC6634C0532925A3B844BC9E7595F0BEB7"
        result = _resolve_account_address(uppercase_addr)
        self.assertEqual(result, "0x742D35Cc6634C0532925A3B844bC9e7595f0bEB7")


if __name__ == "__main__":
    unittest.main()
