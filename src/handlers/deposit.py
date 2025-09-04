import click
from .setup import setup
from .constants import HYPEREVM_PROD_RPC, HYPEREVM_TEST_RPC
from web3 import Web3, HTTPProvider


def run(
    production: bool, private_key: str | None, account_address: str | None, amount: str
) -> None:
    info, exchange, address, account = setup(production, private_key, account_address)
    url = HYPEREVM_PROD_RPC if production else HYPEREVM_TEST_RPC
    w3 = Web3(HTTPProvider(url))
    balance = w3.eth.get_balance(account.address)
    click.echo(f"Hello {account.address}, your balance is {balance}.")
