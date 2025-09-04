from __future__ import annotations
from typing import Any
import click
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box
from .setup import setup
from hyperliquid.utils.types import Cloid


def _parse_order_response(response: dict) -> list[dict[str, str]]:
    """Parse the common structure of order placement/cancellation API responses."""
    if response.get("status") != "ok":
        return [{"error": f"API returned non-ok status: {response.get('status')}"}]

    try:
        data = response["response"]["data"]
        if "statuses" in data:
            return data["statuses"]
        return [data]
    except (KeyError, TypeError) as e:
        return [{"error": f"Failed to parse API response: {e}"}]


def _display_order_result(console: Console, result_data: list[dict]) -> None:
    """Display order operation results in a formatted table."""
    if not result_data:
        console.print(Text("No results returned", style="dim"))
        return

    table = Table(
        title="Order Result",
        title_style="bold bright_green",
        header_style="green",
        border_style="green",
        box=box.ROUNDED,
        expand=False,
    )
    table.add_column("Field", style="bold")
    table.add_column("Value")

    for item in result_data:
        if "error" in item:
            table.add_row("Error", Text(str(item["error"]), style="red"))
        else:
            for key, value in item.items():
                if isinstance(value, dict):
                    if "oid" in value:
                        table.add_row("Order ID", str(value["oid"]))
                    if "cloid" in value:
                        table.add_row("Client Order ID", str(value["cloid"]))
                else:
                    table.add_row(str(key).replace("_", " ").title(), str(value))

    console.print(table)


def new_order_run(
    coin: str,
    is_buy: bool,
    size: float,
    price: float,
    private_key: str | None,
    production: bool,
    account_address: str | None,
    time_in_force: str,
    client_order_id: str | None,
    post_only: bool,
    reduce_only: bool,
) -> None:
    """Place a new limit order on the perps market."""

    # Input validation
    if price <= 0:
        console = Console()
        console.print("[bold red]Error: Price must be positive.[/bold red]")
        return
    if size <= 0:
        console = Console()
        console.print("[bold red]Error: Size must be positive.[/bold red]")
        return

    info, exchange, address, _account = setup(production, private_key, account_address)

    order_type: dict[str, Any] = {"limit": {"tif": time_in_force}}
    if post_only:
        order_type["limit"]["postOnly"] = True
    if reduce_only:
        order_type["limit"]["reduceOnly"] = True

    order_request: dict[str, Any] = {
        "coin": coin,
        "is_buy": is_buy,
        "sz": size,
        "limit_px": price,
        "order_type": order_type,
    }

    if client_order_id:
        order_request["cloid"] = Cloid.from_str(client_order_id)

    try:
        response = exchange.bulk_orders([order_request])

        result_data = _parse_order_response(response)
        console = Console()
        _display_order_result(console, result_data)

    except Exception as e:
        raise click.ClickException(f"Failed to place order: {e}")


def modify_order_run(
    oid_or_cloid: str,
    coin: str | None,
    size: float | None,
    price: float | None,
    private_key: str | None,
    production: bool,
    account_address: str | None,
    time_in_force: str | None,
    client_order_id: str | None,
) -> None:
    """Modify an existing order by OID or CLOID."""

    # Validate that we have something to modify
    if not price and not size and not time_in_force and not client_order_id:
        console = Console()
        console.print(
            "[bold red]Error: Must specify at least one parameter to modify (--price, --size, --tif, or --cloid).[/bold red]"
        )
        return

    info, exchange, address, _account = setup(production, private_key, account_address)

    # Build modification request dynamically
    order_to_modify: dict[str, Any] = {}

    if coin:
        order_to_modify["coin"] = coin

    if price is not None:
        if price <= 0:
            console = Console()
            console.print("[bold red]Error: Price must be positive.[/bold red]")
            return
        order_to_modify["limit_px"] = price

    if size is not None:
        if size <= 0:
            console = Console()
            console.print("[bold red]Error: Size must be positive.[/bold red]")
            return
        order_to_modify["sz"] = size

    if time_in_force:
        order_to_modify["order_type"] = {"limit": {"tif": time_in_force}}

    if client_order_id:
        order_to_modify["cloid"] = Cloid.from_str(client_order_id)

    try:
        # Determine if oid_or_cloid is an OID (numeric) or CLOID
        try:
            int(oid_or_cloid)
            oid = int(oid_or_cloid)
            modify_request = {"oid": oid, **order_to_modify}
            response = exchange.bulk_modify_orders_new([modify_request])
        except ValueError:
            # It's a CLOID
            cloid = Cloid.from_str(oid_or_cloid)
            modify_request = {"cloid": cloid, **order_to_modify}
            response = exchange.bulk_modify_orders_new([modify_request])

        result_data = _parse_order_response(response)
        console = Console()
        _display_order_result(console, result_data)

    except Exception as e:
        raise click.ClickException(f"Failed to modify order: {e}")


def cancel_order_run(
    coin: str,
    oid: str,
    private_key: str | None,
    production: bool,
    account_address: str | None,
) -> None:
    """Cancel an order by OID."""

    info, exchange, address, _account = setup(production, private_key, account_address)

    try:
        # Convert OID to integer
        order_id = int(oid)
        response = exchange.cancel(coin, order_id)

        result_data = _parse_order_response(response)
        console = Console()
        _display_order_result(console, result_data)

    except ValueError:
        raise click.ClickException(
            f"Invalid order ID: {oid}. Order ID must be numeric."
        )
    except Exception as e:
        raise click.ClickException(f"Failed to cancel order: {e}")


def run(
    amount: str,
    direction: str,
    price: str,
    private_key: str | None,
    production: bool,
    account_address: str | None,
) -> None:
    """Legacy function - Place a Limit Order on the Perps Market"""
    # Convert legacy parameters to new format
    is_buy = direction.lower() in ["buy", "b", "long"]
    new_order_run(
        "ETH",  # Default to ETH for legacy compatibility
        is_buy,
        float(amount),
        float(price),
        private_key,
        production,
        account_address,
        "Gtc",  # Default time in force
        None,  # No client order ID
        False,  # Not post only
        False,  # Not reduce only
    )
