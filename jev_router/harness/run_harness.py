"""
Jev Router Test Harness
Fires all 20 synthetic fixtures at the inbound webhook and records results.
"""

import json
import os
import time
import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from tabulate import tabulate

# ── Config ──────────────────────────────────────────────────────────────────
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "").strip()
API_KEY     = os.getenv("WEBHOOK_API_KEY", "").strip()
FIXTURES    = Path(__file__).parent.parent / "fixtures" / "fixtures.json"
RESULTS_DIR = Path(__file__).parent / "results"
INTER_REQUEST_DELAY = 2   # seconds — prevents race condition on C8 dedup test
REQUEST_TIMEOUT     = 30  # seconds per POST

# C5-01 malformed payload — posted as raw broken string, not valid JSON
C5_01_RAW_BODY = '{unit_id: 0014, text: broken json no quotes}'

# ── Validation ───────────────────────────────────────────────────────────────
if not WEBHOOK_URL:
    raise SystemExit(
        "ERROR: WEBHOOK_URL is not set.\n"
        "Copy .env.example to .env and fill in the real webhook URL."
    )

# ── Load fixtures ─────────────────────────────────────────────────────────────
with open(FIXTURES, "r") as f:
    data = json.load(f)

fixtures = data["fixtures"]
print(f"Loaded {len(fixtures)} fixtures from {FIXTURES}")
print(f"Target: {WEBHOOK_URL}\n")

# ── Build headers ─────────────────────────────────────────────────────────────
headers = {"Content-Type": "application/json"}
if API_KEY:
    headers["X-Api-Key"] = API_KEY

# ── Run ───────────────────────────────────────────────────────────────────────
results = []

for i, fixture in enumerate(fixtures):
    label = fixture.get("_fixture_label", f"fixture-{i}")
    unit_id = fixture.get("unit_id", "NO_ID")

    # C5-01 special case: post raw broken string to simulate malformed JSON
    if label.startswith("C5-01"):
        body_bytes = C5_01_RAW_BODY.encode("utf-8")
        is_malformed = True
    else:
        body_bytes = json.dumps(fixture).encode("utf-8")
        is_malformed = False

    sent_at = datetime.datetime.utcnow().isoformat() + "Z"
    t0 = time.monotonic()

    try:
        resp = requests.post(
            WEBHOOK_URL,
            data=body_bytes,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        latency_ms = round((time.monotonic() - t0) * 1000, 1)
        status     = resp.status_code
        try:
            body = resp.json()
        except Exception:
            body = resp.text[:500]

    except requests.Timeout:
        latency_ms = REQUEST_TIMEOUT * 1000
        status     = "TIMEOUT"
        body       = f"No response within {REQUEST_TIMEOUT}s"

    except requests.RequestException as exc:
        latency_ms = round((time.monotonic() - t0) * 1000, 1)
        status     = "ERROR"
        body       = str(exc)[:500]

    row = {
        "index":       i + 1,
        "unit_id":     unit_id,
        "label":       label,
        "malformed":   is_malformed,
        "http_status": status,
        "latency_ms":  latency_ms,
        "sent_at":     sent_at,
        "response":    body,
    }
    results.append(row)

    # Live console row
    status_str = str(status)
    flag = "OK" if str(status) == "200" else "!!"
    print(f"[{flag}] #{i+1:02d} {label[:55]:<55} {status_str:>7}  {latency_ms:>7}ms")

    # Delay between requests
    if i < len(fixtures) - 1:
        time.sleep(INTER_REQUEST_DELAY)

# ── Write results JSON ────────────────────────────────────────────────────────
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
out_path = RESULTS_DIR / f"run_{ts}.json"

with open(out_path, "w") as f:
    json.dump(
        {
            "run_timestamp": ts,
            "webhook_url":   WEBHOOK_URL,
            "total_fixtures": len(fixtures),
            "results": results,
        },
        f,
        indent=2,
    )

# ── Summary table ─────────────────────────────────────────────────────────────
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

table_rows = [
    [r["index"], r["label"][:50], r["http_status"], r["latency_ms"]]
    for r in results
]
print(tabulate(table_rows, headers=["#", "Fixture", "HTTP", "ms"], tablefmt="simple"))

total   = len(results)
ok      = sum(1 for r in results if str(r["http_status"]) == "200")
timeout = sum(1 for r in results if r["http_status"] == "TIMEOUT")
error   = sum(1 for r in results if r["http_status"] == "ERROR")
other   = total - ok - timeout - error

print(f"\nTotal: {total}  |  200 OK: {ok}  |  Timeout: {timeout}  |  Error: {error}  |  Other: {other}")
print(f"Results written to: {out_path}")
