# 🌈 Boobly — Stay Fresh, Stay You

A bright, playful e-commerce storefront for **Boobly**, the color-pop water bottle
with 12 sugar-free aroma pods. Designed to make 6–17 year olds go *wooow* 🤩

| Layer | Tech |
|-------|------|
| Frontend | React 18 + Vite + Framer Motion |
| Backend | Flask (REST API) |
| Storage | Supabase (Postgres + Storage), with an in-memory fallback |

## ✨ What's inside

- **Rainbow, glassmorphic, animated UI** — floating gradient blobs, hue-shifting logo,
  a scrolling marquee, bobbing bottles, sparkly **confetti bursts** on every add-to-cart.
- **Flavor Lab** — all 12 aroma pods as juicy gradient cards (filter by Fruit / Tea / Classic),
  each with a tap-to-open detail modal.
- **Bottle picker** + **Bundles** (Starter Kit, Squad Pack, Flavor Vault).
- **Animated cart drawer** with quantity controls, a mini checkout, and an order-success celebration.
- **Reviews, How-it-works, newsletter** — all kid-friendly copy.
- Cart persists in `localStorage`; the storefront still works fully even if the API is offline.

## 🚀 Run it

### 1. Backend (Flask)
```bash
cd backend
python -m venv venv
# Windows:  venv\Scripts\activate
# macOS/Linux:  source venv/bin/activate
pip install -r requirements.txt
python app.py            # http://localhost:5000
```
Runs out of the box with an in-memory order store. To persist orders to Supabase,
copy `.env.example` to `.env`, add your `SUPABASE_URL` / `SUPABASE_KEY`, and run
`schema.sql` in the Supabase SQL editor.

### 2. Frontend (React)
```bash
cd frontend
npm install
npm run dev              # http://localhost:5173
```
Vite proxies `/api` → `http://localhost:5000`, so run the backend alongside it
(or just run the frontend alone — it falls back to the local catalog).

## 💳 Payments, email, admin & tracking

- **Stripe Checkout** — set `STRIPE_SECRET_KEY` (+ `STRIPE_WEBHOOK_SECRET`) in
  `backend/.env`. Prices are resolved **server-side** from `products.py` (the
  client-sent price is ignored). Stripe collects a validated **shipping address**.
  Locally, forward webhooks with: `stripe listen --forward-to localhost:5000/api/webhook`.
- **Order emails** — set `RESEND_API_KEY` to send confirmation + status emails
  (otherwise they're logged, app still works).
- **Admin dashboard** — visit `http://localhost:5000/admin`, sign in with
  `ADMIN_API_TOKEN`. **Orders** tab: view orders + update status (emails the
  customer). **Products** tab: add / edit / delete products, change prices and the
  pod pack price. Catalog is DB-backed (`catalog_store.py`, Supabase `products` /
  `settings` tables, auto-seeded from `products.py`); price edits are the source of
  truth for both the storefront and checkout.
- **Order tracking** — customers use the **Track my order** link in the footer
  (order ref + email); no account needed.

Generate an admin token: `python -c "import secrets; print(secrets.token_urlsafe(32))"`.
See `backend/.env.example` for every variable.

## ☁️ Deploy (Vercel + Render)

**Backend → Render** (`render.yaml` blueprint, or a Python web service with
root `backend/`):
- Start command: `gunicorn app:app --workers 1 --threads 8 --timeout 120 --bind 0.0.0.0:$PORT`
  (1 worker keeps the in-process SSE broker consistent; threads serve the live streams).
- Health check: `/api/health`.
- Set env vars: `SUPABASE_URL`, `SUPABASE_KEY` (service_role), `STRIPE_SECRET_KEY`,
  `STRIPE_WEBHOOK_SECRET`, `ADMIN_API_TOKEN`, `RESEND_API_KEY`, `EMAIL_FROM`,
  `SHIP_COUNTRIES`, `PUBLIC_BASE_URL` (your Vercel URL), `CORS_ORIGINS` (your Vercel URL).

**Frontend → Vercel** (root directory `frontend/`, Vite preset auto-detected):
- Env var: `VITE_API_BASE=https://<your-render-service>.onrender.com/api`.

After both are live: register the Stripe webhook at `https://<render>/api/webhook`,
and upload product images from `/admin` so they land in Supabase Storage
(Render's disk is ephemeral). Note: Render free instances cold-start after idle —
the storefront's SSE reconnects automatically.

## 🗂️ Structure
```
boobly/
├── assets/                 # original product images
├── backend/
│   ├── app.py              # Flask API (catalog + orders)
│   ├── products.py         # catalog: 3 bottles, 12 pods, 3 bundles
│   ├── supabase_client.py  # Supabase wrapper + memory fallback
│   ├── schema.sql          # Supabase table + policies
│   └── requirements.txt
└── frontend/
    ├── public/             # getBooblyMain.png, booblyPerfume.jpg
    └── src/
        ├── App.jsx
        ├── api.js
        ├── context/CartContext.jsx
        ├── data/products.js
        └── components/      # Hero, FlavorGrid, Bundles, CartDrawer, Confetti …
```

## 🧃 The 12 flavors
Cherry·Orange·Apple · Strawberry·Blueberry · Strawberry·Kiwi · Blueberries ·
Passion Fruit · Lemon · Strawberry · Cola · Blueberry Tea · Honey Tea ·
Blackberry · Mango Tea
