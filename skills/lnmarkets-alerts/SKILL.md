---
name: lnmarkets-alerts
description: Monitor Bitcoin price and LN Markets trading positions. Use for BTC price alerts (thresholds, % moves), checking open positions, PnL tracking, liquidation warnings, and account balance. Triggers on queries about Bitcoin price, trading positions, LN Markets account status, or crypto alerts.
---

# LN Markets Alerts

Monitor BTC price and LN Markets positions via the v3 API.

## Setup

Set these environment variables (or pass to scripts):

```
LNM_API_KEY=your_api_key
LNM_API_SECRET=your_api_secret  
LNM_API_PASSPHRASE=your_passphrase
```

## Scripts

All scripts are in the `scripts/` directory.

### check_price.py
Get current BTC/USD price from LN Markets (no auth required).

```bash
python3 scripts/check_price.py
```

Output: Index price, last trade price, funding rate.

### check_account.py
Get account balance and info (requires auth).

```bash
LNM_API_KEY=... LNM_API_SECRET=... LNM_API_PASSPHRASE=... python3 scripts/check_account.py
```

Output: Username, balance in sats/BTC, synthetic USD balance.

### check_positions.py
List all open futures positions (requires auth).

```bash
# Show all positions
python3 scripts/check_positions.py

# Show only alerts (liquidation/loss warnings)
python3 scripts/check_positions.py --alerts
```

Output includes:
- Position type (isolated/cross), side (long/short)
- Entry price, quantity, margin
- Current PnL
- Liquidation price and distance

**Alerts triggered when:**
- Position <10% from liquidation
- Unrealized loss >20% of margin

## Usage Examples

| User says | Action |
|-----------|--------|
| "What's BTC at?" | Run `check_price.py` |
| "Check my positions" | Run `check_positions.py` |
| "Am I at risk?" | Run `check_positions.py --alerts` |
| "What's my balance?" | Run `check_account.py` |

## API Client

`scripts/lnm_client.py` provides reusable functions:

```python
from lnm_client import get_ticker, get_account, get_all_positions

# Public (no auth)
ticker = get_ticker()  # BTC price

# Authenticated
account = get_account()  # Balance, username
positions = get_all_positions()  # Running trades + cross position
```

## v3 API Notes

- Base URL: `https://api.lnmarkets.com/v3`
- Auth signature uses **lowercase** method: `timestamp + method.lower() + path + data`
- Headers are lowercase: `lnm-access-key`, `lnm-access-signature`, etc.
- GET params include `?` prefix in signature data
