"""Transactional email via Resend, with a no-op fallback.

If RESEND_API_KEY is unset, emails are logged instead of sent so the app keeps
working in local/demo mode. Get a key at https://resend.com (free tier is fine).
"""
import os
from html import escape

import httpx


def _e(value):
    """HTML-escape any user-provided value before it lands in email markup."""
    return escape(str(value if value is not None else ""))

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
# Must be a domain you've verified in Resend. The onboarding@resend.dev sender
# works out of the box for testing.
EMAIL_FROM = os.environ.get("EMAIL_FROM", "Boobly <onboarding@resend.dev>")
# Public URL of the Boobly logo (served by this API at /assets/booblyLogo.jpg).
LOGO_URL = os.environ.get(
    "EMAIL_LOGO_URL", "https://boobly-api.onrender.com/assets/booblyLogo.jpg"
)
# Storefront URL used for the footer links.
STORE_URL = os.environ.get("PUBLIC_BASE_URL", "https://getboobly.com").rstrip("/")
# Address + support contact shown in the footer.
SUPPORT_EMAIL = os.environ.get("SUPPORT_EMAIL", "hello@boobly.com")
COMPANY_ADDRESS = os.environ.get("COMPANY_ADDRESS", "Boobly, Montreal, QC, Canada")


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


def _first_name(name, email=""):
    """A friendly name for the greeting — falls back to the email handle."""
    name = (name or "").strip()
    if name:
        return name.split()[0]
    handle = (email or "").split("@")[0].strip()
    return handle.capitalize() if handle else "there"


def _shell(name, heading, body_html):
    """Wrap content in the branded Boobly email layout (matches the sample).

    Top accent bars + logo header, a "Hello {name}," greeting, the message body,
    a colored links band, and a dark legal footer.
    """
    return f"""\
<div style="margin:0;padding:0;background:#f4f2f8">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f2f8">
    <tr><td align="center" style="padding:24px 12px">
      <table role="presentation" width="600" cellpadding="0" cellspacing="0"
             style="max-width:600px;width:100%;background:#ffffff;border-radius:16px;overflow:hidden;
                    font-family:system-ui,-apple-system,Segoe UI,Arial,sans-serif;color:#1a1330">

        <!-- top accent bars -->
        <tr><td style="height:8px;background:#a6f000;font-size:0;line-height:0">&nbsp;</td></tr>
        <tr><td style="height:8px;background:#ff2e93;font-size:0;line-height:0">&nbsp;</td></tr>

        <!-- logo header -->
        <tr><td align="center"
                style="background:linear-gradient(90deg,#a05cfa,#ff2e93);padding:28px 24px">
          <img src="{LOGO_URL}" alt="Boobly" width="150"
               style="display:block;max-width:150px;height:auto;border:0"/>
        </td></tr>

        <!-- body -->
        <tr><td style="padding:32px 32px 8px">
          <p style="margin:0 0 18px;font-size:16px">Hello {name},</p>
          <h1 style="margin:0 0 16px;font-size:23px;line-height:1.3">{heading}</h1>
          {body_html}
          <p style="margin:28px 0 0;font-size:15px">All the best,<br/>The Boobly Team 💧</p>
        </td></tr>

        <!-- links band -->
        <tr><td align="center" style="background:#20d0c8;padding:22px 24px">
          <div style="font-size:20px;font-weight:800;color:#0b1a19;margin-bottom:8px">getBoobly.com</div>
          <div style="font-size:14px;font-weight:600">
            <a href="{STORE_URL}" style="color:#0b1a19;text-decoration:none;margin:0 8px">› Shop</a>
            <a href="{STORE_URL}/#how" style="color:#0b1a19;text-decoration:none;margin:0 8px">› Help</a>
            <a href="{STORE_URL}/#privacy" style="color:#0b1a19;text-decoration:none;margin:0 8px">› Privacy</a>
          </div>
        </td></tr>

        <!-- legal footer -->
        <tr><td style="background:#0d0d0d;padding:24px;color:#8a8a8a;font-size:12px" align="center">
          <div style="margin-bottom:12px">
            <a href="{STORE_URL}/#privacy" style="color:#ffffff;text-decoration:underline;margin:0 10px">Privacy &amp; Legal</a>
            <a href="mailto:{SUPPORT_EMAIL}" style="color:#ffffff;text-decoration:underline;margin:0 10px">Contact Us</a>
            <a href="{STORE_URL}/#unsubscribe" style="color:#ffffff;text-decoration:underline;margin:0 10px">Unsubscribe</a>
          </div>
          <div style="margin-bottom:6px">{COMPANY_ADDRESS}</div>
          <div>© 2026 Boobly. All rights reserved.</div>
        </td></tr>

      </table>
    </td></tr>
  </table>
</div>"""


