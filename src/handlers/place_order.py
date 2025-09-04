def run(
    amount: str,
    direction: str,
    price: str,
    private_key: str | None,
    production: bool,
    account_address: str | None,
) -> None:
    """Place a Limit Order on the Perps Market"""
