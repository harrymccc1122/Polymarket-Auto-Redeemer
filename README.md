# Polymarket Auto Redeemer

A production-ready starter bot to automatically redeem resolved Polymarket positions from your wallet.

## What it does

- Loads your wallet + contract config from environment variables.
- Fetches redeemable positions from either:
  - A GraphQL endpoint (`--graphql-endpoint`) that exposes `redeemablePositions(wallet)`.
  - A local JSON file (`--positions-file`) for testing.
- Groups positions per condition and generates `redeemPositions` transactions.
- Supports `--dry-run` mode (default) so you can inspect transactions before broadcasting.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Configuration

Copy `.env.example` to `.env` and fill values:

```bash
cp .env.example .env
```

Required:

- `POLYMARKET_RPC_URL`
- `POLYMARKET_PRIVATE_KEY`
- `POLYMARKET_WALLET_ADDRESS`
- `POLYMARKET_CONDITIONAL_TOKENS_ADDRESS`

Optional:

- `POLYMARKET_CHAIN_ID` (default `137`)
- `POLYMARKET_GAS_MULTIPLIER` (default `1.15`)
- `POLYMARKET_MAX_POSITIONS_PER_TX` (reserved for future batching)

## Usage

### 1) Safe dry-run with local sample positions

```bash
polymarket-auto-redeemer run --positions-file sample_positions.json --dry-run
```

### 2) Live mode via GraphQL source

```bash
polymarket-auto-redeemer run --graphql-endpoint https://your-indexer/graphql --dry-run
```

When ready, broadcast real transactions:

```bash
polymarket-auto-redeemer run --graphql-endpoint https://your-indexer/graphql --dry-run false
```

## Position payload schema

Both JSON file rows and GraphQL rows must include:

```json
{
  "conditionId": "0x...32-byte-hex...",
  "collateralToken": "0x...address...",
  "parentCollectionId": "0x...32-byte-hex...",
  "indexSet": 1,
  "tokenBalanceWei": "1000000000000000000"
}
```

## Security notes

- Keep your private key in a dedicated hot wallet with only required funds.
- Start with `--dry-run` and verify transaction data before real execution.
- Consider adding allowlists for collateral tokens and minimum balance thresholds before production deployment.
