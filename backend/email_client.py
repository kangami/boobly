"""Transactional email via Resend, with a no-op fallback.

If RESEND_API_KEY is unset, emails are logged instead of sent so the app keeps
working in local/demo mode. Get a key at https://resend.com (free tier is fine).
"""
import os

import httpx

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
# Must be a domain you've verified in Resend. The onboarding@resend.dev sender
# works out of the box for testing.
EMAIL_FROM = os.environ.get("EMAIL_FROM", "Boobly <onboarding@resend.dev>")


def is_live():
    return bool(RESEND_API_KEY)


def _send(to, subject, html):
    if not to:
        return False
    if not RESEND_API_KEY:
        # Keep logs ASCII-safe — some Windows consoles can't encode emoji.
        print(f"[email] (offline) skipped, no RESEND_API_KEY -> {to}")
        return False
    try:
        res = httpx.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
            json={"from": EMAIL_FROM, "to": [to], "subject": subject, "html": html},
            timeout=10,
        )
        res.raise_for_status()
        print(f"[email] sent -> {to}")
        return True
    except Exception as exc:  # pragma: no cover
        print(f"[email] send failed: {exc}")
        return False


def _items_table(items):
    rows = "".join(
        f"<tr><td style='padding:6px 0'>{i.get('name','Item')} × {i.get('qty',1)}</td>"
        f"<td style='padding:6px 0;text-align:right'>${float(i.get('price',0)) * int(i.get('qty',1)):.2f}</td></tr>"
        for i in items
    )
    return f"<table style='width:100%;border-collapse:collapse'>{rows}</table>"


def send_order_confirmation(order):
    """Email the shopper a receipt for a placed order."""
    customer = order.get("customer") or {}
    to = customer.get("email")
    name = customer.get("name") or "friend"
    addr = order.get("shipping_address") or {}
    ship_html = ""
    if addr.get("line1"):
        ship_html = (
            "<p style='margin:18px 0 4px;font-weight:600'>Shipping to</p>"
            f"<p style='margin:0;opacity:.8'>{addr.get('line1','')} {addr.get('line2','')}<br>"
            f"{addr.get('city','')} {addr.get('state','')} {addr.get('postal_code','')}<br>"
            f"{addr.get('country','')}</p>"
        )

    html = f"""
    <div style="font-family:system-ui,Arial,sans-serif;max-width:520px;margin:auto;color:#1a1330">
      <h1 style="font-size:26px">🌈 Thanks, {name}!</h1>
      <p>Your Boobly order is confirmed. Here's your rainbow of flavor:</p>
      {_items_table(order.get('items', []))}
      <hr style="border:none;border-top:1px solid #eee;margin:14px 0">
      <p style="text-align:right;font-size:18px"><b>Total: ${float(order.get('total',0)):.2f}</b></p>
      {ship_html}
      <p style="margin-top:18px">Order ref: <code>{order.get('id','')}</code></p>
      <p style="opacity:.7;margin-top:24px">Stay Fresh, Stay You 💧</p>
    </div>
    """
    return _send(to, "Your Boobly order is confirmed 🎉", html)


def send_status_update(order):
    """Notify the shopper when their order status changes (e.g. shipped)."""
    customer = order.get("customer") or {}
    to = customer.get("email")
    name = customer.get("name") or "friend"
    status = order.get("status", "updated")
    pretty = {
        "packed": "is packed and getting ready to ship 📦",
        "shipped": "is on its way to you 🚚",
        "delivered": "has been delivered — enjoy! 🎉",
        "cancelled": "has been cancelled. If this is a surprise, just reply to this email.",
    }.get(status, f"status is now: {status}")

    html = f"""
    <div style="font-family:system-ui,Arial,sans-serif;max-width:520px;margin:auto;color:#1a1330">
      <h1 style="font-size:24px">Hi {name} 👋</h1>
      <p>Your Boobly order <code>{order.get('id','')}</code> {pretty}</p>
      <p style="opacity:.7;margin-top:24px">Stay Fresh, Stay You 💧</p>
    </div>
    """
    return _send(to, f"Boobly order update: {status}", html)
