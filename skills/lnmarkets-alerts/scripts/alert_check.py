#!/usr/bin/env python3
"""
LN Markets Alert Monitor
Checks positions and price, returns alerts if any issues detected.
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lnm_client import get_ticker, get_account, get_all_positions

# Alert thresholds
LIQUIDATION_THRESHOLD = 10  # Alert if <10% from liquidation
LOSS_THRESHOLD = 20  # Alert if loss >20% of margin
PRICE_CHANGE_THRESHOLD = 5  # Alert if price changed >5% since last check

STATE_FILE = os.path.join(os.path.dirname(__file__), "..", ".alert_state.json")


PRICE_HISTORY_LENGTH = 5  # Track last 5 minutes


def load_state():
    """Load previous state (price history)."""
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"price_history": []}


def save_state(state):
    """Save current state."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def check_price_movement(current_price, state):
    """Check if price moved significantly over last 5 minutes."""
    alerts = []
    price_history = state.get("price_history", [])
    
    # Add current price to history
    price_history.append(current_price)
    
    # Keep only last N prices
    if len(price_history) > PRICE_HISTORY_LENGTH:
        price_history = price_history[-PRICE_HISTORY_LENGTH:]
    
    state["price_history"] = price_history
    
    # Need at least 5 data points to compare
    if len(price_history) >= PRICE_HISTORY_LENGTH:
        oldest_price = price_history[0]
        if oldest_price and oldest_price > 0:
            change_pct = ((current_price - oldest_price) / oldest_price) * 100
            if abs(change_pct) >= PRICE_CHANGE_THRESHOLD:
                direction = "📈" if change_pct > 0 else "📉"
                alerts.append(
                    f"{direction} BTC moved {change_pct:+.1f}% in 5 minutes!\n"
                    f"   ${oldest_price:,.0f} → ${current_price:,.0f}"
                )
    
    return alerts


def is_long(side: str) -> bool:
    """Check if position is long (buy)."""
    return side in ("b", "buy")


def check_positions(positions, current_price):
    """Check positions for liquidation risk and large losses."""
    alerts = []
    
    # Check isolated trades
    for trade in positions.get("isolated", []):
        side = trade.get("side", "unknown")
        quantity = trade.get("quantity", 0)
        margin = trade.get("margin", 0)
        pl = trade.get("pl", 0)
        liq_price = trade.get("liquidation", 0)
        trade_id = str(trade.get("id", "?"))[:8]
        side_str = "LONG" if is_long(side) else "SHORT"
        
        # Check liquidation distance
        if liq_price and current_price:
            if is_long(side):  # long
                liq_distance = ((current_price - liq_price) / current_price) * 100
            else:  # short
                liq_distance = ((liq_price - current_price) / current_price) * 100
            
            if liq_distance < LIQUIDATION_THRESHOLD:
                alerts.append(
                    f"🚨 LIQUIDATION RISK!\n"
                    f"   Isolated {side_str} #{trade_id}\n"
                    f"   Only {liq_distance:.1f}% from liquidation\n"
                    f"   Current: ${current_price:,.0f} | Liq: ${liq_price:,.0f}"
                )
        
        # Check large losses
        if margin > 0 and pl < 0:
            loss_pct = abs(pl) / margin * 100
            if loss_pct > LOSS_THRESHOLD:
                alerts.append(
                    f"📉 LARGE LOSS\n"
                    f"   Isolated {side_str} #{trade_id}\n"
                    f"   Down {loss_pct:.1f}% ({pl:,} sats)"
                )
    
    # Check cross position
    cross = positions.get("cross", {})
    cross_qty = cross.get("quantity", 0)
    if cross_qty != 0:
        side = cross.get("side", "unknown")
        margin = cross.get("margin", 0)
        pl = cross.get("pl", 0)
        liq_price = cross.get("liquidation", 0)
        side_str = "LONG" if is_long(side) else "SHORT"
        
        if liq_price and current_price:
            if is_long(side):
                liq_distance = ((current_price - liq_price) / current_price) * 100
            else:
                liq_distance = ((liq_price - current_price) / current_price) * 100
            
            if liq_distance < LIQUIDATION_THRESHOLD:
                alerts.append(
                    f"🚨 LIQUIDATION RISK!\n"
                    f"   Cross {side_str} position\n"
                    f"   Only {liq_distance:.1f}% from liquidation\n"
                    f"   Current: ${current_price:,.0f} | Liq: ${liq_price:,.0f}"
                )
        
        if margin > 0 and pl < 0:
            loss_pct = abs(pl) / margin * 100
            if loss_pct > LOSS_THRESHOLD:
                alerts.append(
                    f"📉 LARGE LOSS\n"
                    f"   Cross {side_str} position\n"
                    f"   Down {loss_pct:.1f}% ({pl:,} sats)"
                )
    
    return alerts


def main():
    """Run alert check and output any alerts."""
    try:
        # Load previous state
        state = load_state()
        
        # Get current data
        ticker = get_ticker()
        current_price = ticker.get("index", 0)
        
        all_alerts = []
        
        # Check price movement (also updates state with price history)
        price_alerts = check_price_movement(current_price, state)
        all_alerts.extend(price_alerts)
        
        # Check positions (requires auth)
        try:
            positions = get_all_positions()
            position_alerts = check_positions(positions, current_price)
            all_alerts.extend(position_alerts)
        except Exception as e:
            if "LNM_API" in str(e):
                pass  # No credentials, skip position check
            else:
                all_alerts.append(f"⚠️ Error checking positions: {e}")
        
        # Save current state (price history already updated)
        save_state(state)
        
        # Output alerts
        if all_alerts:
            print("🔔 LN MARKETS ALERTS\n")
            print(f"BTC: ${current_price:,.0f}\n")
            for alert in all_alerts:
                print(alert)
                print()
        else:
            # No alerts - silent
            pass
        
        # Exit code: 1 if alerts, 0 if none
        sys.exit(1 if all_alerts else 0)
        
    except Exception as e:
        print(f"❌ Alert check failed: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
