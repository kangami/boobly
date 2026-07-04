"""DB-backed catalog (products + settings) with an in-memory fallback.

The hardcoded lists in products.py are the SEED. On first use we copy them into
the Supabase `products` / `settings` tables; after that the admin dashboard can
add / edit / delete products and change prices, and those become the source of
truth for both the storefront and server-side checkout pricing.

If Supabase isn't configured (or the tables don't exist yet), everything falls
back to an in-memory copy of the seed so the app keeps working.
"""
import products
import supabase_client

# kind -> which extra fields live in the jsonb `data` blob
_DATA_FIELDS = {
    "bottle": ("tagline", "color", "gradient", "capacity_ml", "emoji"),
    "pod": ("emoji", "notes", "color", "gradient", "family", "caffeine", "vitamins"),
    "bundle": ("emoji", "desc", "bottle_count", "pod_packs", "compare_at", "badge"),
}

# In-memory fallback (lazily seeded)
_mem_products = None
_mem_settings = None


# --------------------------------------------------------------------------- #
# Seed helpers
# --------------------------------------------------------------------------- #
def _seed_rows():
    rows = []
    for pos, b in enumerate(products.BOTTLES):
        rows.append(_row("bottle", b["id"], b["name"], b["price"], pos, b))
    for pos, f in enumerate(products.FLAVORS):
        rows.append(_row("pod", f["id"], f["name"], 0, pos, f))
    for pos, b in enumerate(products.BUNDLES):
        rows.append(_row("bundle", b["id"], b["name"], b["price"], pos, b))
    return rows


def _row(kind, pid, name, price, pos, src):
    data = {k: src[k] for k in _DATA_FIELDS[kind] if k in src}
    return {
        "id": pid,
        "kind": kind,
        "name": name,
        "price": float(price),
        "active": True,
        "position": pos,
        "data": data,
    }


def _seed_settings():
    return {
        "pod_pack_price": float(products.POD_PACK_PRICE),
        "pod_pack_size": int(products.POD_PACK_SIZE),
    }


# --------------------------------------------------------------------------- #
# Low-level access (DB or memory)
# --------------------------------------------------------------------------- #
def _mem_prod():
    global _mem_products
    if _mem_products is None:
        _mem_products = _seed_rows()
    return _mem_products


def _mem_set():
    global _mem_settings
    if _mem_settings is None:
        _mem_settings = _seed_settings()
    return _mem_settings


def _ensure_seeded(client):
    """Populate the DB from the seed the first time (empty tables)."""
    try:
        res = client.table("products").select("id").limit(1).execute()
        if not res.data:
            client.table("products").insert(_seed_rows()).execute()
        sres = client.table("settings").select("key").limit(1).execute()
        if not sres.data:
            client.table("settings").insert(
                [{"key": k, "value": v} for k, v in _seed_settings().items()]
            ).execute()
    except Exception as exc:  # pragma: no cover
        print(f"[catalog] seeding skipped: {exc}")


def _all_products(include_inactive=False):
    client = supabase_client._get_client()
    if client is None:
        rows = list(_mem_prod())
    else:
        try:
            _ensure_seeded(client)
            res = client.table("products").select("*").order("position").execute()
            rows = res.data or []
        except Exception as exc:  # pragma: no cover
            print(f"[catalog] read failed, using memory: {exc}")
            rows = list(_mem_prod())
    if not include_inactive:
        rows = [r for r in rows if r.get("active", True)]
    return rows


def _settings():
    client = supabase_client._get_client()
    if client is None:
        return dict(_mem_set())
    try:
        _ensure_seeded(client)
        res = client.table("settings").select("*").execute()
        out = {r["key"]: r["value"] for r in (res.data or [])}
        return out or dict(_mem_set())
    except Exception as exc:  # pragma: no cover
        print(f"[catalog] settings read failed, using memory: {exc}")
        return dict(_mem_set())


# --------------------------------------------------------------------------- #
# Public API — storefront
# --------------------------------------------------------------------------- #
def _shape(row, with_price):
    out = {"id": row["id"], "name": row["name"], **(row.get("data") or {})}
    if with_price:
        out["price"] = float(row.get("price", 0))
    return out


def get_catalog():
    """Same shape products.catalog() returned, but from the DB."""
    rows = _all_products()
    settings = _settings()
    bottles = [_shape(r, True) for r in rows if r["kind"] == "bottle"]
    flavors = [_shape(r, False) for r in rows if r["kind"] == "pod"]
    bundles = [_shape(r, True) for r in rows if r["kind"] == "bundle"]
    return {
        "bottles": bottles,
        "flavors": flavors,
        "bundles": bundles,
        "pod_pack_price": float(settings.get("pod_pack_price", products.POD_PACK_PRICE)),
        "pod_pack_size": int(settings.get("pod_pack_size", products.POD_PACK_SIZE)),
    }


