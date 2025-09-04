from .setup import setup
import click
from .constants import (
    ARB_PROD_RPC,
    ARB_TEST_RPC,
    USDC_ARB_PROD_ADDR,
    USDC_ARB_TEST_ADDR,
    ERC20_ABI,
    BRIDGE2_PROD_ADDR,
    BRIDGE2_TEST_ADDR,
)
from web3 import Web3, HTTPProvider
from rich.console import Console
from typing import Any
from rich.table import Table
from rich.text import Text
from rich import box


def run(
    production: bool, private_key: str | None, account_address: str | None, amount: str
) -> None:
    """Deposit USDC to HyperCore from Arbitrum via signer wallet address"""
    info, exchange, address, account = setup(production, private_key, account_address)
    url = ARB_PROD_RPC if production else ARB_TEST_RPC
    w3 = Web3(HTTPProvider(url))

    usdc_address = (
        Web3.to_checksum_address(USDC_ARB_PROD_ADDR)
        if production
        else Web3.to_checksum_address(USDC_ARB_TEST_ADDR)
    )
    bridge_address = (
        Web3.to_checksum_address(BRIDGE2_PROD_ADDR)
        if production
        else Web3.to_checksum_address(BRIDGE2_TEST_ADDR)
    )

    eth_balance = w3.eth.get_balance(account.address)
    usdc_contract = w3.eth.contract(address=usdc_address, abi=ERC20_ABI)
    usdc_balance = usdc_contract.functions.balanceOf(account.address).call()
    _renderHeader(eth_balance, usdc_balance)
    click.echo(f"Hello {account.address}, your balance is {eth_balance}.")
    click.echo(usdc_balance)


def _renderHeader(ethBalance: Any, usdcBalance: Any) -> None:
    """Render the header for the ETH statuses"""
    console = Console()
    table = Table(
        show_header=False,
        box=None,
        padding=(0, 1),
        title="Signer Balances",
        title_style="bold bright_cyan",
        title_justify="left",
    )
    table.add_column("k", style="bold cyan", no_wrap=True)
    table.add_column("v")
    table.add_row("ETH Balance", str(ethBalance))
    table.add_row("USDC Balance", str(usdcBalance))
    console.print(table)
