#!/usr/bin/env python3
"""Check LN Markets open positions with optional alerts."""

import sys
import os
import argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lnm_client import get_all_positions, get_ticker

def sats_to_btc(sats: int) -> float:
    """Convert satoshis to BTC."""
    return sats / 100_000_000

def format_isolated_trade(trade: dict, current_price: float) -> str:
    """Format an isolated margin trade for display."""
    side = trade.get("side", "unknown")
    quantity = trade.get("quantity", 0)
    entry = trade.get("price", 0)
    margin = trade.get("margin", 0)
    pl = trade.get("pl", 0)
    liq_price = trade.get("liquidation", 0)
    trade_id = trade.get("id", "?")[:8]
    
    side_emoji = "🟢" if side == "b" else "🔴"
    side_str = "LONG" if side == "b" else "SHORT"
    
    # Calculate distance to liquidation
    liq_distance = None
    if liq_price and current_price:
        if side == "b":  # long
            liq_distance = ((current_price - liq_price) / current_price) * 100
        else:  # short
            liq_distance = ((liq_price - current_price) / current_price) * 100
    
    lines = [
        f"{side_emoji} ISOLATED {side_str} #{trade_id}",
        f"   Qty: {quantity:,} contracts @ ${entry:,.0f}",
        f"   Margin: {margin:,} sats | PnL: {pl:+,} sats",
        f"   Liquidation: ${liq_price:,.0f}",
    ]
    
    if liq_distance is not None:
        lines[-1] += f" ({liq_distance:.1f}% away)"
    
    return "\n".join(lines)

def format_cross_position(pos: dict, current_price: float) -> str:
    """Format cross margin position for display."""
    quantity = pos.get("quantity", 0)
    if quantity == 0:
        return None  # No cross position
    
    side = pos.get("side", "unknown")
    entry = pos.get("price", 0)
    margin = pos.get("margin", 0)
    pl = pos.get("pl", 0)
    liq_price = pos.get("liquidation", 0)
    
    side_emoji = "🟢" if side == "b" else "🔴"
    side_str = "LONG" if side == "b" else "SHORT"
    
    # Calculate distance to liquidation
    liq_distance = None
    if liq_price and current_price:
        if side == "b":  # long
            liq_distance = ((current_price - liq_price) / current_price) * 100
        else:  # short
            liq_distance = ((liq_price - current_price) / current_price) * 100
    
    lines = [
        f"{side_emoji} CROSS {side_str}",
        f"   Qty: {quantity:,} contracts @ ${entry:,.0f}",
        f"   Margin: {margin:,} sats | PnL: {pl:+,} sats",
        f"   Liquidation: ${liq_price:,.0f}",
    ]
    
    if liq_distance is not None:
        lines[-1] += f" ({liq_distance:.1f}% away)"
    
    return "\n".join(lines)

def check_alerts(isolated: list, cross: dict, current_price: float) -> list:
    """Check for risky positions."""
    alerts = []
    
    # Check isolated trades
    for trade in isolated:
        side = trade.get("side", "unknown")
        quantity = trade.get("quantity", 0)
        margin = trade.get("margin", 0)
        pl = trade.get("pl", 0)
        liq_price = trade.get("liquidation", 0)
        trade_id = trade.get("id", "?")[:8]
        
        if liq_price and current_price:
            if side == "b":
                liq_distance = ((current_price - liq_price) / current_price) * 100
            else:
                liq_distance = ((liq_price - current_price) / current_price) * 100
            
            if liq_distance < 10:
                side_str = "LONG" if side == "b" else "SHORT"
                alerts.append(f"⚠️ LIQUIDATION WARNING: Isolated {side_str} #{trade_id} only {liq_distance:.1f}% from liquidation!")
        
        if margin > 0 and pl < 0:
            loss_pct = abs(pl) / margin * 100
            if loss_pct > 20:
                side_str = "LONG" if side == "b" else "SHORT"
                alerts.append(f"📉 LOSS: Isolated {side_str} #{trade_id} down {loss_pct:.1f}% ({pl:,} sats)")
    
    # Check cross position
    cross_qty = cross.get("quantity", 0)
    if cross_qty != 0:
        side = cross.get("side", "unknown")
        margin = cross.get("margin", 0)
        pl = cross.get("pl", 0)
        liq_price = cross.get("liquidation", 0)
        
        if liq_price and current_price:
            if side == "b":
                liq_distance = ((current_price - liq_price) / current_price) * 100
            else:
                liq_distance = ((liq_price - current_price) / current_price) * 100
            
            if liq_distance < 10:
                side_str = "LONG" if side == "b" else "SHORT"
                alerts.append(f"⚠️ LIQUIDATION WARNING: Cross {side_str} only {liq_distance:.1f}% from liquidation!")
        
        if margin > 0 and pl < 0:
            loss_pct = abs(pl) / margin * 100
            if loss_pct > 20:
                side_str = "LONG" if side == "b" else "SHORT"
                alerts.append(f"📉 LOSS: Cross {side_str} down {loss_pct:.1f}% ({pl:,} sats)")
    
    return alerts

def main():
    parser = argparse.ArgumentParser(description="Check LN Markets positions")
    parser.add_argument("--alerts", action="store_true", help="Show only alerts for risky positions")
    args = parser.parse_args()
    
    try:
        positions = get_all_positions()
        ticker = get_ticker()
        current_price = ticker.get("index", 0)
        
        isolated = positions.get("isolated", [])
        cross = positions.get("cross", {})
        
        # Filter to only running/open trades
        isolated = [t for t in isolated if t.get("running", False)]
        
        has_cross = cross.get("quantity", 0) != 0
        total_positions = len(isolated) + (1 if has_cross else 0)
        
        if total_positions == 0:
            print("📭 No open positions")
            return
        
        if args.alerts:
            alerts = check_alerts(isolated, cross, current_price)
            if alerts:
                print("🚨 POSITION ALERTS\n")
                for alert in alerts:
                    print(alert)
            else:
                print("✅ All positions healthy - no alerts")
        else:
            print(f"📊 Open Positions ({total_positions} total)")
            print(f"   Current BTC: ${current_price:,.0f}\n")
            
            total_pl = 0
            total_margin = 0
            
            for trade in isolated:
                print(format_isolated_trade(trade, current_price))
                print()
                total_pl += trade.get("pl", 0)
                total_margin += trade.get("margin", 0)
            
            if has_cross:
                cross_str = format_cross_position(cross, current_price)
                if cross_str:
                    print(cross_str)
                    print()
                    total_pl += cross.get("pl", 0)
                    total_margin += cross.get("margin", 0)
            
            print(f"📈 TOTAL")
            print(f"   Margin: {total_margin:,} sats ({sats_to_btc(total_margin):.8f} BTC)")
            print(f"   PnL: {total_pl:+,} sats ({sats_to_btc(total_pl):.8f} BTC)")
        
    except Exception as e:
        print(f"❌ Error fetching positions: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
