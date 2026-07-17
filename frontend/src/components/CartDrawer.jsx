import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { useCart } from '../context/CartContext.jsx'
import { placeOrder, startCheckout } from '../api.js'

const CUSTOMER_KEY = 'boobly_customer'
// Mirrors the backend (stripe_client.py). The exact fee is charged on Stripe's
// checkout page; this is just the storefront hint before redirect.
const DELIVERY_FEE = 8.95
const FREE_SHIP_THRESHOLD = 65

// Load the shopper's saved name/email (empty on their first visit).
function loadCustomer() {
  try {
    const saved = JSON.parse(localStorage.getItem(CUSTOMER_KEY))
    return { name: saved?.name || '', email: saved?.email || '' }
  } catch {
    return { name: '', email: '' }
  }
}

function saveCustomer({ name, email }) {
  try {
    localStorage.setItem(CUSTOMER_KEY, JSON.stringify({ name, email }))
  } catch {
    /* private mode / storage full — pre-fill just won't persist */
  }
}

export default function CartDrawer() {
  const { items, open, setOpen, count, total, inc, dec, remove, clear } = useCart()
  const [stage, setStage] = useState('cart') // cart | checkout | done
  // Pre-fill name/email from the shopper's last checkout so they don't retype it.
  const [form, setForm] = useState(loadCustomer)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  // Never leave the drawer stuck on "Placing order…" — reset the transient
  // state whenever it (re)opens, including when restored from the back/forward
  // cache after returning from Stripe.
  useEffect(() => {
    if (open) {
      setBusy(false)
      setError('')
    }
  }, [open])

  function close() {
    setOpen(false)
    setTimeout(() => setStage('cart'), 300)
  }

  async function submit(e) {
    e.preventDefault()
    if (busy) return // guard against double-submit
    setBusy(true)
    setError('')
    try {
      // Remember who they are for next time (they can still edit it above).
      saveCustomer(form)
      const payload = {
        items: items.map((i) => ({ id: i.id, name: i.name, type: i.type, qty: i.qty, price: i.price, variant: i.variant || null })),
        customer: form,
      }

      // Try real Stripe Checkout first. On success the browser redirects away to
      // Stripe's hosted page and the cart is cleared on the success return (App.jsx).
      const result = await startCheckout(payload)
      if (result.redirected) return // navigating to Stripe; nothing more to do here
      if (result.error) {
        // Real failure — keep the cart intact so they can retry.
        setError(result.error)
        return
      }

      // Genuine offline/demo mode only (backend unreachable / Stripe not set up).
      await placeOrder(payload)
      setStage('done')
      clear()
      window.boobBurst?.(window.innerWidth - 180, 120)
    } finally {
      // Always re-enable the button, even on the redirect path (harmless if we
      // navigate away, essential if the user comes back).
      setBusy(false)
    }
  }

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            key="cart-overlay"
            className="drawer-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={close}
          />
          <motion.aside
            key="cart-drawer"
            className="drawer"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', stiffness: 320, damping: 34 }}
          >
            <div className="drawer-head">
              <h3>
                {stage === 'cart' && `Your bag 🛍️`}
                {stage === 'checkout' && `Checkout 💳`}
                {stage === 'done' && `Woohoo! 🎉`}
              </h3>
              <button className="drawer-close" onClick={close}>✕</button>
            </div>

            {stage === 'done' ? (
              <div className="order-done">
                <div className="big">🎉</div>
                <h3 style={{ fontSize: 26, margin: '12px 0 8px' }}>Order placed!</h3>
                <p style={{ opacity: 0.7 }}>
                  Thanks {form.name || 'friend'}! Your rainbow of flavor is on its way.
                  We sent a confirmation to {form.email || 'your inbox'}.
                </p>
                <button className="btn btn-primary" style={{ marginTop: 22 }} onClick={close}>
                  Keep shopping
                </button>
              </div>
            ) : count === 0 ? (
              <div className="empty-cart">
                <div className="big">🫙</div>
                <p>Your bag is thirsty!<br />Add some flavor pods to get started.</p>
                <button className="btn btn-primary" style={{ marginTop: 18 }} onClick={close}>
                  Browse flavors
                </button>
              </div>
            ) : (
              <>
                <div className="drawer-body">
                  {stage === 'checkout' && (
                    <form className="checkout-fields" onSubmit={submit} id="checkout-form">
                      <input
                        placeholder="Your name"
                        value={form.name}
                        onChange={(e) => setForm({ ...form, name: e.target.value })}
                        required
                      />
                      <input
                        type="email"
                        placeholder="Email for your receipt"
                        value={form.email}
                        onChange={(e) => setForm({ ...form, email: e.target.value })}
                        required
                      />
                    </form>
                  )}
                  <AnimatePresence mode="popLayout" initial={false}>
                    {items.map((i) => (
                      <motion.div
                        layout
                        key={i.key}
                        className="cart-item"
                        initial={{ opacity: 0, x: 30 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 40, transition: { duration: 0.18 } }}
                      >
                        <div
                          className="cart-thumb"
                          style={
                            i.image
                              ? { backgroundImage: `url(${i.image})`, backgroundSize: 'cover', backgroundPosition: 'center' }
                              : { background: i.color || '#a05cfa' }
                          }
                        >
                          {!i.image && (i.emoji || '💧')}
                        </div>
                        <div className="info">
                          <b>{i.name}</b>
                          <span>${Number(i.price || 0).toFixed(2)} each</span>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <div className="qty">
                            <button onClick={() => dec(i.key)}>−</button>
                            <b>{i.qty}</b>
                            <button onClick={() => inc(i.key)}>+</button>
                          </div>
                          <button className="cart-remove" onClick={() => remove(i.key)}>remove</button>
                        </div>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                </div>

                <div className="drawer-foot">
                  <div className="drawer-delivery">
                    <span>Delivery</span>
                    {total >= FREE_SHIP_THRESHOLD ? (
                      <b style={{ color: '#12b76a' }}>Free 🎉</b>
                    ) : (
                      <b>from ${DELIVERY_FEE.toFixed(2)}</b>
                    )}
                  </div>
                  {total < FREE_SHIP_THRESHOLD && (
                    <p className="drawer-ship-hint">
                      Add ${(FREE_SHIP_THRESHOLD - total).toFixed(2)} more for free delivery!
                    </p>
                  )}
                  <div className="drawer-total">
                    <span>Subtotal</span>
                    <b>${total.toFixed(2)}</b>
                  </div>
                  {stage === 'checkout' && error && (
                    <p className="checkout-err">{error}</p>
                  )}
                  {stage === 'cart' ? (
                    <button className="btn btn-primary" onClick={() => setStage('checkout')}>
                      Checkout →
                    </button>
                  ) : (
                    <button
                      className="btn btn-primary"
                      type="submit"
                      form="checkout-form"
                      disabled={busy}
                    >
                      {busy ? 'Placing order…' : `Pay $${total.toFixed(2)} 🎉`}
                    </button>
                  )}
                </div>
              </>
            )}
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  )
}
