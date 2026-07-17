import { FALLBACK_CATALOG } from './data/products.js'

// In dev, Vite proxies "/api" → the Flask backend. In production (Vercel),
// set VITE_API_BASE to your Render backend, e.g. https://boobly-api.onrender.com/api
export const API_BASE = (import.meta.env.VITE_API_BASE || '/api').replace(/\/$/, '')
const BASE = API_BASE

export async function fetchCatalog() {
  try {
    const res = await fetch(`${BASE}/catalog`)
    if (!res.ok) throw new Error('bad status')
    return await res.json()
  } catch (e) {
    console.warn('[boobly] API offline, using local catalog')
    return FALLBACK_CATALOG
  }
}

/**
 * Start a Stripe Checkout session and redirect the browser to it.
 * Returns { redirected: true } on success, or { offline: true } when Stripe
 * isn't configured so the caller can fall back to the simulated-order flow.
 */
export async function startCheckout(payload) {
  try {
    const res = await fetch(`${BASE}/checkout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (res.status === 503) return { offline: true } // Stripe not configured
    if (!res.ok) {
      // Backend reachable but the request failed (e.g. Stripe error): surface it
      // so the shopper can retry — do NOT fake a success or clear their cart.
      const err = await res.json().catch(() => ({}))
      return { error: err.error || 'Checkout failed. Please try again.' }
    }
    const { url } = await res.json()
    if (!url) return { error: 'Checkout failed. Please try again.' }
    window.location.href = url
    return { redirected: true }
  } catch (e) {
    // Network error / backend unreachable → fall back to the demo flow.
    console.warn('[boobly] checkout API unreachable, using demo flow')
    return { offline: true }
  }
}

export async function subscribeNewsletter(email) {
  try {
    const res = await fetch(`${BASE}/subscribe`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      return { error: err.error || 'Could not subscribe' }
    }
    return { ok: true }
  } catch (e) {
    // Offline: don't block the celebratory UX.
    return { ok: true, offline: true }
  }
}

export async function trackOrder(id, email) {
  try {
    const res = await fetch(`${BASE}/track?id=${encodeURIComponent(id)}&email=${encodeURIComponent(email)}`)
    const data = await res.json().catch(() => ({}))
    if (!res.ok) return { error: data.error || 'No matching order found' }
    return data
  } catch (e) {
    return { error: 'Tracking is offline right now — try again soon.' }
  }
}

export async function placeOrder(payload) {
  try {
    const res = await fetch(`${BASE}/orders`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.error || 'Order failed')
    }
    return await res.json()
  } catch (e) {
    // Offline demo mode: fake a successful order so the UX still completes.
    console.warn('[boobly] order API offline, simulating success')
    return {
      ok: true,
      offline: true,
      order: { id: 'demo-' + Date.now(), status: 'received', ...payload },
    }
  }
}
