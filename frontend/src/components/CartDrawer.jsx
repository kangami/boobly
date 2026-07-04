import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { useCart } from '../context/CartContext.jsx'
import { placeOrder, startCheckout } from '../api.js'

export default function CartDrawer() {
  const { items, open, setOpen, count, total, inc, dec, remove, clear } = useCart()
  const [stage, setStage] = useState('cart') // cart | checkout | done
  const [form, setForm] = useState({ name: '', email: '' })
  const [busy, setBusy] = useState(false)

  function close() {
    setOpen(false)
    setTimeout(() => setStage('cart'), 300)
  }

  async function submit(e) {
    e.preventDefault()
    setBusy(true)
    const payload = {
      items: items.map((i) => ({ id: i.id, name: i.name, type: i.type, qty: i.qty, price: i.price })),
      customer: form,
    }

    // Try real Stripe Checkout first. On success the browser redirects away to
    // Stripe's hosted page and the cart is cleared on the success return (App.jsx).
    const result = await startCheckout(payload)
    if (result.redirected) return // navigating to Stripe; nothing more to do here

    // Stripe not configured / offline → keep the demo flow working.
    await placeOrder(payload)
    setBusy(false)
    setStage('done')
    clear()
    window.boobBurst?.(window.innerWidth - 180, 120)
  }

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            className="drawer-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={close}
          />
          <motion.aside
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
                  {items.map((i) => (
                    <motion.div layout key={i.key} className="cart-item">
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
                        <span>${i.price.toFixed(2)} each</span>
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
                </div>

                <div className="drawer-foot">
                  <div className="drawer-total">
                    <span>Total</span>
                    <b>${total.toFixed(2)}</b>
                  </div>
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
