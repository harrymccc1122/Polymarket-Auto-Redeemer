from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv(_path=None):
        return False



@dataclass(slots=True)
class RedeemerConfig:
    rpc_url: str
    private_key: str
    wallet_address: str
    conditional_tokens_address: str
    chain_id: int = 137
    gas_multiplier: float = 1.15
    max_positions_per_tx: int = 8

    @classmethod
    def from_env(cls, env_file: str | None = None) -> "RedeemerConfig":
        if env_file:
            load_dotenv(env_file)
        else:
            default_env = Path(".env")
            if default_env.exists():
                load_dotenv(default_env)

        required = {
            "rpc_url": os.getenv("POLYMARKET_RPC_URL"),
            "private_key": os.getenv("POLYMARKET_PRIVATE_KEY"),
            "wallet_address": os.getenv("POLYMARKET_WALLET_ADDRESS"),
            "conditional_tokens_address": os.getenv("POLYMARKET_CONDITIONAL_TOKENS_ADDRESS"),
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            env_names = ", ".join(name.upper() for name in missing)
            raise ValueError(f"Missing required configuration: {env_names}")

        return cls(
            rpc_url=required["rpc_url"] or "",
            private_key=required["private_key"] or "",
            wallet_address=required["wallet_address"] or "",
            conditional_tokens_address=required["conditional_tokens_address"] or "",
            chain_id=int(os.getenv("POLYMARKET_CHAIN_ID", "137")),
            gas_multiplier=float(os.getenv("POLYMARKET_GAS_MULTIPLIER", "1.15")),
            max_positions_per_tx=int(os.getenv("POLYMARKET_MAX_POSITIONS_PER_TX", "8")),
        )
