from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple

import click

from .setup import setup


def _try_info_open_orders(info: Any, address: str) -> List[Dict[str, Any]]:
    """Try multiple ways to get open orders using the Info client."""
    for meth in ("open_orders", "user_open_orders", "get_open_orders"):
        if hasattr(info, meth):
            try:
                out = getattr(info, meth)(address)
                if isinstance(out, list):
                    return out
            except Exception:
                pass
    return []


def _extract_from_user_state(
    state: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Extract positions and orders from a generic user_state response."""
    positions = state.get("assetPositions") or state.get("positions") or []

    orders: List[Dict[str, Any]] = []
    for k, v in state.items():
        if not isinstance(v, (list, dict)):
            continue
        key = k.lower()
        if "open" in key and "order" in key:
            if isinstance(v, list):
                orders.extend(v)
            elif isinstance(v, dict):
                for vv in v.values():
                    if isinstance(vv, list):
                        orders.extend(vv)
    return positions, orders


def run(production: bool, private_key: str | None, account_address: str | None) -> None:
    """Get positions and open orders for the provided private key."""
    info = exchange = address = None  # for finally-scope
    info, exchange, address = setup(production, private_key, account_address)

    positions: List[Dict[str, Any]] = []
    open_orders: List[Dict[str, Any]] = []

    state = None
    for meth in ("user_state", "userState", "get_user_state"):
        if hasattr(info, meth):
            try:
                state = getattr(info, meth)(address)
                break
            except Exception:
                state = None

    if isinstance(state, dict):
        p, o = _extract_from_user_state(state)
        positions = p or positions
        open_orders = o or open_orders

    if not open_orders and info is not None:
        open_orders = _try_info_open_orders(info, address)

    result = {
        "address": address,
        "environment": "production" if production else "testnet",
        "positions": positions,
        "open_orders": open_orders,
    }

    click.echo(json.dumps(result, indent=2))
