#!/usr/bin/env python3
"""Check LN Markets account balance and info."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lnm_client import get_account

def sats_to_btc(sats: int) -> float:
    """Convert satoshis to BTC."""
    return sats / 100_000_000

def main():
    try:
        account = get_account()
        
        balance = account.get("balance", 0)
        username = account.get("username", "N/A")
        
        print(f"💰 LN Markets Account")
        print(f"   User: {username}")
        print(f"   Balance: {balance:,} sats ({sats_to_btc(balance):.8f} BTC)")
        
        # Show additional fields if available
        if "syntheticUsdBalance" in account:
            susd = account["syntheticUsdBalance"]
            print(f"   Synthetic USD: ${susd/100:,.2f}")
        
        if "linkingpublickey" in account:
            pk = account["linkingpublickey"][:16] + "..."
            print(f"   Linking Key: {pk}")
        
    except Exception as e:
        print(f"❌ Error fetching account: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
