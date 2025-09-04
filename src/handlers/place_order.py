from __future__ import annotations
from typing import Any
from datetime import datetime
import click
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box
from .setup import setup
from hyperliquid.utils.types import Cloid


## TODO: Test Delete
## TODO: Test CLoids


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


def _display_order_status(console: Console, order_info: dict) -> None:
    """Display current order status in a formatted table."""
    table = Table(
        title="Current Order Status",
        title_style="bold bright_cyan",
        header_style="cyan",
        border_style="cyan",
        box=box.ROUNDED,
        expand=False,
    )
    table.add_column("Field", style="bold")
    table.add_column("Value")

    # Order details
    table.add_row("Order ID", str(order_info.get("oid", "N/A")))
    table.add_row("Coin", order_info.get("coin", "N/A"))
    table.add_row("Side", "Buy" if order_info.get("side") == "B" else "Sell")
    table.add_row("Size", order_info.get("sz", "N/A"))
    table.add_row("Price", order_info.get("limitPx", "N/A"))
    table.add_row("Order Type", order_info.get("orderType", "N/A"))
    table.add_row("Time in Force", order_info.get("tif", "N/A"))
    table.add_row("Reduce Only", "Yes" if order_info.get("reduceOnly") else "No")

    if order_info.get("cloid"):
        table.add_row("Client Order ID", str(order_info["cloid"]))

    # Add timestamp if available
    if "timestamp" in order_info:
        ts = datetime.fromtimestamp(order_info["timestamp"] / 1000)
        table.add_row("Created", ts.strftime("%Y-%m-%d %H:%M:%S"))

    console.print(table)


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

    cloid = Cloid.from_str(client_order_id) if client_order_id else None

    try:
        response = exchange.order(
            coin, is_buy, size, price, order_type, reduce_only, cloid
        )
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
    if not price and not size and not time_in_force and not client_order_id:
        console = Console()
        console.print(
            "[bold red]Error: Must specify at least one parameter to modify (--price, --size, --tif, or --cloid).[/bold red]"
        )
        return

    info, exchange, address, _account = setup(production, private_key, account_address)
    oid = int(oid_or_cloid)
    order_status = info.query_order_by_oid(address, oid)

    if order_status["status"] != "order" or order_status["order"]["status"] != "open":
        raise click.ClickException(
            "Order is not in a modifiable state or cannot be found."
        )
    order_info = order_status["order"]["order"]

    # Display current order status
    console = Console()
    _display_order_status(console, order_info)

    new_order: dict[str, Any] = {
        "coin": coin if coin is not None else order_info["coin"],
        "side": order_info["side"] == "B",
        "size": size if size is not None else float(order_info["sz"]),
        "limit_px": price if price is not None else float(order_info["limitPx"]),
        "tif": time_in_force if time_in_force is not None else order_info["tif"],
        "order_type": order_info["orderType"],
    }

    if price is not None:
        if price <= 0:
            console = Console()
            console.print("[bold red]Error: Price must be positive.[/bold red]")
            return

    if size is not None:
        if size <= 0:
            console = Console()
            console.print("[bold red]Error: Size must be positive.[/bold red]")
            return
        new_order["sz"] = size

    order_type = {"limit": {"tif": new_order["tif"]}}

    try:
        try:
            response = exchange.modify_order(
                oid,
                new_order["coin"],
                new_order["side"],
                new_order["size"],
                new_order["limit_px"],
                order_type,
            )
        except ValueError:
            cloid = Cloid.from_str(oid_or_cloid)
            response = exchange.modify_order(
                cloid,
                new_order["coin"],
                new_order["side"],
                new_order["size"],
                new_order["limit_px"],
                order_type,
            )

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
