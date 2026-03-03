from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from typing import Any

from .config import RedeemerConfig
from .models import RedeemablePosition, RedemptionCandidate

CONDITIONAL_TOKENS_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "collateralToken", "type": "address"},
            {"internalType": "bytes32", "name": "parentCollectionId", "type": "bytes32"},
            {"internalType": "bytes32", "name": "conditionId", "type": "bytes32"},
            {"internalType": "uint256[]", "name": "indexSets", "type": "uint256[]"},
        ],
        "name": "redeemPositions",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    }
]


class AutoRedeemer:
    def __init__(self, config: RedeemerConfig) -> None:
        try:
            from web3 import Web3  # pylint: disable=import-outside-toplevel
        except ModuleNotFoundError as exc:
            raise RuntimeError("web3 is required to run the redeemer. Install project dependencies first.") from exc

        self._web3_cls = Web3
        self.config = config
        self.w3 = Web3(Web3.HTTPProvider(config.rpc_url))
        self.wallet = self.w3.to_checksum_address(config.wallet_address)
        self.contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(config.conditional_tokens_address), abi=CONDITIONAL_TOKENS_ABI
        )

    def build_candidates(self, positions: list[RedeemablePosition]) -> list[RedemptionCandidate]:
        grouped: dict[tuple[str, str, str], list[RedeemablePosition]] = defaultdict(list)
        for position in positions:
            key = (position.condition_id, position.collateral_token, position.parent_collection_id)
            grouped[key].append(position)

        candidates: list[RedemptionCandidate] = []
        for (condition_id, collateral_token, parent_collection_id), grouped_positions in grouped.items():
            sorted_positions = sorted(grouped_positions, key=lambda p: p.index_set)
            candidates.append(
                RedemptionCandidate(
                    condition_id=condition_id,
                    collateral_token=collateral_token,
                    parent_collection_id=parent_collection_id,
                    index_sets=[p.index_set for p in sorted_positions],
                    total_balance_wei=sum(p.token_balance_wei for p in sorted_positions),
                )
            )

        return sorted(candidates, key=lambda c: c.total_balance_wei, reverse=True)

    def redeem_all(self, candidates: list[RedemptionCandidate], dry_run: bool = True) -> list[dict[str, Any]]:
        tx_results: list[dict[str, Any]] = []
        nonce = self.w3.eth.get_transaction_count(self.wallet)

        for candidate in candidates:
            tx = self.contract.functions.redeemPositions(
                self.w3.to_checksum_address(candidate.collateral_token),
                self._web3_cls.to_bytes(hexstr=candidate.parent_collection_id),
                self._web3_cls.to_bytes(hexstr=candidate.condition_id),
                candidate.index_sets,
            ).build_transaction(
                {
                    "from": self.wallet,
                    "nonce": nonce,
                    "chainId": self.config.chain_id,
                }
            )
            tx["gas"] = int(tx.get("gas", 300_000) * self.config.gas_multiplier)
            tx["maxFeePerGas"] = self.w3.eth.gas_price
            tx["maxPriorityFeePerGas"] = int(self.w3.eth.gas_price * 0.1)

            result = {
                "candidate": asdict(candidate),
                "nonce": nonce,
                "dry_run": dry_run,
            }

            if dry_run:
                result["tx"] = tx
                tx_results.append(result)
                nonce += 1
                continue

            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.config.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            result["tx_hash"] = tx_hash.hex()
            result["status"] = receipt.status
            tx_results.append(result)
            nonce += 1

        return tx_results
