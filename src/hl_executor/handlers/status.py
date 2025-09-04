from __future__ import annotations

import json
from typing import Any, Dict, List

import click

from .setup import setup


def run(production: bool, private_key: str | None, account_address: str | None) -> None:
    """Get positions and open orders using canonical SDK methods.

    Uses `info.user_state(address)` for positions and `info.open_orders(address)`
    for open orders, matching Hyperliquid SDK examples.
    """
    info, _exchange, address = setup(production, private_key, account_address)

    try:
        state: Dict[str, Any] = info.user_state(address)
    except Exception as e:
        raise click.ClickException(f"Failed to fetch user_state: {e}")

    positions: List[Dict[str, Any]] = (
        state.get("assetPositions") or state.get("positions") or []
    )

    try:
        open_orders: List[Dict[str, Any]] = info.open_orders(address)
    except Exception as e:
        click.echo(f"Warning: failed to fetch open_orders: {e}", err=True)
        open_orders = []

    result = {
        "address": address,
        "environment": "production" if production else "testnet",
        "positions": positions,
        "open_orders": open_orders,
    }

    click.echo(json.dumps(result, indent=2))
