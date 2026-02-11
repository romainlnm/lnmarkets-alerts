# LN Markets API Reference

Base URL: `https://api.lnmarkets.com/v2`

## Authentication

All authenticated requests require headers:
- `LNM-ACCESS-KEY`: API key
- `LNM-ACCESS-SIGNATURE`: HMAC SHA256 signature (base64)
- `LNM-ACCESS-PASSPHRASE`: API passphrase
- `LNM-ACCESS-TIMESTAMP`: Unix timestamp in milliseconds

Signature = HMAC-SHA256(secret, timestamp + method + path + params)

## Key Endpoints

### Public (No Auth)

- `GET /futures/ticker` - BTC/USD price (index, lastPrice)

### Authenticated

- `GET /user` - Account info (balance in sats)
- `GET /futures?type=running` - Open positions

### Position Object

```json
{
  "id": "position_id",
  "side": "b" | "s",      // b=long, s=short
  "quantity": 1000,        // contracts (1 contract = $1)
  "price": 95000,          // entry price
  "margin": 100000,        // margin in sats
  "pl": -5000,             // unrealized PnL in sats
  "liquidation": 85000     // liquidation price
}
```

## Rate Limits

- Authenticated: 1 request/second
- Public: 30 requests/minute

## Docs

Full documentation: https://docs.lnmarkets.com/api/
