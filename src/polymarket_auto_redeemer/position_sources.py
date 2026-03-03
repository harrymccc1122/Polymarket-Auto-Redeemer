from __future__ import annotations

import json
from abc import ABC, abstractmethod
from collections.abc import Iterable
from pathlib import Path


from .models import RedeemablePosition


class PositionSource(ABC):
    @abstractmethod
    def fetch_positions(self, wallet_address: str) -> list[RedeemablePosition]:
        raise NotImplementedError


class JsonPositionSource(PositionSource):
    """Reads precomputed redeemable positions from JSON file."""

    def __init__(self, path: str) -> None:
        self.path = Path(path)

    def fetch_positions(self, wallet_address: str) -> list[RedeemablePosition]:
        data = json.loads(self.path.read_text())
        return _parse_positions(data)


class GraphQLPositionSource(PositionSource):
    """Loads redeemable positions from a GraphQL endpoint.

    Expected response fields:
      - conditionId
      - collateralToken
      - parentCollectionId
      - indexSet (int)
      - tokenBalanceWei (int-like string)
    """

    def __init__(self, endpoint: str, timeout_seconds: int = 20) -> None:
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds

    def fetch_positions(self, wallet_address: str) -> list[RedeemablePosition]:
        query = """
        query RedeemablePositions($wallet: String!) {
          redeemablePositions(wallet: $wallet) {
            conditionId
            collateralToken
            parentCollectionId
            indexSet
            tokenBalanceWei
          }
        }
        """
        try:
            import requests  # pylint: disable=import-outside-toplevel
        except ModuleNotFoundError as exc:
            raise RuntimeError("requests is required for GraphQL position sourcing") from exc

        response = requests.post(
            self.endpoint,
            json={"query": query, "variables": {"wallet": wallet_address.lower()}},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()

        if payload.get("errors"):
            raise ValueError(f"GraphQL errors: {payload['errors']}")

        rows = payload.get("data", {}).get("redeemablePositions", [])
        return _parse_positions(rows)


def _parse_positions(rows: Iterable[dict]) -> list[RedeemablePosition]:
    positions: list[RedeemablePosition] = []
    for row in rows:
        balance = int(row["tokenBalanceWei"])
        if balance <= 0:
            continue
        positions.append(
            RedeemablePosition(
                condition_id=row["conditionId"],
                collateral_token=row["collateralToken"],
                parent_collection_id=row.get("parentCollectionId", "0x" + "0" * 64),
                index_set=int(row["indexSet"]),
                token_balance_wei=balance,
            )
        )
    return positions
