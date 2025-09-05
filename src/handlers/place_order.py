from __future__ import annotations
from hyperliquid.utils.types import Cloid
from typing import Any
from datetime import datetime
import click
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box
from .setup import setup, parse_cloid

## TODO: Allow Multiple deletes


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
    click.echo()
    table.add_column("Field", style="bold")
    table.add_column("Value")
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

    if "timestamp" in order_info:
        ts = datetime.fromtimestamp(order_info["timestamp"] / 1000)
        table.add_row("Created", ts.strftime("%Y-%m-%d %H:%M:%S"))

    console.print(table)


def _display_order_result(console: Console, result_data: list[dict]) -> None:
    """Display order operation results in a formatted table."""
    if not result_data:
        console.print(Text("No results returned", style="dim"))
        return

    click.echo()
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


def _display_cancel_result(
    console: Console, result_data: list[dict], order_id: int
) -> None:
    """Display cancel order results in a formatted table."""
    if not result_data:
        console.print(Text("No results returned", style="dim"))
        return

    click.echo()
    table = Table(
        title="Cancel Order Result",
        title_style="bold bright_yellow",
        header_style="yellow",
        border_style="yellow",
        show_header=False,
        box=box.ROUNDED,
        expand=False,
    )
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("Order ID", str(order_id))

    if result_data and len(result_data) > 0:
        status = result_data[0]
        if isinstance(status, str):
            table.add_row(
                "Status", Text(status, style="green" if status == "success" else "red")
            )
        elif isinstance(status, dict):
            if "error" in status:
                table.add_row("Status", Text("Failed", style="red"))
                table.add_row("Error", Text(str(status["error"]), style="red"))
            else:
                status_text = str(status.get("status", "Unknown"))
                style = "green" if status_text == "success" else "red"
                table.add_row("Status", Text(status_text, style=style))

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

    try:
        cloid = parse_cloid(client_order_id) if client_order_id else None
    except ValueError as e:
        console = Console()
        console.print(f"[bold red]Error: {e}[/bold red]")
        return
    try:
        response = exchange.order(
            coin, is_buy, size, price, order_type, reduce_only, cloid
        )
        result_data = _parse_order_response(response)
    except Exception as e:
        raise click.ClickException(f"Failed to place order: {e}")

    console = Console()
    _display_order_result(console, result_data)

    if result_data and len(result_data) > 0 and "error" not in result_data[0]:
        order_id = None
        for item in result_data:
            if isinstance(item, dict):
                if "oid" in item:
                    order_id = item["oid"]
                    break
                for value in item.values():
                    if isinstance(value, dict) and "oid" in value:
                        order_id = value["oid"]
                        break

        if order_id:
            try:
                order_status = info.query_order_by_oid(address, int(order_id))
                if order_status.get("status") == "order":
                    order_info = order_status["order"]["order"]
                    _display_order_status(console, order_info)
            except Exception:
                pass


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
    reduce_only: bool | None,
) -> None:
    """Modify an existing order by OID or CLOID."""
    if not price and not size and not time_in_force and not client_order_id:
        console = Console()
        console.print(
            "[bold red]Error: Must specify at least one parameter to modify (--price, --size, --tif, or --cloid).[/bold red]"
        )
        return

    info, exchange, address, _account = setup(production, private_key, account_address)
    id = int(oid_or_cloid) if oid_or_cloid.isdigit() else parse_cloid(oid_or_cloid)
    order_status = (
        info.query_order_by_oid(address, id)
        if isinstance(id, int)
        else info.query_order_by_cloid(address, id)
    )
    if order_status["status"] != "order" or order_status["order"]["status"] != "open":
        raise click.ClickException(
            "Order is not in a modifiable state or cannot be found."
        )
    order_info = order_status["order"]["order"]
    console = Console()
    _display_order_status(console, order_info)

    new_order: dict[str, Any] = {
        "coin": coin if coin is not None else order_info["coin"],
        "side": order_info["side"] == "B",
        "size": size if size is not None else float(order_info["sz"]),
        "limit_px": price if price is not None else float(order_info["limitPx"]),
        "tif": time_in_force if time_in_force is not None else order_info["tif"],
        "order_type": order_info["orderType"],
        "reduce_only": reduce_only
        if reduce_only is not None
        else order_info["reduceOnly"],
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
        existing_cloid = None
        if order_info.get("cloid"):
            try:
                existing_cloid = parse_cloid(order_info["cloid"])
            except ValueError:
                # If parsing fails, just pass None
                existing_cloid = None

        response = exchange.modify_order(
            id,
            new_order["coin"],
            new_order["side"],
            new_order["size"],
            new_order["limit_px"],
            order_type,
            new_order["reduce_only"],
            existing_cloid,
        )

        result_data = _parse_order_response(response)
        console = Console()
        _display_order_result(console, result_data)

    except Exception as e:
        raise click.ClickException(f"Failed to modify order: {e}")


def cancel_order_run(
    oid_or_cloid: str,
    private_key: str | None,
    production: bool,
    account_address: str | None,
) -> None:
    """Cancel an order by OID."""

    info, exchange, address, _account = setup(production, private_key, account_address)

    try:
        order = (
            info.query_order_by_oid(address, int(oid_or_cloid))
            if oid_or_cloid.isdigit()
            else info.query_order_by_cloid(address, Cloid.from_str(oid_or_cloid))
        )
        coin = order["order"]["order"]["coin"]
        order_id = order["order"]["order"]["oid"]
        response = exchange.cancel(coin, order_id)

        result_data = _parse_order_response(response)
        console = Console()
        _display_cancel_result(console, result_data, order_id)

    except Exception as e:
        raise click.ClickException(f"Failed to cancel order: {e}")
