"""Thin Supabase wrapper with a graceful in-memory fallback.

If SUPABASE_URL / SUPABASE_KEY are not set, the app still runs fully using an
in-memory store so the storefront works out of the box. Add credentials in
backend/.env to persist orders to your Supabase Postgres project.
"""
import os
import uuid
from datetime import datetime, timezone

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

_client = None
_memory_orders = []  # fallback store
_memory_subscribers = []  # fallback store for newsletter signups


def _get_client():
    global _client
    if _client is not None:
        return _client
    if not (SUPABASE_URL and SUPABASE_KEY):
        return None
    try:
        from supabase import create_client
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return _client
    except Exception as exc:  # pragma: no cover
        print(f"[supabase] could not init client, using memory store: {exc}")
        return None


def is_live():
    return _get_client() is not None


def save_order(order: dict) -> dict:
    order = {
        **order,
        "id": order.get("id") or str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": order.get("status", "received"),
    }
    client = _get_client()
    if client is None:
        _memory_orders.append(order)
        return order
    try:
        client.table("orders").insert(order).execute()
    except Exception as exc:  # pragma: no cover
        print(f"[supabase] insert failed, falling back to memory: {exc}")
        _memory_orders.append(order)
    return order


def order_exists(order_id) -> bool:
    """True if an order with this id is already stored (webhook idempotency)."""
    if not order_id:
        return False
    client = _get_client()
    if client is None:
        return any(o.get("id") == order_id for o in _memory_orders)
    try:
        res = client.table("orders").select("id").eq("id", order_id).limit(1).execute()
        return bool(res.data)
    except Exception as exc:  # pragma: no cover
        print(f"[supabase] exists check failed: {exc}")
        return any(o.get("id") == order_id for o in _memory_orders)


def get_order(order_id):
    """Return a single order by id, or None."""
    if not order_id:
        return None
    client = _get_client()
    if client is None:
        return next((o for o in _memory_orders if o.get("id") == order_id), None)
    try:
        res = client.table("orders").select("*").eq("id", order_id).limit(1).execute()
        return (res.data or [None])[0]
    except Exception as exc:  # pragma: no cover
        print(f"[supabase] get_order failed: {exc}")
        return next((o for o in _memory_orders if o.get("id") == order_id), None)


def update_order_status(order_id, status):
    """Set an order's status. Returns the updated order, or None if not found."""
    client = _get_client()
    if client is None:
        for o in _memory_orders:
            if o.get("id") == order_id:
                o["status"] = status
                return o
        return None
    try:
        res = client.table("orders").update({"status": status}).eq("id", order_id).execute()
        return (res.data or [None])[0]
    except Exception as exc:  # pragma: no cover
        print(f"[supabase] update_order_status failed: {exc}")
        return None


def list_orders():
    client = _get_client()
    if client is None:
        return list(reversed(_memory_orders))
    try:
        res = client.table("orders").select("*").order("created_at", desc=True).execute()
        return res.data or []
    except Exception as exc:  # pragma: no cover
        print(f"[supabase] select failed: {exc}")
        return list(reversed(_memory_orders))


def add_subscriber(email: str) -> dict:
    """Store a newsletter signup (idempotent on email). Returns the record."""
    email = (email or "").strip().lower()
    record = {"email": email, "created_at": datetime.now(timezone.utc).isoformat()}
    client = _get_client()
    if client is None:
        if not any(s["email"] == email for s in _memory_subscribers):
            _memory_subscribers.append(record)
        return record
    try:
        # upsert on the email primary key = no duplicates.
        client.table("subscribers").upsert(record, on_conflict="email").execute()
    except Exception as exc:  # pragma: no cover
        print(f"[supabase] subscriber insert failed: {exc}")
        if not any(s["email"] == email for s in _memory_subscribers):
            _memory_subscribers.append(record)
    return record


def list_subscribers():
    client = _get_client()
    if client is None:
        return list(reversed(_memory_subscribers))
    try:
        res = client.table("subscribers").select("*").order("created_at", desc=True).execute()
        return res.data or []
    except Exception as exc:  # pragma: no cover
        print(f"[supabase] subscribers select failed: {exc}")
        return list(reversed(_memory_subscribers))
