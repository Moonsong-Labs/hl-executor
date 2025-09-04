import click


def run(
    production: bool, private_key: str | None, account_address: str | None, amount: str
) -> None:
    click.echo("Hello")
