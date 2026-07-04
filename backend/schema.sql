-- Boobly Supabase schema.
-- Run this in the Supabase SQL editor for your project.

-- Note: `id` is text (not uuid) because a paid order reuses its Stripe Checkout
-- session id (cs_…) as the primary key, which makes webhook inserts idempotent.
-- Demo/offline orders use a uuid string, which also fits a text column.
create table if not exists orders (
  id text primary key default gen_random_uuid()::text,
  created_at timestamptz not null default now(),
  status text not null default 'received',
  total numeric(10,2) not null default 0,
  items jsonb not null default '[]'::jsonb,
  customer jsonb not null default '{}'::jsonb,
  shipping_address jsonb not null default '{}'::jsonb
);

-- ---------------------------------------------------------------------------
-- Migrations for tables created on an earlier version of this schema.
-- Safe to run repeatedly.
-- ---------------------------------------------------------------------------
-- 1) Add the shipping address column.
alter table orders add column if not exists shipping_address jsonb not null default '{}'::jsonb;

-- 2) Convert id from uuid -> text so paid orders can use their Stripe session id.
alter table orders alter column id drop default;
alter table orders alter column id type text using id::text;
alter table orders alter column id set default gen_random_uuid()::text;

-- ---------------------------------------------------------------------------
-- Catalog: products + settings (managed from the /admin dashboard).
-- The backend auto-seeds these from products.py the first time they're empty.
-- ---------------------------------------------------------------------------
create table if not exists products (
  id text primary key,
  kind text not null check (kind in ('bottle', 'pod', 'bundle')),
  name text not null,
  price numeric(10,2) not null default 0,
  active boolean not null default true,
  position int not null default 0,
  data jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

create table if not exists settings (
  key text primary key,
  value jsonb not null default '{}'::jsonb
);

-- Newsletter signups from the "Join the Boobly squad" form.
create table if not exists subscribers (
  email text primary key,
  created_at timestamptz not null default now()
);

alter table products enable row level security;
alter table settings enable row level security;
alter table subscribers enable row level security;
-- No anon policies: the backend reads/writes with the service_role key, which
-- bypasses RLS. The public key can't touch the catalog directly.

-- Optional: a storage bucket for product imagery.
-- In the Supabase dashboard create a public bucket named "boobly-media"
-- and upload getBooblyMain.png and booblyPerfume.jpg, then reference their
-- public URLs from the frontend if you prefer hosted assets.

-- ---------------------------------------------------------------------------
-- Row Level Security
-- ---------------------------------------------------------------------------
-- The Flask backend talks to Supabase with the SERVICE_ROLE key, which bypasses
-- RLS entirely. So we keep RLS ON and grant the public `anon` role NOTHING —
-- orders (names, emails, addresses) are never readable with the public key.
alter table orders enable row level security;

-- Remove the permissive demo policies from earlier versions if present.
drop policy if exists "orders insert" on orders;
drop policy if exists "orders read" on orders;

-- (Intentionally no anon policies: with RLS enabled and no policy, the anon
--  role is denied. All access goes through the backend's service_role key.)
