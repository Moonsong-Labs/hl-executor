from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Union
import click
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box
from .setup import setup


def _colorize_number(
    value: Union[str, float, int, Decimal, None],
    suffix: str = "",
    is_already_percentage: bool = False,
) -> Text:
    """Return a Text with green for positive, red for negative."""
    if value is None:
        return Text("-")
    try:
        num = float(value)
    except Exception:
        return Text(str(value))
    style = "green" if num > 0 else ("red" if num < 0 else "")
    if suffix == "%":
        # For percentages, check if value is already in percentage form
        if is_already_percentage:
            # Value is already a percentage (e.g., 0.05 for 5%), multiply by 100
            txt = f"{num * 100:.2f}{suffix}"
        else:
            # Value is already in display form (e.g., 5 for 5%)
            txt = f"{num:.2f}{suffix}"
    else:
        # For non-percentages, format as integer if it's a whole number
        if num == int(num):
            txt = f"{int(num)}{suffix}"
        else:
            txt = f"{num}{suffix}"
    return Text(txt, style=style)


def _normalize_positions(
    raw_positions: List[Dict[str, Any]] | None,
) -> List[Dict[str, Any]]:
    """Flatten possible wrapper formats to a consistent position dict list."""
    normalized: List[Dict[str, Any]] = []
    for item in raw_positions or []:
        pos = item.get("position") if isinstance(item, dict) else None
        if not pos and isinstance(item, dict):
            pos = item
        if not isinstance(pos, dict):
            continue
        normalized.append(pos)
    return normalized


def _render_positions(console: Console, positions: List[Dict[str, Any]]) -> None:
    if not positions:
        console.print(Text("No open positions", style="dim"))
        return

    table = Table(
        title="Positions",
        title_style="bold bright_cyan",
        header_style="cyan",
        border_style="cyan",
        box=box.ROUNDED,
        expand=False,
    )
    table.add_column("Coin", style="bold")
    table.add_column("Size")
    table.add_column("Lev")
    table.add_column("Entry Px")
    table.add_column("Value")
    table.add_column("Unreal PnL", justify="right")
    table.add_column("ROE", justify="right")
    table.add_column("Liq Px")
    table.add_column("Margin Used")

    for p in positions:
        coin = str(p.get("coin", "-"))
        size = str(p.get("szi") or p.get("sz") or "-")
        lev = p.get("leverage")
        if isinstance(lev, dict):
            lev_str = (
                f"{lev.get('value', '-')}{'x' if lev.get('value') is not None else ''}"
            )
        else:
            lev_str = str(lev) if lev is not None else "-"

        entry_px = p.get("entryPx")
        value = p.get("positionValue") or p.get("value")
        upnl = p.get("unrealizedPnl")
        roe = p.get("returnOnEquity")
        liq_px = p.get("liquidationPx")
        margin_used = p.get("marginUsed")

        roe_text = _colorize_number(roe, "%", is_already_percentage=True)
        upnl_text = _colorize_number(upnl)

        table.add_row(
            coin,
            size,
            str(lev_str),
            str(entry_px or "-"),
            str(value or "-"),
            upnl_text,
            roe_text,
            str(liq_px or "-"),
            str(margin_used or "-"),
        )

    console.print(table)


def _render_open_orders(console: Console, orders: List[Dict[str, Any]]) -> None:
    if not orders:
        console.print(Text("No open orders", style="dim"))
        return

    table = Table(
        title="Open Orders",
        title_style="bold bright_yellow",
        header_style="yellow",
        border_style="yellow",
        box=box.ROUNDED,
        expand=False,
    )
    table.add_column("Coin", style="bold")
    table.add_column("Side")
    table.add_column("Limit Px")
    table.add_column("Size")
    table.add_column("OID", justify="right")
    table.add_column("Client OID", overflow="fold")
    table.add_column("Time")

    for o in orders:
        coin = str(o.get("coin", "-"))
        side_raw = (o.get("side") or "").upper()
        side = Text(
            "Buy" if side_raw == "B" else ("Sell" if side_raw == "A" else side_raw)
        )
        side.stylize("green" if side_raw == "B" else ("red" if side_raw == "A" else ""))
        limit_px = str(o.get("limitPx") or "-")
        size = str(o.get("sz") or o.get("origSz") or "-")
        oid = str(o.get("oid") or "-")
        cloid = str(o.get("cloid") or "-")
        ts = o.get("timestamp")
        try:
            ts_dt = datetime.fromtimestamp(int(ts) / 1000) if ts else None
            time_str = ts_dt.strftime("%Y-%m-%d %H:%M:%S") if ts_dt else "-"
        except Exception:
            time_str = "-"

        table.add_row(coin, side, limit_px, size, oid, cloid, time_str)

    console.print(table)


def _space(console: Console, lines: int = 1) -> None:
    for _ in range(max(0, lines)):
        console.print("")


def run(production: bool, private_key: str | None, account_address: str | None) -> None:
    """Get positions and open orders and render with Rich tables."""
    info, _exchange, address, _account = setup(production, private_key, account_address)

    try:
        state: Dict[str, Any] = info.user_state(address)
    except Exception as e:
        raise click.ClickException(f"Failed to fetch user_state: {e}")

    positions_raw: List[Dict[str, Any]] = (
        state.get("assetPositions") or state.get("positions") or []
    )
    positions = _normalize_positions(positions_raw)

    try:
        open_orders: List[Dict[str, Any]] = info.open_orders(address)
    except Exception as e:
        click.echo(f"Warning: failed to fetch open_orders: {e}", err=True)
        open_orders = []

    console = Console()
    _space(console, 1)
    _render_positions(console, positions)
    _space(console, 1)
    _render_open_orders(console, open_orders)
