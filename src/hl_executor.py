import click
from pathlib import Path
from dotenv import load_dotenv
from handlers.status import run as status_run
from handlers.deposit import run as deposit_run


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


@cli.group()
def order():
    """Limit order operations"""
    pass


@order.command()
@click.argument("coin", type=str)
@click.argument("direction", type=click.Choice(["buy", "sell"], case_sensitive=False))
@click.argument("size", type=float)
@click.argument("price", type=float)
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
@click.option(
    "--tif",
    "time_in_force",
    type=click.Choice(["Gtc", "Ioc", "Alo"], case_sensitive=False),
    default="Gtc",
    help="Time in force: Gtc (Good Till Cancel), Ioc (Immediate or Cancel), Alo (Add Liquidity Only)",
)
@click.option(
    "--cloid",
    "client_order_id",
    type=str,
    required=False,
    help="Client order ID for tracking",
)
@click.option(
    "--post-only",
    "post_only",
    is_flag=True,
    help="Post only order (maker only)",
)
@click.option(
    "--reduce-only",
    "reduce_only",
    is_flag=True,
    help="Reduce only order",
)
def new(
    coin: str,
    direction: str,
    size: float,
    price: float,
    private_key: str | None,
    production: bool,
    account_address: str | None,
    time_in_force: str,
    client_order_id: str | None,
    post_only: bool,
    reduce_only: bool,
):
    """Place a new limit order"""
    from handlers.place_order import new_order_run

    new_order_run(
        coin,
        direction.lower() == "buy",
        size,
        price,
        private_key,
        production,
        account_address,
        time_in_force,
        client_order_id,
        post_only,
        reduce_only,
    )


@order.command()
@click.argument("oid_or_cloid", type=str)
@click.option(
    "--coin",
    type=str,
    help="Market symbol (required if specifying new parameters)",
)
@click.option(
    "--size",
    type=float,
    help="New order size",
)
@click.option(
    "--price",
    type=float,
    help="New order price",
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
@click.option(
    "--tif",
    "time_in_force",
    type=click.Choice(["Gtc", "Ioc", "Alo"], case_sensitive=False),
    help="Time in force",
)
@click.option(
    "--cloid",
    "client_order_id",
    type=str,
    required=False,
    help="New client order ID",
)
def modify(
    oid_or_cloid: str,
    coin: str | None,
    size: float | None,
    price: float | None,
    private_key: str | None,
    production: bool,
    account_address: str | None,
    time_in_force: str | None,
    client_order_id: str | None,
):
    """Modify an existing order by OID or CLOID"""
    from handlers.place_order import modify_order_run

    modify_order_run(
        oid_or_cloid,
        coin,
        size,
        price,
        private_key,
        production,
        account_address,
        time_in_force,
        client_order_id,
    )


@order.command()
@click.argument("coin", type=str)
@click.argument("oid", type=str)
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
def cancel(
    coin: str,
    oid: str,
    private_key: str | None,
    production: bool,
    account_address: str | None,
):
    """Cancel an order by OID"""
    from handlers.place_order import cancel_order_run

    cancel_order_run(
        coin,
        oid,
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


if __name__ == "__main__":
    cli()
