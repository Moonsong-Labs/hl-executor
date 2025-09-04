# HyperLiquid Executor


## Usage

### Pre-requisites

### Installation

### Commands

```sh
# Deposit USDC from EVM (Arbitrum) to HL core
hlexec deposit \
  --amount 10.5 \
  [--production] \
  [--rpc-url https://arb1.arbitrum.io/rpc] \
  [--usdc-address 0x...] \
  [--bridge-address 0x...]
```

#### `Status` 

## Type Checking

This project uses mypy for static type checking. Configuration lives in `pyproject.toml` under `[tool.mypy]` with a `src/` layout (`mypy_path = "src"` and `files = ["hl_executor"]`).

Run mypy using your preferred workflow:

- With uv (after syncing dev deps):
  - `uv run mypy -p hl_executor`
  - or `uv run python -m mypy -p hl_executor`

- With an active virtualenv where mypy is installed:
  - `python -m mypy -p hl_executor`
  - or `mypy -p hl_executor`

Notes:
- Third‑party libs without type hints (e.g., `hyperliquid`, `web3`, `eth_account`) are silenced in config with per‑module ignores.
- A `py.typed` marker is included so downstream users get type information when this package is distributed.
