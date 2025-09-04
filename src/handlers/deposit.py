# from __future__ import annotations
from .setup import setup
import click
from .constants import (
    ARB_PROD_RPC,
    ARB_TEST_RPC,
    USDC_ARB_PROD_ADDR,
    USDC_ARB_TEST_ADDR,
    ERC20_ABI,
    BRIDGE2_PROD_ADDR,
    BRIDGE2_TEST_ADDR,
)
from web3 import Web3, HTTPProvider
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Any
from rich.table import Table
from rich.text import Text
from rich import box
from decimal import Decimal
import time


def run(
    production: bool, private_key: str | None, account_address: str | None, amount: str
) -> None:
    """Deposit USDC to HyperCore from Arbitrum via signer wallet address"""
    info, exchange, address, account = setup(production, private_key, account_address)

    url = ARB_PROD_RPC if production else ARB_TEST_RPC
    w3 = Web3(HTTPProvider(url))

    if not w3.is_connected():
        raise click.ClickException("Failed to connect to Arbitrum RPC")

    usdc_address = (
        Web3.to_checksum_address(USDC_ARB_PROD_ADDR)
        if production
        else Web3.to_checksum_address(USDC_ARB_TEST_ADDR)
    )
    bridge_address = (
        Web3.to_checksum_address(BRIDGE2_PROD_ADDR)
        if production
        else Web3.to_checksum_address(BRIDGE2_TEST_ADDR)
    )

    console = Console()
    usdc_contract = w3.eth.contract(address=usdc_address, abi=ERC20_ABI)

    eth_balance_wei = w3.eth.get_balance(account.address)
    eth_balance = Decimal(str(w3.from_wei(eth_balance_wei, "ether")))
    usdc_balance_raw = usdc_contract.functions.balanceOf(account.address).call()
    usdc_decimals = usdc_contract.functions.decimals().call()
    usdc_balance = Decimal(usdc_balance_raw) / Decimal(10**usdc_decimals)

    _render_balances(console, eth_balance, usdc_balance, account.address)

    try:
        deposit_amount = Decimal(amount)
        deposit_amount_raw = int(deposit_amount * Decimal(10**usdc_decimals))
    except Exception as e:
        raise click.ClickException(f"Invalid amount format: {e}")

    # Check minimum deposit amount
    if deposit_amount < 5:
        raise click.ClickException(
            f"Minimum deposit amount is 5 USDC. Requested: {deposit_amount:.6f}"
        )

    if usdc_balance < deposit_amount:
        raise click.ClickException(
            f"Insufficient USDC balance. Have: {usdc_balance:.6f}, Need: {deposit_amount:.6f}"
        )

    if eth_balance < 0.001:
        console.print(Text("⚠️  Warning: Low ETH balance for gas fees", style="yellow"))

    initial_hl_balance = _get_hl_usd_balance(info, account.address)
    console.print(f"\n💰 Initial HL balance: ${initial_hl_balance:.2f}")
    console.print(f"📤 Depositing: {deposit_amount:.6f} USDC\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Building transaction...", total=None)

        nonce = w3.eth.get_transaction_count(account.address)
        gas_price = w3.eth.gas_price

        transfer_tx = usdc_contract.functions.transfer(
            bridge_address, deposit_amount_raw
        ).build_transaction(
            {
                "from": account.address,
                "nonce": nonce,
                "gasPrice": gas_price,
            }
        )

        try:
            gas_estimate = w3.eth.estimate_gas(transfer_tx)
            transfer_tx["gas"] = int(gas_estimate * 1.2)  # Add 20% buffer
        except Exception as e:
            raise click.ClickException(f"Gas estimation failed: {e}")

        progress.update(task, description="Signing transaction...")

        signed_tx = w3.eth.account.sign_transaction(
            transfer_tx, private_key=account.key.hex()
        )

        progress.update(task, description="Sending transaction to bridge...")

        try:
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            console.print(f"✅ Transaction sent: {tx_hash.hex()}")
        except Exception as e:
            raise click.ClickException(f"Transaction failed: {e}")

        progress.update(task, description="Waiting for confirmation...")

        try:
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            if receipt["status"] != 1:
                raise click.ClickException("Transaction failed on chain")
            console.print(f"✅ Transaction confirmed in block {receipt['blockNumber']}")
        except Exception as e:
            raise click.ClickException(f"Transaction confirmation failed: {e}")

    console.print("\n⏳ Waiting for HyperLiquid credit...")
    credited = _poll_for_hl_credit(
        console, info, account.address, initial_hl_balance, float(deposit_amount)
    )

    if not credited:
        raise click.ClickException("Timeout waiting for HyperLiquid credit")

    if address.lower() != account.address.lower():
        console.print(
            f"\n🔄 Transferring from signer {account.address} to target {address}..."
        )

        try:
            before_transfer = _get_hl_usd_balance(info, address)
            transfer_result = exchange.usd_transfer(float(deposit_amount), address)

            if transfer_result and transfer_result.get("status") == "ok":
                console.print("✅ Internal transfer initiated")

                time.sleep(2)

                final_balance = _get_hl_usd_balance(info, address)
                transferred = final_balance - before_transfer
                fee = float(deposit_amount) - transferred

                if transferred > float(deposit_amount) * 0.99:  # 1% tolerance for fees
                    console.print(
                        f"✅ Transfer complete. Amount: ${transferred:.2f}, Fee: ${fee:.4f}"
                    )
                else:
                    console.print(
                        f"⚠️  Transfer amount mismatch. Expected: ${deposit_amount:.2f}, Got: ${transferred:.2f}"
                    )
            else:
                raise click.ClickException(f"USD transfer failed: {transfer_result}")
        except Exception as e:
            raise click.ClickException(f"Internal transfer failed: {e}")

    final_hl_balance = _get_hl_usd_balance(info, address)
    net_credited = final_hl_balance - initial_hl_balance

    _render_summary(console, float(deposit_amount), net_credited, final_hl_balance)


