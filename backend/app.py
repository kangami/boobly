"""Boobly Flask API — catalog + orders, backed by Supabase (with fallback)."""
import hmac
import os
import queue
import uuid
from functools import wraps

from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

import products
import supabase_client
import stripe_client
import email_client
import catalog_store

BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, "..", "assets")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)
ADMIN_API_TOKEN = os.environ.get("ADMIN_API_TOKEN")
ORDER_STATUSES = ["received", "paid", "packed", "shipped", "delivered", "cancelled"]
STORAGE_BUCKET = "boobly-media"
ALLOWED_IMAGE_EXT = {"png", "jpg", "jpeg", "webp", "gif"}
# Comma-separated allowed origins for the browser app (e.g. your Vercel URL).
# Empty or unset -> allow all ("*"). Trailing slashes are stripped so a value
# like "https://app.vercel.app/" still matches the browser Origin (no slash).
_cors_raw = (os.environ.get("CORS_ORIGINS") or "").strip() or "*"
CORS_ORIGINS = [o.strip().rstrip("/") for o in _cors_raw.split(",") if o.strip()] or ["*"]

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": CORS_ORIGINS}})


def _validate_cart(data):
    """Return (clean_items, total, customer) or raise ValueError with a message.

    Prices are resolved server-side from the catalog — the client-sent `price`
    is intentionally ignored so a tampered cart can't underpay.
    """
    items = data.get("items", [])
    if not items:
        raise ValueError("Cart is empty")

    total = 0.0
    clean_items = []
    for it in items:
        try:
            qty = int(it.get("qty", 1))
        except (TypeError, ValueError):
            raise ValueError("Invalid quantity")
        qty = max(1, min(qty, 99))  # clamp to a sane per-line range

        info = catalog_store.lookup_price(it.get("type"), it.get("id"))
        if info is None:
            raise ValueError(f"Unknown item: {it.get('type')}/{it.get('id')}")

        price = info["price"]  # authoritative server price
        total += qty * price
        clean_items.append({
            "id": it.get("id"),
            "name": info["name"],
            "type": it.get("type"),
            "qty": qty,
            "price": price,
        })

    customer = {
        "name": (data.get("customer") or {}).get("name", ""),
        "email": (data.get("customer") or {}).get("email", ""),
    }
    return clean_items, round(total, 2), customer


# --- Live updates (Server-Sent Events) -------------------------------------
# In-process pub/sub: each connected client gets a queue; a catalog change
# notifies them all so storefronts refresh without a page reload.
_sse_subscribers = set()


def _broadcast_catalog():
    for q in list(_sse_subscribers):
        try:
            q.put_nowait("catalog")
        except Exception:
            pass


def require_admin(view):
    """Gate an endpoint behind the admin token (header `X-Admin-Token`).

    Secure by default: if ADMIN_API_TOKEN isn't configured, access is denied
    rather than left open.
    """
    @wraps(view)
    def wrapper(*args, **kwargs):
        sent = request.headers.get("X-Admin-Token", "")
        if not ADMIN_API_TOKEN or not hmac.compare_digest(sent, ADMIN_API_TOKEN):
            return jsonify({"error": "Unauthorized"}), 401
        return view(*args, **kwargs)
    return wrapper


@app.get("/api/health")
def health():
    return jsonify({
        "ok": True,
        "supabase": supabase_client.is_live(),
        "stripe": stripe_client.is_live(),
        "email": email_client.is_live(),
    })


@app.get("/api/catalog")
def catalog():
    return jsonify(catalog_store.get_catalog())


