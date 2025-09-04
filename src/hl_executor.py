import click
from pathlib import Path
from dotenv import load_dotenv
from handlers.status import run as status_run
from handlers.deposit import run as deposit_run
from handlers.place_order import run as order_run


@click.group()
def cli():
    """HyperLiquid Executor - Python CLI"""
    load_dotenv(Path.cwd() / ".env", override=False)


@cli.command()
@click.option(
    "--private-key",
    "private_key",
    type=str,
    required=False,
    help="Private key for signing transactions",
)
@click.option(
    "--production",
    "production",
    is_flag=True,
    help="Connect to the production environment (default is testnet)",
)
@click.option(
    "--address",
    "account_address",
    type=str,
    required=False,
    help="This the HL account address which the Action will be performed on",
)
def status(
    private_key: str | None,
    production: bool,
    account_address: str | None,
):
    """Get positions and open orders for the account"""
    status_run(production, private_key, account_address)


@cli.command()
@click.argument(
    "direction",
    type=str,
)
@click.argument(
    "market",
    type=str,
)
@click.argument(
    "amount",
    type=str,
)
@click.argument(
    "price",
    type=str,
)
@click.option(
    "--private-key",
    "private_key",
    type=str,
    required=False,
    help="Private key for signing transactions",
)
@click.option(
    "--production",
    "production",
    is_flag=True,
    help="Connect to the production environment (default is testnet)",
)
@click.option(
    "--address",
    "account_address",
    type=str,
    required=False,
    help="This the HL account address which the Action will be performed on",
)
def order(
    amount: str,
    direction: str,
    price: str,
    private_key: str | None,
    production: bool,
    account_address: str | None,
):
    """Place Limit Order"""
    order_run(
        amount,
        direction,
        price,
        private_key,
        production,
        account_address,
    )


@cli.command()
@click.argument(
    "amount",
    type=str,
)
@click.option(
    "--private-key",
    "private_key",
    type=str,
    required=False,
    help="Private key for signing transactions",
)
@click.option(
    "--production",
    "production",
    is_flag=True,
    help="Connect to the production environment (default is testnet)",
)
@click.option(
    "--address",
    "account_address",
    type=str,
    required=False,
    help="This the HL account address which the Action will be performed on",
)
def deposit(
    amount: str,
    private_key: str | None,
    production: bool,
    account_address: str | None,
):
    """Deposit Funds from ARB -> Core"""
    deposit_run(
        production,
        private_key,
        account_address,
        amount,
    )


@cli.command()
def leverage():
    """Change the leverage of a market"""
    click.echo("Welcome to the Withdraw Funds from Core -> EVM command!")


@cli.command()
def withdraw():
    """Withdraw Funds from Core -> EVM"""
    click.echo("Welcome to the Withdraw Funds from Core -> EVM command!")


@cli.command()
def transfer():
    """Transfer funds between vaults"""
    click.echo("Welcome to the Vault Transfer command!")
