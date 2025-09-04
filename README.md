# HyperLiquid Executor

## Usage

### Pre-requisites

Install `uv` via their official [docs](https://docs.astral.sh/uv/#installation). The one-liner is:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

> [!NOTE]  
> `uv` is highly recommended to use, other package managers are untested on this repo.

### Installation

```sh
uv sync
```

### Commands

```sh
Usage: hlexec [OPTIONS] COMMAND [ARGS]...

  HyperLiquid Executor - Python CLI

Options:
  --private-key TEXT  Private key for signing transactions
  --production        Connect to the production environment (default is
                      testnet)
  --address TEXT      This the HL account address which the Action will be
                      performed on
  --help              Show this message and exit.

Commands:
  deposit   Deposit Funds from EVM -> Core
  order     Place Limit Order
  status    Get positions and open orders for the account
  transfer  Transfer funds between vaults
  withdraw  Withdraw Funds from Core -> EVM
```

#### `status`

#### `deposit <amount>`