@app.get("/api/events")
def events():
    """SSE stream: emits a 'change' event whenever the catalog is updated."""
    def stream():
        q = queue.Queue()
        _sse_subscribers.add(q)
        try:
            yield "retry: 3000\n\n"
            yield "event: ping\ndata: connected\n\n"
            while True:
                try:
                    msg = q.get(timeout=15)
                    yield f"event: change\ndata: {msg}\n\n"
                except queue.Empty:
                    yield ": keepalive\n\n"  # comment line keeps the connection open
        finally:
            _sse_subscribers.discard(q)

    return Response(
        stream(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Connection": "keep-alive"},
    )


@app.post("/api/orders")
def create_order():
    data = request.get_json(silent=True) or {}
    try:
        clean_items, total, customer = _validate_cart(data)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    order = supabase_client.save_order({
        "items": clean_items,
        "total": total,
        "customer": customer,
    })
    email_client.send_order_confirmation(order)
    return jsonify({"ok": True, "order": order}), 201


@app.post("/api/checkout")
def create_checkout():
    """Create a Stripe Checkout session and return its hosted URL.

    If Stripe isn't configured, return 503 so the frontend can fall back to
    the simulated-order flow.
    """
    data = request.get_json(silent=True) or {}
    try:
        clean_items, total, customer = _validate_cart(data)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    if not stripe_client.is_live():
        return jsonify({"error": "Stripe not configured", "offline": True}), 503

    try:
        session = stripe_client.create_checkout_session(clean_items, total, customer)
    except Exception as exc:
        print(f"[checkout] failed: {exc}")
        return jsonify({"error": "Could not start checkout"}), 502

    return jsonify({"ok": True, "url": session.url, "id": session.id})


@app.post("/api/webhook")
def stripe_webhook():
    """Persist the order once Stripe confirms payment."""
    event = stripe_client.parse_webhook(request.get_data(), request.headers.get("Stripe-Signature"))
    if event is None:
        return jsonify({"error": "Invalid webhook"}), 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        session_id = session.get("id")

        # Idempotency: Stripe retries webhooks, so never insert the same order twice.
        if supabase_client.order_exists(session_id):
            print(f"[webhook] order {session_id} already saved, skipping")
            return jsonify({"received": True, "duplicate": True})

        meta = session.get("metadata") or {}
        line_items = []
        try:
            stripe = stripe_client._get()
            items_resp = stripe.checkout.Session.list_line_items(session_id, limit=100)
            line_items = [
                {
                    "name": li.get("description"),
                    "qty": li.get("quantity"),
                    "price": (li.get("amount_total", 0) / 100) / max(1, li.get("quantity", 1)),
                }
                for li in items_resp.get("data", [])
            ]
        except Exception as exc:  # pragma: no cover
            print(f"[webhook] could not fetch line items: {exc}")

        # Delivery details Stripe collected on its hosted page.
        ship = session.get("shipping_details") or {}
        ship_addr = ship.get("address") or {}
        details = session.get("customer_details") or {}

        order = supabase_client.save_order({
            "id": session_id,
            "items": line_items,
            "total": (session.get("amount_total") or 0) / 100,
            "customer": {
                "name": ship.get("name") or details.get("name") or meta.get("customer_name", ""),
                "email": session.get("customer_email")
                or details.get("email")
                or meta.get("customer_email", ""),
                "phone": details.get("phone") or session.get("customer_phone") or "",
            },
            "shipping_address": {
                "line1": ship_addr.get("line1", ""),
                "line2": ship_addr.get("line2", ""),
                "city": ship_addr.get("city", ""),
                "state": ship_addr.get("state", ""),
                "postal_code": ship_addr.get("postal_code", ""),
                "country": ship_addr.get("country", ""),
            },
            "status": "paid",
        })
        email_client.send_order_confirmation(order)
        print(f"[webhook] order saved for session {session_id}")

    return jsonify({"received": True})


# --- Order tracking (public, identity-checked by email) --------------------
@app.get("/api/track")
def track_order():
    """Look up one order by id + matching email. No account required."""
    order_id = (request.args.get("id") or "").strip()
    email = (request.args.get("email") or "").strip().lower()
    if not order_id or not email:
        return jsonify({"error": "Order id and email are required"}), 400

    order = supabase_client.get_order(order_id)
    if not order or (order.get("customer") or {}).get("email", "").lower() != email:
        # Same response whether the id is wrong or the email mismatches,
        # so we don't leak which order ids exist.
        return jsonify({"error": "No matching order found"}), 404

    # Return only what the shopper needs — never the raw customer record.
    return jsonify({
        "id": order.get("id"),
        "status": order.get("status"),
        "total": order.get("total"),
        "items": order.get("items", []),
        "created_at": order.get("created_at"),
        "shipping_address": order.get("shipping_address", {}),
    })


# --- Newsletter -------------------------------------------------------------
@app.post("/api/subscribe")
def subscribe():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({"error": "Please enter a valid email"}), 400
    supabase_client.add_subscriber(email)
    return jsonify({"ok": True}), 201


# --- Admin ------------------------------------------------------------------
@app.get("/api/orders")
@require_admin
def list_orders():
    return jsonify(supabase_client.list_orders())


@app.get("/api/admin/subscribers")
@require_admin
def admin_subscribers():
    return jsonify(supabase_client.list_subscribers())


@app.get("/api/admin/customers")
@require_admin
def admin_customers():
    """Aggregate orders per customer email → buying frequency & lifetime value."""
    subscriber_emails = {s.get("email", "").lower() for s in supabase_client.list_subscribers()}
    customers = {}
    for o in supabase_client.list_orders():
        cust = o.get("customer") or {}
        email = (cust.get("email") or "").strip().lower()
        if not email:
            continue
        created = o.get("created_at") or ""
        c = customers.get(email)
        if c is None:
            c = customers[email] = {
                "email": email,
                "name": cust.get("name") or "",
                "orders": 0,
                "total_spent": 0.0,
                "first_order": created,
                "last_order": created,
                "is_subscriber": email in subscriber_emails,
            }
        c["orders"] += 1
        c["total_spent"] += float(o.get("total") or 0)
        if cust.get("name") and not c["name"]:
            c["name"] = cust["name"]
        if created and created < c["first_order"]:
            c["first_order"] = created
        if created and created > c["last_order"]:
            c["last_order"] = created

    result = sorted(customers.values(), key=lambda c: c["orders"], reverse=True)
    for c in result:
        c["total_spent"] = round(c["total_spent"], 2)
    return jsonify(result)


@app.post("/api/orders/<order_id>/status")
@require_admin
def set_order_status(order_id):
    data = request.get_json(silent=True) or {}
    status = (data.get("status") or "").strip()
    if status not in ORDER_STATUSES:
        return jsonify({"error": f"status must be one of {ORDER_STATUSES}"}), 400

    order = supabase_client.update_order_status(order_id, status)
    if order is None:
        return jsonify({"error": "Order not found"}), 404
    email_client.send_status_update(order)
    return jsonify({"ok": True, "order": order})


@app.get("/api/admin/products")
@require_admin
def admin_list_products():
    return jsonify(catalog_store.list_products())


@app.post("/api/admin/products")
@require_admin
def admin_upsert_product():
    data = request.get_json(silent=True) or {}
    try:
        row = catalog_store.upsert_product(data)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400
    _broadcast_catalog()
    return jsonify({"ok": True, "product": row})


@app.delete("/api/admin/products/<pid>")
@require_admin
def admin_delete_product(pid):
    ok = catalog_store.delete_product(pid)
    _broadcast_catalog()
    return jsonify({"ok": ok})


def _store_image(pid, file_storage):
    """Save an uploaded image and return its public URL.

    Uses Supabase Storage (public bucket) when available, otherwise falls back
    to local disk served at /api/uploads/<file>.
    """
    ext = (file_storage.filename.rsplit(".", 1)[-1] if "." in file_storage.filename else "").lower()
    if ext not in ALLOWED_IMAGE_EXT:
        raise ValueError(f"image must be one of {sorted(ALLOWED_IMAGE_EXT)}")
    data = file_storage.read()
    content_type = file_storage.mimetype or "application/octet-stream"
    filename = f"{pid}-{uuid.uuid4().hex[:8]}.{ext}"

    client = supabase_client._get_client()
    if client is not None:
        path = f"products/{filename}"
        try:
            try:
                client.storage.create_bucket(STORAGE_BUCKET, options={"public": True})
            except Exception:
                pass  # bucket already exists
            client.storage.from_(STORAGE_BUCKET).upload(
                path, data, {"content-type": content_type, "upsert": "true"}
            )
            url = client.storage.from_(STORAGE_BUCKET).get_public_url(path)
            return url.rstrip("?")
        except Exception as exc:
            print(f"[image] Supabase Storage failed, using local disk: {exc}")

    # Local fallback.
    with open(os.path.join(UPLOADS_DIR, filename), "wb") as fh:
        fh.write(data)
    return f"/api/uploads/{filename}"


@app.post("/api/admin/products/<pid>/image")
@require_admin
def admin_upload_image(pid):
    if "image" not in request.files:
        return jsonify({"error": "No image file (field name must be 'image')"}), 400
    try:
        url = _store_image(pid, request.files["image"])
        row = catalog_store.set_product_image(pid, url)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400
    _broadcast_catalog()
    return jsonify({"ok": True, "url": url, "product": row})


@app.delete("/api/admin/products/<pid>/image")
@require_admin
def admin_delete_image(pid):
    try:
        row = catalog_store.clear_product_image(pid)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400
    _broadcast_catalog()
    return jsonify({"ok": True, "product": row})


@app.get("/api/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOADS_DIR, filename)


@app.get("/api/admin/settings")
@require_admin
def admin_get_settings():
    return jsonify(catalog_store.get_settings())


@app.post("/api/admin/settings")
@require_admin
def admin_set_settings():
    data = request.get_json(silent=True) or {}
    updated = {}
    try:
        for key in ("pod_pack_price", "pod_pack_size"):
            if key in data:
                updated.update(catalog_store.set_setting(key, data[key]))
    except ValueError as err:
        return jsonify({"error": str(err)}), 400
    _broadcast_catalog()
    return jsonify({"ok": True, "settings": updated})


@app.get("/admin")
def admin_page():
    return send_from_directory(BASE_DIR, "admin.html")


@app.get("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(ASSETS_DIR, filename)


if __name__ == "__main__":
    # threaded=True so the long-lived SSE stream doesn't block other requests.
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
