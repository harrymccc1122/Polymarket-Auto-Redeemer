from __future__ import annotations

import json

import typer

from .config import RedeemerConfig
from .position_sources import GraphQLPositionSource, JsonPositionSource, PositionSource
from .redeemer import AutoRedeemer

app = typer.Typer(help="Automated redeemer for resolved Polymarket positions")


@app.command()
def run(
    dry_run: bool = typer.Option(True, help="Build transactions but don't broadcast"),
    env_file: str | None = typer.Option(None, help="Path to .env file"),
    graphql_endpoint: str | None = typer.Option(
        None,
        help="GraphQL endpoint that returns redeemablePositions(wallet)",
    ),
    positions_file: str | None = typer.Option(
        None,
        help="JSON file with redeemable positions (for local testing)",
    ),
) -> None:
    """Redeem all detected positions."""

    if not graphql_endpoint and not positions_file:
        raise typer.BadParameter("Provide either --graphql-endpoint or --positions-file")

    config = RedeemerConfig.from_env(env_file=env_file)
    redeemer = AutoRedeemer(config)
    source: PositionSource
    if positions_file:
        source = JsonPositionSource(positions_file)
    else:
        source = GraphQLPositionSource(graphql_endpoint or "")

    positions = source.fetch_positions(config.wallet_address)
    candidates = redeemer.build_candidates(positions)
    if not candidates:
        typer.echo("No redeemable positions found.")
        return

    typer.echo(f"Found {len(candidates)} redeemable condition groups.")
    results = redeemer.redeem_all(candidates, dry_run=dry_run)
    typer.echo(json.dumps(results, indent=2))


if __name__ == "__main__":
    app()
