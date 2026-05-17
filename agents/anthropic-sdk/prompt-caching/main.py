#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "anthropic",
# ]
# ///

import time
import anthropic

# Sonnet 4.6 pricing per million tokens
PRICE = {
    "input":          3.00,
    "cache_creation": 3.75,
    "cache_read":     0.30,
    "output":        15.00,
}

# ~6k-token synthetic API reference doc — large enough that prefill compute is
# non-trivial, realistic stand-in for a static system prompt reused across requests.
LARGE_DOC = """
# Acme Payments API — Reference Documentation v4.2

## Overview

The Acme Payments API provides a RESTful interface for processing financial transactions,
managing customer accounts, handling refunds, and generating reconciliation reports.
All endpoints require TLS 1.2 or higher. Authentication is via Bearer token issued
through the /auth/token endpoint.

Base URL: https://api.acmepayments.example/v4

---

## Authentication

### POST /auth/token

Exchange client credentials for a short-lived access token.

**Request body**
```json
{
  "client_id": "string",
  "client_secret": "string",
  "grant_type": "client_credentials",
  "scope": "payments:read payments:write refunds:write reports:read"
}
```

**Response 200**
```json
{
  "access_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "payments:read payments:write refunds:write reports:read"
}
```

**Error codes**
- 401 invalid_client — credentials not recognised
- 400 invalid_scope — one or more requested scopes unknown
- 429 rate_limited — token issuance rate exceeded; retry after header indicates delay

Tokens carry a 1-hour TTL. Rotate secrets via the developer portal. Leaked tokens
can be revoked immediately via DELETE /auth/token/{jti}.

---

## Payments

### POST /payments

Create and immediately submit a new payment.

**Headers**
- Authorization: Bearer {token}
- Idempotency-Key: {uuid} (strongly recommended; replays safe for 24 h)
- Content-Type: application/json

**Request body**
```json
{
  "amount": 10050,
  "currency": "USD",
  "source": {
    "type": "card",
    "number": "4111111111111111",
    "exp_month": 12,
    "exp_year": 2027,
    "cvc": "123",
    "billing": {
      "name": "Jane Doe",
      "line1": "123 Main St",
      "city": "San Francisco",
      "state": "CA",
      "postal_code": "94105",
      "country": "US"
    }
  },
  "destination": {
    "type": "bank_account",
    "routing_number": "021000021",
    "account_number": "9876543210",
    "account_type": "checking"
  },
  "description": "Invoice #1042",
  "metadata": {
    "order_id": "ord_8fj29a"
  },
  "capture_method": "automatic",
  "statement_descriptor": "ACME CORP"
}
```

**amount** — integer, in the smallest currency unit (cents for USD). Min 50, max 99999999.
**currency** — ISO 4217 three-letter code. Supported: USD, EUR, GBP, CAD, AUD, JPY, SGD, HKD.
**capture_method** — `automatic` (default) captures immediately; `manual` creates an authorisation hold requiring a subsequent POST /payments/{id}/capture within 7 days.

**Response 201**
```json
{
  "id": "pay_3Kx9mQzRtV",
  "object": "payment",
  "status": "succeeded",
  "amount": 10050,
  "currency": "USD",
  "created": 1716000000,
  "description": "Invoice #1042",
  "metadata": { "order_id": "ord_8fj29a" },
  "outcome": {
    "network_status": "approved_by_network",
    "reason": null,
    "risk_level": "normal",
    "risk_score": 14,
    "seller_message": "Payment complete."
  },
  "receipt_url": "https://pay.acmepayments.example/r/pay_3Kx9mQzRtV"
}
```

**Payment status values**
| Status | Description |
|---|---|
| `requires_payment_method` | No source attached yet |
| `requires_confirmation` | Awaiting explicit confirm call |
| `requires_action` | 3DS or other out-of-band step needed |
| `processing` | Submitted to network, pending settlement |
| `succeeded` | Captured and settled |
| `canceled` | Voided before capture |
| `failed` | Declined or error |

---

### GET /payments/{id}

Retrieve a single payment by ID.

**Response 200** — same schema as POST /payments 201 response.

---

### GET /payments

List payments with optional filtering.

**Query parameters**
- `created[gte]` / `created[lte]` — Unix timestamp range
- `status` — filter by status value
- `cursor` — opaque pagination cursor from previous response
- `limit` — 1–100, default 20

**Response 200**
```json
{
  "object": "list",
  "data": [ /* array of payment objects */ ],
  "has_more": true,
  "next_cursor": "cur_abc123"
}
```

---

### POST /payments/{id}/capture

Capture a previously authorised payment (only valid when capture_method=manual).

**Request body**
```json
{
  "amount": 10050
}
```

Partial captures are supported; `amount` must be ≤ original authorised amount.
Remaining uncaptured amount is automatically released.

---

### POST /payments/{id}/cancel

Cancel/void a payment. Only permitted for payments in `requires_capture` or
`requires_confirmation` status. Cancellation is immediate and irrevocable.

---

## Refunds

### POST /refunds

Initiate a full or partial refund against a succeeded payment.

**Request body**
```json
{
  "payment_id": "pay_3Kx9mQzRtV",
  "amount": 5000,
  "reason": "customer_request",
  "metadata": {}
}
```

**reason** — one of: `duplicate`, `fraudulent`, `customer_request`. Used for
reporting and risk scoring; does not affect processing.

Refunds settle within 5–10 business days for cards, 1–3 days for bank accounts.
Original payment fees are not refunded.

**Response 201**
```json
{
  "id": "ref_7Yp2nLwKsA",
  "object": "refund",
  "payment_id": "pay_3Kx9mQzRtV",
  "amount": 5000,
  "currency": "USD",
  "status": "pending",
  "reason": "customer_request",
  "created": 1716003600
}
```

---

### GET /refunds/{id}

Retrieve a single refund. Status transitions: `pending` → `succeeded` or `failed`.

---

## Disputes

Disputes (chargebacks) are automatically created when a cardholder files a claim
with their issuing bank. You receive a `dispute.created` webhook event.

### GET /disputes/{id}

**Response 200**
```json
{
  "id": "dis_5Hm4kBvWnQ",
  "object": "dispute",
  "payment_id": "pay_3Kx9mQzRtV",
  "amount": 10050,
  "currency": "USD",
  "status": "needs_response",
  "reason": "credit_not_processed",
  "evidence_due_by": 1716518400,
  "evidence": null
}
```

### POST /disputes/{id}/evidence

Submit evidence to counter a dispute. Must be submitted before `evidence_due_by`.

```json
{
  "customer_communication": "base64-encoded PDF",
  "shipping_documentation": "base64-encoded PDF",
  "service_date": "2026-05-01",
  "uncategorized_text": "Customer received order on 2026-05-03 per tracking #1Z999..."
}
```

---

## Webhooks

Register endpoints to receive real-time event notifications.

### POST /webhooks

```json
{
  "url": "https://yourserver.example/hooks/acme",
  "events": ["payment.succeeded", "payment.failed", "refund.succeeded", "dispute.created"],
  "secret": "whsec_your_signing_secret"
}
```

Events are delivered with an `Acme-Signature` header (HMAC-SHA256 of the raw body
using your signing secret). Validate before processing. Retry schedule: immediate,
then 5 min, 30 min, 2 h, 6 h, 24 h (6 attempts total). Return 2xx to acknowledge.

**Event types**
- `payment.created` / `payment.succeeded` / `payment.failed` / `payment.canceled`
- `refund.created` / `refund.succeeded` / `refund.failed`
- `dispute.created` / `dispute.closed`
- `payout.paid` / `payout.failed`

---

## Reports

### GET /reports/reconciliation

Generate a reconciliation report for a date range.

**Query parameters**
- `date[gte]` / `date[lte]` — ISO 8601 date (YYYY-MM-DD), max range 31 days
- `format` — `json` (default) or `csv`
- `timezone` — IANA tz name, default UTC

**Response 200** — array of settlement records with payment IDs, amounts, fees,
net amounts, and settlement dates.

---

## Rate Limits

| Endpoint group | Limit |
|---|---|
| POST /auth/token | 10 req/min per client |
| POST /payments | 100 req/min per account |
| GET /payments, GET /refunds | 300 req/min per account |
| POST /refunds | 50 req/min per account |
| POST /webhooks | 20 req/min per account |
| GET /reports/* | 10 req/min per account |

Responses include `X-RateLimit-Remaining` and `X-RateLimit-Reset` headers.
On 429, honour the `Retry-After` header before retrying.

---

## Error Schema

All errors follow a consistent envelope:

```json
{
  "error": {
    "code": "card_declined",
    "message": "Your card was declined.",
    "param": null,
    "doc_url": "https://docs.acmepayments.example/errors/card_declined"
  }
}
```

**Common error codes**
- `authentication_required` — token missing or expired
- `card_declined` — issuer declined; check decline_code sub-field
- `insufficient_funds` — card or account has insufficient balance
- `invalid_account` — destination account details invalid
- `idempotency_conflict` — same Idempotency-Key, different body
- `resource_not_found` — ID not found or not accessible to this account
- `rate_limited` — slow down requests
- `internal_error` — transient server error; safe to retry with backoff

---

## SDK support

Official SDKs: Python, Node.js, Go, Ruby, Java. All wrap this REST API with
typed models, automatic retry with exponential backoff, and idempotency key
management. Install via your package manager (e.g. `pip install acme-payments`).

Changelog and migration guides: https://docs.acmepayments.example/changelog
""" * 3  # repeat 3x to reach ~6k tokens


