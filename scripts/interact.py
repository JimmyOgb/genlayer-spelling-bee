#!/usr/bin/env python3
"""
interact.py — Interact with a deployed Spelling Bee contract.

Usage:
    python scripts/interact.py --action get_puzzle
    python scripts/interact.py --action submit_word --word "crane"
    python scripts/interact.py --action leaderboard
    python scripts/interact.py --action stats

Env vars:
    PRIVATE_KEY        Caller private key
    CONTRACT_ADDRESS   Deployed contract address
    NETWORK            testnet | localnet
"""

import argparse
import asyncio
import json
import os
import sys

try:
    from genlayer import Client, Account
except ImportError:
    print("ERROR: genlayer-py not installed. Run: pip install genlayer-py")
    sys.exit(1)

NETWORKS = {
    "testnet": "https://studio.genlayer.com/api",
    "localnet": "http://localhost:4000/api",
}


async def run(action: str, word: str | None, network: str, private_key: str, contract_address: str):
    rpc_url = NETWORKS[network]
    account = Account.from_private_key(private_key)
    client = Client(endpoint=rpc_url, account=account)

    print(f"Contract : {contract_address}")
    print(f"Caller   : {account.address}")
    print(f"Network  : {network}\n")

    if action == "get_puzzle":
        result = await client.call_contract(
            address=contract_address,
            function="get_current_puzzle",
            args=[],
        )
        print("=== Current Puzzle ===")
        print(json.dumps(result, indent=2))

    elif action == "submit_word":
        if not word:
            print("ERROR: --word required for submit_word action")
            sys.exit(1)

        print(f"Submitting word: '{word}'")
        tx = await client.write_contract(
            address=contract_address,
            function="submit_word",
            args=[word],
        )
        print(f"Tx hash: {tx}")
        receipt = await client.wait_for_transaction(tx, timeout=300)
        print("\n=== Result ===")
        print(json.dumps(receipt.result, indent=2))

    elif action == "leaderboard":
        result = await client.call_contract(
            address=contract_address,
            function="get_leaderboard",
            args=[10],
        )
        print("=== Leaderboard (Top 10) ===")
        for i, entry in enumerate(result, 1):
            print(f"{i:2}. {entry['address']} | {entry['total_points']} pts | {entry['rank_title']}")

    elif action == "stats":
        result = await client.call_contract(
            address=contract_address,
            function="get_game_stats",
            args=[],
        )
        print("=== Game Stats ===")
        print(json.dumps(result, indent=2))

    elif action == "my_score":
        result = await client.call_contract(
            address=contract_address,
            function="get_player_score",
            args=[account.address],
        )
        print(f"=== Score for {account.address} ===")
        print(json.dumps(result, indent=2))

    elif action == "advance_round":
        print("Advancing to next round…")
        tx = await client.write_contract(
            address=contract_address,
            function="advance_round",
            args=[],
        )
        receipt = await client.wait_for_transaction(tx, timeout=300)
        print("=== New Round ===")
        print(json.dumps(receipt.result, indent=2))

    else:
        print(f"Unknown action: {action}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Interact with Spelling Bee contract")
    parser.add_argument(
        "--action",
        required=True,
        choices=["get_puzzle", "submit_word", "leaderboard", "stats", "my_score", "advance_round"],
    )
    parser.add_argument("--word", default=None)
    parser.add_argument(
        "--network",
        choices=["testnet", "localnet"],
        default=os.getenv("NETWORK", "testnet"),
    )
    args = parser.parse_args()

    private_key = os.getenv("PRIVATE_KEY")
    if not private_key:
        print("ERROR: Set PRIVATE_KEY environment variable.")
        sys.exit(1)

    contract_address = os.getenv("CONTRACT_ADDRESS", "0x63Bfa1201F0b4e95bc9f7f1473c8cB57d2afa0Ac")

    asyncio.run(
        run(args.action, args.word, args.network, private_key, contract_address)
    )


if __name__ == "__main__":
    main()
