"""Quick Supabase connectivity check.

Run from the backend folder (with your venv active) AFTER filling in
backend/.env with SUPABASE_URL / SUPABASE_KEY and running schema.sql:

    python test_supabase.py

It verifies the client connects, inserts a throwaway order, reads it back,
then deletes it so your table stays clean.
"""
import os
import uuid

from dotenv import load_dotenv

load_dotenv()

URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")


def main():
    print("1) Checking env vars…")
    if not (URL and KEY):
        print("   ✗ SUPABASE_URL / SUPABASE_KEY missing. Copy .env.example to .env and fill them in.")
        return
    print(f"   ✓ URL = {URL}")
    print(f"   ✓ KEY = {KEY[:8]}…{KEY[-4:]} ({len(KEY)} chars)")

    print("2) Creating client…")
    from supabase import create_client
    client = create_client(URL, KEY)
    print("   ✓ client created")

    probe_id = str(uuid.uuid4())
    print(f"3) Inserting probe order {probe_id}…")
    client.table("orders").insert({
        "id": probe_id,
        "total": 0,
        "items": [{"name": "connectivity probe", "qty": 1, "price": 0}],
        "customer": {"name": "probe", "email": "probe@example.com"},
    }).execute()
    print("   ✓ insert ok")

    print("4) Reading it back…")
    res = client.table("orders").select("*").eq("id", probe_id).execute()
    assert res.data, "probe row not found"
    print(f"   ✓ read ok — status={res.data[0].get('status')}")

    print("5) Cleaning up probe row…")
    client.table("orders").delete().eq("id", probe_id).execute()
    print("   ✓ deleted")

    print("\n🎉 Supabase is connected and working.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\n✗ FAILED: {type(exc).__name__}: {exc}")
        print("\nCommon causes:")
        print("  • schema.sql not run yet (table 'orders' doesn't exist)")
        print("  • RLS policies block the anon key for insert/delete → use the service_role key for this test")
        print("  • Wrong project URL or key")
