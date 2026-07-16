"""Stripe Checkout helper with a graceful offline fallback.

If STRIPE_SECRET_KEY is unset, is_live() returns False and the app falls back
to the simulated-order flow so the storefront still works for local demos.
"""
import os

SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "http://localhost:5173")
# Checkout currency (ISO 4217, lowercase), e.g. cad, usd, eur.
CURRENCY = os.environ.get("STRIPE_CURRENCY", "cad").lower()
# Countries Boobly will ship to (Stripe collects + validates the address).
SHIP_COUNTRIES = [
    c.strip().upper()
    for c in os.environ.get("SHIP_COUNTRIES", "CA").split(",")
    if c.strip()
]
# Delivery fee (in currency units) applied to orders below the free-shipping
# threshold. Orders at or above the threshold ship free.
DELIVERY_FEE = float(os.environ.get("DELIVERY_FEE", "8.95"))
FREE_SHIP_THRESHOLD = float(os.environ.get("FREE_SHIP_THRESHOLD", "65"))

_stripe = None


def _get():
    global _stripe
    if _stripe is not None:
        return _stripe
    if not SECRET_KEY:
        return None
    try:
        import stripe
        stripe.api_key = SECRET_KEY
        _stripe = stripe
        return _stripe
    except Exception as exc:  # pragma: no cover
        print(f"[stripe] could not init: {exc}")
        return None


def is_live():
    return _get() is not None


def _rate(name, amount, description, min_days, max_days):
    """Build one Stripe shipping_rate_data entry."""
    return {
        "shipping_rate_data": {
            "type": "fixed_amount",
            "fixed_amount": {"amount": max(0, round(amount * 100)), "currency": CURRENCY},
            "display_name": name,
            "delivery_estimate": {
                "minimum": {"unit": "business_day", "value": min_days},
                "maximum": {"unit": "business_day", "value": max_days},
            },
            "metadata": {"description": description},
        }
    }


def _shipping_options(total):
    """Delivery methods offered at checkout.

    Orders at/above FREE_SHIP_THRESHOLD ship free; smaller orders pay the
    delivery fee and choose between Standard and P.O. Box delivery.
    """
    if float(total or 0) >= FREE_SHIP_THRESHOLD:
        return [_rate("Free Delivery", 0, "Free shipping on orders over "
                      f"${FREE_SHIP_THRESHOLD:.0f}", 1, 3)]
    return [
        _rate(
            "Standard Delivery", DELIVERY_FEE,
            "Receive your order in 1-3 business days. Orders placed after 4PM "
            "(EST) or on weekends are processed the next business day.",
            1, 3,
        ),
        _rate(
            "P.O. Box Delivery", DELIVERY_FEE,
            "For P.O. Box addresses. Delivery in 1-3 business days in metro "
            "areas, 2-4 business days elsewhere.",
            1, 4,
        ),
    ]


def create_checkout_session(clean_items, total, customer):
    """Create a hosted Checkout session. Returns the Stripe session object.

    `clean_items` are the validated cart items from app.py (id/name/type/qty/price).
    Prices are USD; Stripe wants integer cents.
    """
    stripe = _get()
    if stripe is None:
        raise RuntimeError("Stripe is not configured")

    line_items = [
        {
            "price_data": {
                "currency": CURRENCY,
                "unit_amount": max(0, round(float(it["price"]) * 100)),
                "product_data": {
                    "name": it.get("name") or "Boobly item",
                    "metadata": {"id": str(it.get("id", "")), "type": it.get("type", "")},
                },
            },
            "quantity": int(it["qty"]),
        }
        for it in clean_items
    ]

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=line_items,
        customer_email=(customer or {}).get("email") or None,
        # Collect a validated delivery address + phone on Stripe's hosted page.
        shipping_address_collection={"allowed_countries": SHIP_COUNTRIES},
        shipping_options=_shipping_options(total),
        phone_number_collection={"enabled": True},
        success_url=f"{PUBLIC_BASE_URL}/?checkout=success&session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{PUBLIC_BASE_URL}/?checkout=cancel",
        # Stash a compact snapshot so the webhook can persist the order.
        metadata={
            "customer_name": (customer or {}).get("name", ""),
            "customer_email": (customer or {}).get("email", ""),
            "total": str(total),
        },
    )
    return session


def parse_webhook(payload: bytes, sig_header: str):
    """Verify and return a Stripe event, or None if it can't be verified."""
    stripe = _get()
    if stripe is None:
        return None
    if not WEBHOOK_SECRET:
        # No signing secret configured — best-effort parse without verification.
        try:
            return stripe.Event.construct_from(__import__("json").loads(payload), stripe.api_key)
        except Exception as exc:  # pragma: no cover
            print(f"[stripe] webhook parse failed: {exc}")
            return None
    try:
        return stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except Exception as exc:
        print(f"[stripe] webhook signature verification failed: {exc}")
        return None
