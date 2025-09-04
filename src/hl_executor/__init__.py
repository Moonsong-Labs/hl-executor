import click
from pathlib import Path
from dotenv import load_dotenv
from .handlers.status import run as status_run


@click.group()
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
@click.pass_context
def cli(
    ctx: click.Context,
    private_key: str | None,
    production: bool,
    account_address: str | None,
):
    """HyperLiquid Executor - Python CLI"""

    load_dotenv(Path.cwd() / ".env", override=False)

    ctx.ensure_object(dict)
    ctx.obj["private_key"] = private_key
    ctx.obj["production"] = production
    ctx.obj["account_address"] = account_address


@cli.command()
@click.pass_context
def status(ctx: click.Context):
    """Get positions and open orders for the account"""
    status_run(
        ctx.obj.get("production", False),
        ctx.obj.get("private_key"),
        ctx.obj.get("account_address"),
    )


@cli.command()
def order():
    """Place Limit Order"""
    click.echo("Welcome to the Place Limit Order command!")


@cli.command()
def deposit():
    """Deposit Funds from EVM -> Core"""
    click.echo("Welcome to the Deposit Funds from EVM -> Core command!")


@cli.command()
def withdraw():
    """Withdraw Funds from Core -> EVM"""
    click.echo("Welcome to the Withdraw Funds from Core -> EVM command!")


@cli.command()
def transfer():
    """Transfer funds between vaults"""
    click.echo("Welcome to the Vault Transfer command!")
