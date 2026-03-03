from polymarket_auto_redeemer.config import RedeemerConfig
from polymarket_auto_redeemer.models import RedeemablePosition
from polymarket_auto_redeemer.redeemer import AutoRedeemer


class DummyEth:
    gas_price = 100

    def get_transaction_count(self, _wallet):
        return 1


class DummyW3:
    eth = DummyEth()


def test_build_candidates_groups_by_condition_and_parent(monkeypatch):
    config = RedeemerConfig(
        rpc_url="http://localhost:8545",
        private_key="0xabc",
        wallet_address="0x0000000000000000000000000000000000000001",
        conditional_tokens_address="0x0000000000000000000000000000000000000002",
    )

    class FakeRedeemer(AutoRedeemer):
        def __init__(self, cfg):
            self.config = cfg

    redeemer = FakeRedeemer(config)

    positions = [
        RedeemablePosition(
            condition_id="0x1".ljust(66, "0"),
            collateral_token="0x0000000000000000000000000000000000000003",
            parent_collection_id="0x" + "0" * 64,
            index_set=2,
            token_balance_wei=4,
        ),
        RedeemablePosition(
            condition_id="0x1".ljust(66, "0"),
            collateral_token="0x0000000000000000000000000000000000000003",
            parent_collection_id="0x" + "0" * 64,
            index_set=1,
            token_balance_wei=6,
        ),
    ]

    candidates = redeemer.build_candidates(positions)

    assert len(candidates) == 1
    assert candidates[0].index_sets == [1, 2]
    assert candidates[0].total_balance_wei == 10