def cost_usd(usage) -> float:
    return (
        usage.input_tokens          * PRICE["input"]          / 1_000_000
        + usage.cache_creation_input_tokens * PRICE["cache_creation"] / 1_000_000
        + usage.cache_read_input_tokens     * PRICE["cache_read"]     / 1_000_000
        + usage.output_tokens        * PRICE["output"]         / 1_000_000
    )


def run(client: anthropic.Anthropic, label: str, use_cache: bool) -> dict:
    system = [{"type": "text", "text": LARGE_DOC}]
    if use_cache:
        system[0]["cache_control"] = {"type": "ephemeral"}

    ttft = None
    t_start = time.perf_counter()

    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=64,
        system=system,
        messages=[{"role": "user", "content": "In one sentence, what does this API do?"}],
    ) as stream:
        for _ in stream.text_stream:
            if ttft is None:
                ttft = (time.perf_counter() - t_start) * 1000
        final = stream.get_final_message()

    total_ms = (time.perf_counter() - t_start) * 1000
    u = final.usage

    return {
        "label":          label,
        "ttft_ms":        round(ttft or 0),
        "total_ms":       round(total_ms),
        "input":          u.input_tokens,
        "cache_creation": u.cache_creation_input_tokens,
        "cache_read":     u.cache_read_input_tokens,
        "output":         u.output_tokens,
        "cost_usd":       cost_usd(u),
    }


client = anthropic.Anthropic()

results = []
for label, use_cache in [("baseline (no cache)", False),
                          ("cache create",        True),
                          ("cache hit",           True)]:
    print(f"Running: {label}...")
    results.append(run(client, label, use_cache))
    time.sleep(1)

# Print comparison table
cols = ["ttft_ms", "total_ms", "input", "cache_creation", "cache_read", "output", "cost_usd"]
labels = [r["label"] for r in results]
col_w = 16

print()
print(f"{'':30s}" + "".join(f"{l:>{col_w}}" for l in labels))
print("-" * (30 + col_w * len(labels)))
for col in cols:
    vals = [r[col] for r in results]
    fmt = f"{col:30s}" + "".join(
        f"{v:>{col_w}.4f}" if isinstance(v, float) else f"{v:>{col_w}}"
        for v in vals
    )
    print(fmt)
