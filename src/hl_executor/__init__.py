import click


@click.group()
def cli():
    """HyperLiquid Executor - Python CLI"""

    click.echo("Welcome to HyperLiquid Executor CLI!")

@cli.command()
def status():
    """Get Order Status"""
    click.echo("Welcome to the Get Order Status command!")

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


