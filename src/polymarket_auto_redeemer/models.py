from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RedeemablePosition:
    condition_id: str
    collateral_token: str
    parent_collection_id: str
    index_set: int
    token_balance_wei: int


@dataclass(slots=True)
class RedemptionCandidate:
    condition_id: str
    collateral_token: str
    parent_collection_id: str
    index_sets: list[int]
    total_balance_wei: int
