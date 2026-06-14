#!/usr/bin/env python3
"""
deploy.py — Deploy the Spelling Bee contract to GenLayer testnet.

Usage:
    python scripts/deploy.py --network testnet
    python scripts/deploy.py --network localnet

Env vars:
    PRIVATE_KEY   Deployer private key (with 0x prefix)
    NETWORK       Override: testnet | localnet
"""

import argparse
import os
import sys
import asyncio
from pathlib import Path

try:
    from genlayer import Client, Account
    from genlayer.py.types import Address
except ImportError:
    print("ERROR: genlayer-py not installed. Run: pip install genlayer-py")
    sys.exit(1)

CONTRACT_FILE = Path(__file__).parent.parent / "contracts" / "spelling_bee.py"

NETWORKS = {
    "testnet": "https://studio.genlayer.com/api",
    "localnet": "http://localhost:4000/api",
}


async def deploy(network: str, private_key: str) -> str:
    rpc_url = NETWORKS[network]
    account = Account.from_private_key(private_key)
    client = Client(endpoint=rpc_url, account=account)

    print(f"Deploying SpellingBee to {network} ({rpc_url})")
    print(f"Deployer: {account.address}")

    contract_code = CONTRACT_FILE.read_text()

    tx_hash = await client.deploy_contract(
        code=contract_code,
        constructor_args=[],
    )
    print(f"Deploy tx:  {tx_hash}")

    # Wait for finality
    receipt = await client.wait_for_transaction(tx_hash, timeout=300)
    contract_address = receipt.contract_address

    print(f"\n✅ Contract deployed!")
    print(f"   Address : {contract_address}")
    print(f"   Tx hash : {tx_hash}")
    print(f"   Block   : {receipt.block_number}")
    print(f"\nUpdate CONTRACT_ADDRESS in frontend/src/App.jsx:")
    print(f'   const CONTRACT_ADDRESS = "{contract_address}";')

    return contract_address


def main():
    parser = argparse.ArgumentParser(description="Deploy Spelling Bee contract")
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

    address = asyncio.run(deploy(args.network, private_key))
    return address


if __name__ == "__main__":
    main()
