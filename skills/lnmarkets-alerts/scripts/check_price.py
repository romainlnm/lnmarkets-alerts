#!/usr/bin/env python3
"""Check current BTC/USD price from LN Markets."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lnm_client import get_ticker

def main():
    try:
        ticker = get_ticker()
        
        index = ticker.get("index", "N/A")
        last_price = ticker.get("lastPrice", "N/A")
        bid = ticker.get("bid", "N/A")
        offer = ticker.get("offer", "N/A")
        funding = ticker.get("fundingRate", "N/A")
        
        print(f"📈 BTC/USD (LN Markets)")
        print(f"   Index: ${index:,.0f}" if isinstance(index, (int, float)) else f"   Index: {index}")
        print(f"   Last:  ${last_price:,.0f}" if isinstance(last_price, (int, float)) else f"   Last: {last_price}")
        print(f"   Bid:   ${bid:,.0f}" if isinstance(bid, (int, float)) else f"   Bid: {bid}")
        print(f"   Offer: ${offer:,.0f}" if isinstance(offer, (int, float)) else f"   Offer: {offer}")
        if isinstance(funding, (int, float)):
            print(f"   Funding: {funding:.4%}")
        
    except Exception as e:
        print(f"❌ Error fetching price: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
