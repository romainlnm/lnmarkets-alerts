# LN Markets Alerts

Monitor your BTC positions and get alerts for liquidation risk, losses, and price movements via the [LN Markets](https://lnmarkets.com) v3 API.

> 🦞 **OpenClaw Skill** — Works standalone or as an [OpenClaw](https://github.com/openclaw/openclaw) AI assistant skill.

## Alert Preview

```
🔔 LN MARKETS ALERTS

BTC: $102,450

🚨 LIQUIDATION RISK!
   Isolated LONG #a1f11a32
   Only 2.8% from liquidation
   Current: $102,450 | Liq: $99,580

📉 LARGE LOSS
   Isolated SHORT #b2d6c918
   Down 34.2% (-4,521 sats)

📈 BTC moved +5.3% in 5 minutes!
   $97,280 → $102,450

💀 POSITION CLOSED/LIQUIDATED!
   Trade #c3e7d029 is gone
```

## Features

- 📈 **BTC Price** — Real-time index price from LN Markets
- 💰 **Account Balance** — Check your sats balance
- 📊 **Position Monitoring** — Track isolated & cross margin trades
- ⚠️ **Alerts** — Warnings for liquidation risk (<10%) and large losses (>20%)

## Setup

### 1. Generate LN Markets API Key (Read-Only)

1. Go to [LN Markets](https://lnmarkets.com) and log in
2. Navigate to **Profile** → **API** (or directly: https://app.lnmarkets.com/user/api)
3. Click **Create new API key**
4. Give it a name (e.g., `alerts-readonly`)
5. **Important:** Select only **read** permissions:
   - ✅ `account:read`
   - ✅ `futures:read`
   - ❌ Leave write/trade permissions unchecked
6. Click **Create**
7. Save the three values shown:
   - **Key** (starts with a random string)
   - **Secret** (long base64 string)
   - **Passphrase** (short string)

> ⚠️ **Never share your API credentials!** Read-only keys can't make trades, but can see your balance and positions.

### 2. Configure Credentials

Create a `.env` file in the skill directory:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```
LNM_API_KEY=your_api_key_here
LNM_API_SECRET=your_api_secret_here
LNM_API_PASSPHRASE=your_passphrase_here
```

### 3. Run

```bash
# Check BTC price (no auth required)
./scripts/run.sh check_price.py

# Check account balance
./scripts/run.sh check_account.py

# Check open positions
./scripts/run.sh check_positions.py

# Check for alerts (liquidation/loss warnings)
./scripts/run.sh check_positions.py --alerts
```

Or run directly with environment variables:

```bash
LNM_API_KEY=... LNM_API_SECRET=... LNM_API_PASSPHRASE=... python3 scripts/check_account.py
```

## Scripts

| Script | Auth Required | Description |
|--------|---------------|-------------|
| `check_price.py` | ❌ | Get current BTC/USD price |
| `check_account.py` | ✅ | Show account balance |
| `check_positions.py` | ✅ | List all open positions |
| `check_positions.py --alerts` | ✅ | Show only risk alerts |

## Alert Thresholds

- **Liquidation warning**: Position is <10% away from liquidation price
- **Loss warning**: Unrealized loss exceeds 20% of margin

## API Client

You can import the client in your own scripts:

```python
from scripts.lnm_client import get_ticker, get_account, get_all_positions

# Public endpoint (no auth)
ticker = get_ticker()
print(f"BTC: ${ticker['index']:,}")

# Authenticated endpoints
account = get_account()
print(f"Balance: {account['balance']:,} sats")

positions = get_all_positions()
print(f"Running trades: {len(positions['isolated'])}")
```

## Requirements

- Python 3.8+
- No external dependencies (uses only stdlib)

## Security Notes

- Always use **read-only** API keys for monitoring
- Never commit `.env` files (already in `.gitignore`)
- Rotate your API keys periodically
- The v3 API uses HMAC-SHA256 signatures with lowercase method names

## License

MIT

## Links

- [LN Markets](https://lnmarkets.com)
- [LN Markets API Docs](https://docs.lnmarkets.com/api)
- [LN Markets Python SDK](https://github.com/ln-markets/sdk-python)
