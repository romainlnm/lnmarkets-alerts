#!/bin/bash
# Cron-friendly alert script - runs check and sends to Telegram if alerts

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Load credentials
if [ -f "$SKILL_DIR/.env" ]; then
    export $(grep -v '^#' "$SKILL_DIR/.env" | xargs)
fi

# Run alert check
OUTPUT=$(python3 "$SCRIPT_DIR/alert_check.py" 2>&1)
EXIT_CODE=$?

# If there are alerts (exit code 1), send to Telegram
if [ $EXIT_CODE -eq 1 ] && [ -n "$OUTPUT" ]; then
    # Telegram config (set these or pass as env vars)
    BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-8395043515:AAHTtUrHIgWy_20KtnF7DYWrKZyavkJ0Pzk}"
    CHAT_ID="${TELEGRAM_CHAT_ID:-582668048}"
    
    # Send to Telegram
    curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
        -d "chat_id=${CHAT_ID}" \
        -d "text=${OUTPUT}" \
        -d "parse_mode=HTML" > /dev/null
fi