def _items_table(items):
    rows = "".join(
        f"<tr><td style='padding:6px 0'>{_e(i.get('name','Item'))} × {_e(i.get('qty',1))}</td>"
        f"<td style='padding:6px 0;text-align:right'>${float(i.get('price',0)) * int(i.get('qty',1)):.2f}</td></tr>"
        for i in items
    )
    return f"<table style='width:100%;border-collapse:collapse;font-size:15px'>{rows}</table>"


def send_order_confirmation(order):
    """Email the shopper a receipt for a placed order."""
    customer = order.get("customer") or {}
    to = customer.get("email")
    name = _e(_first_name(customer.get("name"), to))
    addr = order.get("shipping_address") or {}
    ship_html = ""
    if addr.get("line1"):
        ship_html = (
            "<p style='margin:18px 0 4px;font-weight:600'>Shipping to</p>"
            f"<p style='margin:0;opacity:.75;font-size:15px'>{_e(addr.get('line1',''))} {_e(addr.get('line2',''))}<br>"
            f"{_e(addr.get('city',''))} {_e(addr.get('state',''))} {_e(addr.get('postal_code',''))}<br>"
            f"{_e(addr.get('country',''))}</p>"
        )

    body = f"""
      <p style="margin:0 0 16px;font-size:15px">Your Boobly order is confirmed — here's your rainbow of flavor:</p>
      {_items_table(order.get('items', []))}
      <hr style="border:none;border-top:1px solid #eee;margin:14px 0">
      <p style="text-align:right;font-size:17px;margin:0"><b>Total: ${float(order.get('total',0)):.2f}</b></p>
      {ship_html}
      <p style="margin:18px 0 0;font-size:13px;opacity:.7">Order ref: <code>{_e(order.get('id',''))}</code></p>
    """
    html = _shell(name, "Thanks for your order! 🌈", body)
    return _send(to, "Your Boobly order is confirmed 🎉", html)


def send_status_update(order):
    """Notify the shopper when their order status changes (e.g. shipped)."""
    customer = order.get("customer") or {}
    to = customer.get("email")
    name = _e(_first_name(customer.get("name"), to))
    status = order.get("status", "updated")
    pretty = {
        "packed": "is packed and getting ready to ship 📦",
        "shipped": "is on its way to you 🚚",
        "delivered": "has been delivered — enjoy! 🎉",
        "cancelled": "has been cancelled. If this is a surprise, just reply to this email.",
    }.get(status, f"status is now: {_e(status)}")

    body = f"""
      <p style="margin:0;font-size:15px">Your Boobly order <code>{_e(order.get('id',''))}</code> {pretty}</p>
    """
    html = _shell(name, "Order update 🚚", body)
    return _send(to, f"Boobly order update: {status}", html)


def send_welcome(email):
    """Welcome + 10% code when someone joins the newsletter."""
    name = _e(_first_name(None, email))
    body = """
      <p style="margin:0 0 14px;font-size:15px">You're in! Here's <b>10% off</b> your first bottle — use code
        <span style="background:#ffe6f2;color:#c2185b;padding:3px 10px;border-radius:8px;font-weight:800">SQUAD10</span>
        at checkout.</p>
      <p style="margin:0;font-size:15px">12 sugar-free aroma pods. Zero sugar, all fun.</p>
    """
    html = _shell(name, "Welcome to the Boobly squad 🌈", body)
    return _send(email, "Welcome to Boobly — here's your 10% 🎉", html)
