from polymarket_auto_redeemer.position_sources import _parse_positions


def test_parse_positions_skips_empty_balances():
    rows = [
        {
            "conditionId": "0x" + "a" * 64,
            "collateralToken": "0x0000000000000000000000000000000000000001",
            "parentCollectionId": "0x" + "0" * 64,
            "indexSet": 1,
            "tokenBalanceWei": "0",
        },
        {
            "conditionId": "0x" + "b" * 64,
            "collateralToken": "0x0000000000000000000000000000000000000001",
            "parentCollectionId": "0x" + "0" * 64,
            "indexSet": 2,
            "tokenBalanceWei": "5",
        },
    ]

    positions = _parse_positions(rows)
    assert len(positions) == 1
    assert positions[0].index_set == 2
