# HyperLiquid Executor

## Usage

### Pre-requisites

Install `uv` via their official [docs](https://docs.astral.sh/uv/#installation). The one-liner is:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

> [!IMPORTANT]  
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

> [!NOTE]  
> This command is the quick dashboard for the HL Account address (provided by `--address` option or `ACCOUNT_ADDRESS` environment variable).

```shell
$ uv run hlexec status
Session Info                                             
 Environment  testnet                                    
 HL Account   0xb764428a29EAEbe8e2301F5924746F818b331F5A 
 Signer       0x57FbAe717f5712C3Bd612f34482832c86D9b17f2 

                                              Positions                                              
╭──────┬─────────┬─────┬──────────┬───────────┬────────────┬────────┬─────────────────┬─────────────╮
│ Coin │ Size    │ Lev │ Entry Px │ Value     │ Unreal PnL │    ROE │ Liq Px          │ Margin Used │
├──────┼─────────┼─────┼──────────┼───────────┼────────────┼────────┼─────────────────┼─────────────┤
│ ETH  │ 0.1     │ 10x │ 4312.0   │ 430.39    │      -0.81 │ -1.88% │ 4002.1844693878 │ 38.175922   │
│ DOGE │ -5175.0 │ 10x │ 0.21572  │ 1099.4805 │    16.8705 │ 15.11% │ 0.3626983345    │ 109.94805   │
╰──────┴─────────┴─────┴──────────┴───────────┴────────────┴────────┴─────────────────┴─────────────╯

                                                 Open Orders                                                 
╭──────┬──────┬──────────┬─────────┬─────────────┬────────────────────────────────────┬─────────────────────╮
│ Coin │ Side │ Limit Px │ Size    │         OID │ Client OID                         │ Time                │
├──────┼──────┼──────────┼─────────┼─────────────┼────────────────────────────────────┼─────────────────────┤
│ DOGE │ Sell │ 0.3      │ 8360.0  │ 38709445951 │ -                                  │ 2025-09-04 11:08:37 │
│ BTC  │ Sell │ 130000.0 │ 0.02196 │ 38707223032 │ -                                  │ 2025-09-04 10:56:32 │
│ ETH  │ Buy  │ 2000.0   │ 0.01    │ 38684898004 │ 0x019913a9b0637000bf85feb8fa139da6 │ 2025-09-04 08:55:00 │
│ ETH  │ Buy  │ 2000.0   │ 0.01    │ 38684843740 │ 0x019913a9b0637000bf85feb8fa139da5 │ 2025-09-04 08:54:42 │
╰──────┴──────┴──────────┴─────────┴─────────────┴────────────────────────────────────┴─────────────────────╯
```

#### `deposit <amount>`

> [!NOTE]  
> This will transfer USDC from the signer's Arbitrum Accont to the provided HL Account Address (provided by `--address` option or `ACCOUNT_ADDRESS` environment variable).

```sh
$ uv run hlexec deposit 5
Session Info                                             
 Environment  testnet                                    
 HL Account   0xb764428a29EAEbe8e2301F5924746F818b331F5A 
 Signer       0x57FbAe717f5712C3Bd612f34482832c86D9b17f2 
Signer Wallet Balances                               
 Address  0x57FbAe717f5712C3Bd612f34482832c86D9b17f2 
 ETH                                        0.299963 
 USDC                                      87.000000 

💰 Initial HL balance: $5.00
📤 Depositing: 5.000000 USDC

✅ Transaction sent: d2e138d06d6082c534f67aa9622d969d218d1fc1fb9ea6fb992df2fe74ad756a
✅ Transaction confirmed in block 190866656
⠏ Waiting for confirmation...

⏳ Waiting for HyperLiquid credit...

✅ HyperLiquid account credited: $5.00
⠏ Checking HyperLiquid balance...

🔄 Transferring from signer 0x57FbAe717f5712C3Bd612f34482832c86D9b17f2 to target 0xb764428a29EAEbe8e2301F5924746F818b331F5A...
✅ Internal transfer initiated
⚠️  Transfer amount mismatch. Expected: $5.00, Got: $4.90


       Deposit Summary        
╔═══════════════╦════════════╗
║ Requested     ║      $5.00 ║
║ Credited      ║    $909.37 ║
║ Final Balance ║    $914.37 ║
║ Status        ║ ✅ SUCCESS ║
╚═══════════════╩════════════╝
```

#### `withdraw`

#### `transfer`


#### `order new`

#### `order modify`

#### `order cancel`

## Testing