def _get_hl_usd_balance(info: Any, address: str) -> float:
    """Get the USD balance from HyperLiquid"""
    try:
        state = info.user_state(address)
        balances = state.get("marginSummary", {})
        account_value = float(balances.get("accountValue", 0))
        return account_value
    except Exception:
        return 0.0


def _poll_for_hl_credit(
    console: Console,
    info: Any,
    address: str,
    initial_balance: float,
    expected_amount: float,
    max_attempts: int = 60,
    poll_interval: float = 2.0,
) -> bool:
    """Poll HyperLiquid for balance credit"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Checking HyperLiquid balance...", total=max_attempts)

        for attempt in range(max_attempts):
            current_balance = _get_hl_usd_balance(info, address)
            credited = current_balance - initial_balance

            progress.update(task, advance=1)

            if credited >= expected_amount * 0.999:
                console.print(f"\n✅ HyperLiquid account credited: ${credited:.2f}")
                return True

            time.sleep(poll_interval)

    return False


def _render_balances(
    console: Console, eth_balance: Decimal, usdc_balance: Decimal, signer: str
) -> None:
    """Render the balance table"""
    table = Table(
        show_header=False,
        box=None,
        padding=(0, 1),
        title="Signer Wallet Balances",
        title_style="bold bright_cyan",
        title_justify="left",
    )
    table.add_column("Asset", style="bold cyan", no_wrap=True)
    table.add_column("Balance", justify="right")
    table.add_row("Address", signer)
    table.add_row("ETH", f"{eth_balance:.6f}")
    table.add_row("USDC", f"{usdc_balance:.6f}")
    console.print(table)


def _render_summary(
    console: Console, requested: float, credited: float, final_balance: float
) -> None:
    """Render the deposit summary"""
    table = Table(
        show_header=False,
        box=box.DOUBLE,
        padding=(0, 1),
        title="Deposit Summary",
        title_style="bold bright_green",
        border_style="green",
    )
    table.add_column("Field", style="bold green", no_wrap=True)
    table.add_column("Value", justify="right")
    table.add_row("Requested", f"${requested:.2f}")
    table.add_row("Credited", f"${credited:.2f}")
    table.add_row("Final Balance", f"${final_balance:.2f}")

    if credited >= requested * 0.99:
        status = Text("✅ SUCCESS", style="bold green")
    else:
        status = Text("⚠️  PARTIAL", style="bold yellow")
    table.add_row("Status", status)

    console.print("\n")
    console.print(table)
