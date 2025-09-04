from __future__ import annotations
from eth_typing.evm import ChecksumAddress
from typing import Optional, Tuple
from web3 import Web3
from hyperliquid.info import Info
from hyperliquid.utils import constants
from hyperliquid.exchange import Exchange
import eth_account
from eth_account.signers.local import LocalAccount
from rich.table import Table
from rich.console import Console

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


def _resolve_account_address(cli_account_address: Optional[str]) -> ChecksumAddress:
    """Choose account address from CLI if provided, else from env (.env loaded)."""
    if cli_account_address:
        return Web3.to_checksum_address(cli_account_address)

    env_address = os.getenv("ACCOUNT_ADDRESS")
    if not env_address:
        raise click.ClickException(
            "Missing account address. Provide --address or set ACCOUNT_ADDRESS in .env"
        )
    return Web3.to_checksum_address(env_address)


def setup(
    production: bool, private_key: Optional[str], account_address: Optional[str]
) -> Tuple[Info, Exchange, str, LocalAccount]:
    """Initialize Hyperliquid SDK clients and return (info, exchange, address).

    - If `private_key` is provided, use it; otherwise load from .env (PRIVATE_KEY).
    - `production=True` selects mainnet; `False` uses testnet.
    """
    pk = _resolve_private_key(private_key)
    address = _resolve_account_address(account_address)
    account = eth_account.Account.from_key(pk)  # type: ignore[attr-defined]
    base_url = constants.MAINNET_API_URL if production else constants.TESTNET_API_URL

    info = Info(base_url, skip_ws=True)
    exchange = Exchange(wallet=account, base_url=base_url, account_address=address)

    env_label = "production" if production else "testnet"
    console = Console()
    _render_header(console, address, account.address, env_label)

    return info, exchange, address, account


def _render_header(
    console: Console, address: str, signer: str, environment: str
) -> None:
    hdr = Table(
        show_header=False,
        box=None,
        padding=(0, 1),
        title="Session Info",
        title_style="bold bright_cyan",
        title_justify="left",
    )
    hdr.add_column("k", style="bold cyan", no_wrap=True)
    hdr.add_column("v")
    hdr.add_row("Environment", environment)
    hdr.add_row("HL Account", address)
    hdr.add_row("Signer", signer)
    console.print(hdr)