def lookup_price(item_type, item_id):
    """Authoritative {name, price} for a cart line from the DB, or None.

    Pods are all sold at the single pod_pack_price setting; we still verify the
    flavor id exists and is active.
    """
    rows = _all_products()  # active only
    settings = _settings()
    if item_type in ("bottle", "bundle"):
        for r in rows:
            if r["kind"] == item_type and r["id"] == item_id:
                return {"name": r["name"], "price": float(r["price"])}
    elif item_type == "pod":
        for r in rows:
            if r["kind"] == "pod" and r["id"] == item_id:
                return {
                    "name": f"{r['name']} — pod pack",
                    "price": float(settings.get("pod_pack_price", products.POD_PACK_PRICE)),
                }
    return None


# --------------------------------------------------------------------------- #
# Public API — admin CRUD
# --------------------------------------------------------------------------- #
def list_products():
    """All products including inactive, for the admin dashboard."""
    return _all_products(include_inactive=True)


def get_product(pid):
    """A single product row (including inactive), or None."""
    return next((r for r in _all_products(include_inactive=True) if r["id"] == pid), None)


def upsert_product(payload):
    """Create or update a product. Returns the stored row, or raises ValueError.

    The `data` blob is MERGED with any existing product's data, so a partial edit
    (e.g. just the emoji from the table) never wipes other fields like the image
    or gradient.
    """
    kind = payload.get("kind")
    if kind not in _DATA_FIELDS:
        raise ValueError("kind must be bottle, pod, or bundle")
    pid = (payload.get("id") or "").strip()
    name = (payload.get("name") or "").strip()
    if not pid or not name:
        raise ValueError("id and name are required")
    try:
        price = float(payload.get("price", 0) or 0)
    except (TypeError, ValueError):
        raise ValueError("price must be a number")
    if price < 0:
        raise ValueError("price must be >= 0")

    existing = get_product(pid)
    merged_data = {**((existing or {}).get("data") or {}), **(payload.get("data") or {})}
    row = {
        "id": pid,
        "kind": kind,
        "name": name,
        "price": price,
        "active": bool(payload.get("active", True)),
        "position": int(payload.get("position", 0) or 0),
        "data": merged_data,
    }
    return _persist_product(row)


def _persist_product(row):
    client = supabase_client._get_client()
    if client is None:
        mem = _mem_prod()
        for i, r in enumerate(mem):
            if r["id"] == row["id"]:
                mem[i] = row
                return row
        mem.append(row)
        return row
    try:
        client.table("products").upsert(row).execute()
        return row
    except Exception as exc:
        raise ValueError(f"save failed: {exc}")


def set_product_image(pid, url):
    """Store an image URL on a product's data. Returns the row, or raises."""
    existing = get_product(pid)
    if existing is None:
        raise ValueError("product not found")
    row = {**existing, "data": {**(existing.get("data") or {}), "image": url}}
    row.pop("updated_at", None)
    return _persist_product(row)


def clear_product_image(pid):
    """Remove the image from a product's data. Returns the row, or raises."""
    existing = get_product(pid)
    if existing is None:
        raise ValueError("product not found")
    data = {**(existing.get("data") or {})}
    data.pop("image", None)
    row = {**existing, "data": data}
    row.pop("updated_at", None)
    return _persist_product(row)


def delete_product(pid):
    """Remove a product. Returns True if something was deleted."""
    client = supabase_client._get_client()
    if client is None:
        mem = _mem_prod()
        before = len(mem)
        _mem_prod_replace([r for r in mem if r["id"] != pid])
        return len(_mem_prod()) < before
    try:
        client.table("products").delete().eq("id", pid).execute()
        return True
    except Exception as exc:  # pragma: no cover
        print(f"[catalog] delete failed: {exc}")
        return False


def _mem_prod_replace(new_list):
    global _mem_products
    _mem_products = new_list


def get_settings():
    return _settings()


def set_setting(key, value):
    if key not in ("pod_pack_price", "pod_pack_size"):
        raise ValueError("unknown setting")
    value = float(value) if key == "pod_pack_price" else int(value)
    client = supabase_client._get_client()
    if client is None:
        _mem_set()[key] = value
        return {key: value}
    try:
        client.table("settings").upsert({"key": key, "value": value}).execute()
        return {key: value}
    except Exception as exc:
        raise ValueError(f"save failed: {exc}")
