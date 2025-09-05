from __future__ import annotations
from .setup import setup
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Any
from rich.table import Table
from rich.text import Text
from rich import box
from decimal import Decimal
from web3 import Web3
import time


def run(
    production: bool,
    private_key: str | None,
    account_address: str | None,
    amount: str,
    no_confirm: bool = False,
    destination_address: str | None = None,
) -> None:
    """Withdraw USDC from HyperLiquid Core to EVM (Arbitrum)"""

    info, exchange, address, account = setup(production, private_key, account_address)

    console = Console()
    initial_hl_balance = _get_hl_usd_balance(info, address)
    withdrawable_balance = _get_withdrawable_balance(info, address)

    if destination_address:
        destination = Web3.to_checksum_address(destination_address)
    else:
        destination = address

    try:
        withdraw_amount = Decimal(amount)
    except Exception as e:
        raise click.ClickException(f"Invalid amount format: {e}")

    if withdraw_amount < 2:
        raise click.ClickException(
            f"Minimum withdrawal amount is $2 (includes $1 fee). Requested: ${withdraw_amount:.2f}"
        )

    if withdrawable_balance < float(withdraw_amount):
        raise click.ClickException(
            f"Insufficient withdrawable balance. Available: ${withdrawable_balance:.2f}, Requested: ${withdraw_amount:.2f}"
        )

    _render_initial_balance(console, initial_hl_balance, withdrawable_balance, address)

    net_amount = float(withdraw_amount) - 1.0  # Subtract $1 fee
    console.print(f"\n💸 Withdrawal Amount: ${withdraw_amount:.2f}")
    console.print(f"💰 Amount after fee: ${net_amount:.2f} (fee: $1.00)")
    console.print(f"📍 Destination: {destination}\n")

    if not no_confirm and not click.confirm("Proceed with withdrawal?"):
        raise click.ClickException("Withdrawal cancelled")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Initiating withdrawal...", total=None)

        try:
            result = exchange.withdraw_from_bridge(float(withdraw_amount), destination)

            if result and result.get("status") == "ok":
                console.print("✅ Withdrawal initiated successfully")
                tx_hash = result.get("response", {}).get("txHash", "N/A")
                if tx_hash != "N/A":
                    console.print(f"📝 Transaction hash: {tx_hash}")
            else:
                error_msg = (
                    result.get("response", "Unknown error") if result else "No response"
                )
                raise click.ClickException(f"Withdrawal failed: {error_msg}")

        except Exception as e:
            if "Insufficient" in str(e):
                raise click.ClickException(f"Insufficient balance for withdrawal: {e}")
            elif "rate limit" in str(e).lower():
                raise click.ClickException("Rate limited. Please try again later.")
            else:
                raise click.ClickException(f"Withdrawal failed: {e}")

        progress.update(task, description="Waiting for balance update...")

        time.sleep(3)

    final_hl_balance = _get_hl_usd_balance(info, address)
    balance_change = initial_hl_balance - final_hl_balance

    _render_summary(
        console,
        float(withdraw_amount),
        net_amount,
        balance_change,
        initial_hl_balance,
        final_hl_balance,
    )

    console.print(
        "\n⏳ Note: Withdrawal to Arbitrum typically takes ~5 minutes to finalize."
    )


def _get_hl_usd_balance(info: Any, address: str) -> float:
    """Get the USD balance from HyperLiquid Core (perps)"""
    try:
        state = info.user_state(address)
        balances = state.get("marginSummary", {})
        account_value = float(balances.get("accountValue", 0))
        return account_value
    except Exception:
        return 0.0


def _get_withdrawable_balance(info: Any, address: str) -> float:
    """Get the withdrawable USD balance from HyperLiquid Core"""
    try:
        state = info.user_state(address)
        withdrawable = float(state.get("withdrawable", 0))
        return withdrawable
    except Exception:
        return 0.0


def _render_initial_balance(
    console: Console, total_balance: float, withdrawable: float, address: str
) -> None:
    """Render the initial balance table"""
    table = Table(
        show_header=False,
        box=None,
        padding=(0, 1),
        title="HyperLiquid Core Balance",
        title_style="bold bright_cyan",
        title_justify="left",
    )
    table.add_column("Field", style="bold cyan", no_wrap=True)
    table.add_column("Value", justify="right")
    table.add_row("Account", address)
    table.add_row("Total Balance", f"${total_balance:.2f}")
    table.add_row("Withdrawable", f"${withdrawable:.2f}")
    console.print(table)


def _render_summary(
    console: Console,
    requested: float,
    net_amount: float,
    balance_change: float,
    initial_balance: float,
    final_balance: float,
) -> None:
    """Render the withdrawal summary"""
    table = Table(
        show_header=False,
        box=box.DOUBLE,
        padding=(0, 1),
        title="Withdrawal Summary",
        title_style="bold bright_green",
        border_style="green",
    )
    table.add_column("Field", style="bold green", no_wrap=True)
    table.add_column("Value", justify="right")
    table.add_row("Requested", f"${requested:.2f}")
    table.add_row("Net Amount", f"${net_amount:.2f}")
    table.add_row("Fee", "$1.00")
    table.add_row("", "")
    table.add_row("Initial Balance", f"${initial_balance:.2f}")
    table.add_row("Final Balance", f"${final_balance:.2f}")
    table.add_row("Balance Change", f"-${balance_change:.2f}")

    expected_change = requested
    if abs(balance_change - expected_change) < 0.01:
        status = Text("✅ SUCCESS", style="bold green")
    elif balance_change > 0:
        status = Text("⏳ PROCESSING", style="bold yellow")
    else:
        status = Text("❌ ERROR", style="bold red")

    table.add_row("Status", status)

    console.print("\n")
    console.print(table)
