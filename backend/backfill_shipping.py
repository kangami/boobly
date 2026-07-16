"""One-off backfill: recover missing shipping addresses from Stripe.

Older orders were saved with an empty `shipping_address` because the webhook
read the deprecated top-level `shipping_details` field. Stripe still holds the
address on the Checkout Session, so this script re-fetches each affected order
and updates the row.

Run from the backend/ directory with your live env loaded:

    python backfill_shipping.py            # dry run — shows what would change
    python backfill_shipping.py --apply    # actually writes the updates

Requires STRIPE_SECRET_KEY, SUPABASE_URL and SUPABASE_KEY (same as the API).
"""
import sys

from dotenv import load_dotenv

load_dotenv()

import stripe_client
import supabase_client


def _extract_address(session):
    """Pull the shipping address out of a Stripe session, trying every location."""
    collected = session.get("collected_information") or {}
    ship = collected.get("shipping_details") or session.get("shipping_details") or {}
    ship_addr = ship.get("address") or {}
    details = session.get("customer_details") or {}
    if not ship_addr:
        ship_addr = details.get("address") or {}
    if not ship_addr:
        return None, ship, details
    return {
        "line1": ship_addr.get("line1", ""),
        "line2": ship_addr.get("line2", ""),
        "city": ship_addr.get("city", ""),
        "state": ship_addr.get("state", ""),
        "postal_code": ship_addr.get("postal_code", ""),
        "country": ship_addr.get("country", ""),
    }, ship, details


def _is_empty(addr):
    """True if a stored shipping_address has no usable street line."""
    return not (addr or {}).get("line1")


def main(apply: bool):
    stripe = stripe_client._get()
    if stripe is None:
        sys.exit("STRIPE_SECRET_KEY is not set — cannot reach Stripe.")
    client = supabase_client._get_client()
    if client is None:
        sys.exit("SUPABASE_URL / SUPABASE_KEY not set — cannot reach the database.")

    orders = supabase_client.list_orders()
    # Only Stripe-backed orders (session ids start with "cs_") that are missing an address.
    targets = [
        o for o in orders
        if str(o.get("id", "")).startswith("cs_") and _is_empty(o.get("shipping_address"))
    ]
    print(f"{len(targets)} order(s) missing a shipping address.\n")

    fixed = 0
    for o in targets:
        oid = o["id"]
        try:
            session = stripe.checkout.Session.retrieve(oid)
        except Exception as exc:
            print(f"  ! {oid}: could not fetch from Stripe: {exc}")
            continue

        addr, ship, details = _extract_address(session)
        if addr is None:
            print(f"  - {oid}: Stripe has no address either, skipping.")
            continue

        # Also refresh the customer name/phone from the shipping details if we can.
        customer = dict(o.get("customer") or {})
        customer["name"] = ship.get("name") or customer.get("name", "")
        customer["phone"] = details.get("phone") or customer.get("phone", "")

        summary = f"{addr['line1']}, {addr['city']} {addr['postal_code']} {addr['country']}"
        print(f"  {'~' if not apply else '+'} {oid}: {summary}")

        if apply:
            try:
                client.table("orders").update(
                    {"shipping_address": addr, "customer": customer}
                ).eq("id", oid).execute()
                fixed += 1
            except Exception as exc:
                print(f"    ! update failed: {exc}")

    print()
    if apply:
        print(f"Done. Updated {fixed} order(s).")
    else:
        print("Dry run — re-run with --apply to write these changes.")


if __name__ == "__main__":
    main(apply="--apply" in sys.argv[1:])
