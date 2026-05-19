#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
source .venv/bin/activate

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <tool_name> [payload_json | @payload_file]"
  echo "Example: $0 sales_invoice_list '{}'"
  exit 1
fi

tool_name="$1"
shift

payload='{}'
if [ "$#" -gt 0 ]; then
  arg="$1"
  if [[ "$arg" == @* ]]; then
    payload=$(cat "${arg:1}")
  else
    payload="$arg"
  fi
fi

read ts sig bearer <<< $(
  python3 - <<'PY'
import os, hmac, hashlib, time
env = {}
with open('.env') as f:
  for l in f:
    if '=' in l:
      k,v = l.strip().split('=',1); env[k]=v
secret = env.get('ACCURATE_API_SECRET','')
bearer = env.get('ACCURATE_BEARER_TOKEN','')
ts = str(int(time.time()*1000))
sig = hmac.new(secret.encode('utf-8'), ts.encode('utf-8'), hashlib.sha256).hexdigest()
print(ts, sig, bearer)
PY
)

payload_json=$(python3 - "${payload}" <<'PY'
import json, sys
payload = sys.argv[1]
print(json.dumps({"arguments": json.loads(payload)}))
PY
)

curl -s -X POST "http://127.0.0.1:8000/call/${tool_name}" \
  -H "Authorization: Bearer ${bearer}" \
  -H "x-api-timestamp: ${ts}" \
  -H "x-api-signature: ${sig}" \
  -H "Content-Type: application/json" \
  -d "${payload_json}"
