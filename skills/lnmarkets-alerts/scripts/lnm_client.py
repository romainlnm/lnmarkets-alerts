#!/usr/bin/env python3
"""LN Markets API client with authentication (stdlib only) - v3 API."""

import os
import time
import hmac
import hashlib
import base64
import json
import urllib.parse
import urllib.request
import urllib.error

API_BASE = "https://api.lnmarkets.com/v3"

def get_server_time() -> int:
    """Get server timestamp to avoid clock sync issues."""
    try:
        req = urllib.request.Request(f"{API_BASE}/time", method="GET")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            # Parse ISO time and convert to ms timestamp
            from datetime import datetime
            dt = datetime.fromisoformat(data["time"].replace("Z", "+00:00"))
            return int(dt.timestamp() * 1000)
    except:
        # Fallback to local time
        return int(time.time() * 1000)

def get_credentials():
    """Get API credentials from environment variables."""
    key = os.environ.get("LNM_API_KEY")
    secret = os.environ.get("LNM_API_SECRET")
    passphrase = os.environ.get("LNM_API_PASSPHRASE")
    
    if not all([key, secret, passphrase]):
        raise ValueError("Missing LNM_API_KEY, LNM_API_SECRET, or LNM_API_PASSPHRASE")
    
    return key, secret, passphrase

def sign_request(secret: str, timestamp: str, method: str, path: str, data: str = "") -> str:
    """Generate HMAC signature for API request (v3 format)."""
    # v3 uses lowercase method
    payload = f"{timestamp}{method.lower()}{path}{data}"
    signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode()

def api_request(method: str, endpoint: str, params: dict = None, auth: bool = True) -> dict:
    """Make API request to LN Markets v3."""
    # Use server time to avoid clock sync issues
    timestamp = str(get_server_time()) if auth else str(int(time.time() * 1000))
    path = f"/v3{endpoint}"
    
    # Build data string for signature
    if method in ["GET", "DELETE"]:
        if params:
            query = urllib.parse.urlencode(params)
            data = f"?{query}"
            url = f"{API_BASE}{endpoint}?{query}"
        else:
            data = ""
            url = f"{API_BASE}{endpoint}"
        body = None
    else:
        data = json.dumps(params, separators=(',', ':')) if params else ""
        url = f"{API_BASE}{endpoint}"
        body = data.encode() if data else None
    
    headers = {}
    
    if auth:
        key, secret, passphrase = get_credentials()
        signature = sign_request(secret, timestamp, method, path, data)
        
        # v3 uses lowercase headers
        headers = {
            "lnm-access-key": key,
            "lnm-access-signature": signature,
            "lnm-access-passphrase": passphrase,
            "lnm-access-timestamp": timestamp,
        }
    
    if method in ["POST", "PUT"] and body:
        headers["Content-Type"] = "application/json"
    
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else str(e)
        raise Exception(f"HTTP {e.code}: {error_body}")

def get_ticker() -> dict:
    """Get current BTC/USD ticker (no auth required)."""
    return api_request("GET", "/futures/ticker", auth=False)

def get_account() -> dict:
    """Get account information including balance."""
    return api_request("GET", "/account")

def get_running_trades() -> list:
    """Get running isolated margin trades."""
    result = api_request("GET", "/futures/isolated/trades/running")
    return result if isinstance(result, list) else []

def get_open_trades() -> list:
    """Get open (pending) isolated margin trades."""
    result = api_request("GET", "/futures/isolated/trades/open")
    return result if isinstance(result, list) else []

def get_cross_position() -> dict:
    """Get cross margin position."""
    return api_request("GET", "/futures/cross/position")

def get_all_positions() -> dict:
    """Get all positions (running isolated trades + cross position)."""
    running = get_running_trades()
    cross = get_cross_position()
    return {"isolated": running, "cross": cross}
