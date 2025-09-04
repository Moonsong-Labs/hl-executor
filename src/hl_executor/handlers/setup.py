from __future__ import annotations
from typing import Optional, Tuple, Any
from hyperliquid.info import Info
from hyperliquid.utils import constants
from hyperliquid.exchange import Exchange
import eth_account
from eth_account.signers.local import LocalAccount

import click
import os


def _resolve_private_key(cli_private_key: Optional[str]) -> str:
    """Choose private key from CLI if provided, else from env (.env loaded)."""
    if cli_private_key:
        return cli_private_key

    env_key = os.getenv("PRIVATE_KEY")
    if not env_key:
        raise click.ClickException(
            "Missing private key. Provide --private-key or set PRIVATE_KEY in .env"
        )
    return env_key


def _resolve_account_address(cli_account_address: Optional[str]) -> str:
    """Choose account address from CLI if provided, else from env (.env loaded)."""
    if cli_account_address:
        return cli_account_address

    env_address = os.getenv("ACCOUNT_ADDRESS")
    if not env_address:
        raise click.ClickException(
            "Missing account address. Provide --address or set ACCOUNT_ADDRESS in .env"
        )
    return env_address


def setup(
    production: bool, private_key: Optional[str], account_address: Optional[str]
) -> Tuple[Any, Any, str]:
    """Initialize Hyperliquid SDK clients and return (info, exchange, address).

    - If `private_key` is provided, use it; otherwise load from .env (PRIVATE_KEY).
    - `production=True` selects mainnet; `False` uses testnet.
    """
    pk = _resolve_private_key(private_key)
    address = _resolve_account_address(account_address)
    account: LocalAccount = eth_account.Account.from_key(pk)
    base_url = constants.MAINNET_API_URL if production else constants.TESTNET_API_URL

    info = Info(base_url, skip_ws=True)
    exchange = Exchange(wallet=account, base_url=base_url, account_address=address)

    env_label = "production" if production else "testnet"
    click.echo(f"Connected to {env_label}:{address} with {account.address}")

    return info, exchange, address
