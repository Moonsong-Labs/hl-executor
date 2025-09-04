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

def setup(production: bool, private_key: Optional[str]) -> Tuple[Any, Any, str]:
    """Initialize Hyperliquid SDK clients and return (info, exchange, address).

    - If `private_key` is provided, use it; otherwise load from .env (PRIVATE_KEY).
    - `production=True` selects mainnet; `False` uses testnet.
    """
    pk = _resolve_private_key(private_key)
    account: LocalAccount = eth_account.Account.from_key(pk)
    address = account.address
    base_url = constants.MAINNET_API_URL if production else constants.TESTNET_API_URL
    
    info = Info(base_url,skip_ws=True)   
    exchange = Exchange(account,base_url)
 
    env_label = "production" if production else "testnet"
    click.echo(f"Connected to {env_label} as {address}")

    return info, exchange, address
