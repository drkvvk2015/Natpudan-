#!/usr/bin/env bash
# Simple helper to clear in-memory error logs on the running backend
API_URL=${1:-http://127.0.0.1:8000}

curl -s -X POST "$API_URL/api/error-correction/errors/clear" | jq || echo "Response: $(curl -s -X POST "$API_URL/api/error-correction/errors/clear")"
