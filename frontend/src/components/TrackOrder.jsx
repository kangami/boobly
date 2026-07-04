import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { trackOrder } from '../api.js'

const STEPS = ['paid', 'packed', 'shipped', 'delivered']
const STEP_LABEL = { paid: 'Paid', packed: 'Packed', shipped: 'Shipped', delivered: 'Delivered' }

export default function TrackOrder({ open, onClose }) {
  const [form, setForm] = useState({ id: '', email: '' })
  const [order, setOrder] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(e) {
    e.preventDefault()
    setBusy(true)
    setError('')
    setOrder(null)
    const res = await trackOrder(form.id.trim(), form.email.trim())
    setBusy(false)
    if (res.error) setError(res.error)
    else setOrder(res)
  }

  function close() {
    onClose()
    setTimeout(() => { setOrder(null); setError(''); setForm({ id: '', email: '' }) }, 300)
  }

  const activeIdx = order ? STEPS.indexOf(order.status) : -1

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            className="drawer-overlay"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={close}
          />
          <motion.div
            className="track-modal"
            initial={{ opacity: 0, y: 30, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.96 }}
            transition={{ type: 'spring', stiffness: 320, damping: 30 }}
          >
            <div className="track-head">
              <h3>Track your order 📦</h3>
              <button className="drawer-close" onClick={close}>✕</button>
            </div>

            <form className="track-form" onSubmit={submit}>
              <input
                placeholder="Order reference"
                value={form.id}
                onChange={(e) => setForm({ ...form, id: e.target.value })}
                required
              />
              <input
                type="email"
                placeholder="Email used at checkout"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                required
              />
              <button className="btn btn-primary" type="submit" disabled={busy}>
                {busy ? 'Looking…' : 'Track it →'}
              </button>
            </form>

            {error && <p className="track-error">{error}</p>}

            {order && (
              <div className="track-result">
                {order.status === 'cancelled' ? (
                  <p className="track-error">This order was cancelled.</p>
                ) : (
                  <div className="track-steps">
                    {STEPS.map((s, i) => (
                      <div key={s} className={`track-step${i <= activeIdx ? ' done' : ''}`}>
                        <span className="dot" />
                        <span>{STEP_LABEL[s]}</span>
                      </div>
                    ))}
                  </div>
                )}
                <div className="track-summary">
                  <div><span>Status</span><b>{order.status}</b></div>
                  <div><span>Total</span><b>${Number(order.total || 0).toFixed(2)}</b></div>
                  <div><span>Items</span><b>{(order.items || []).reduce((n, i) => n + (i.qty || 0), 0)}</b></div>
                </div>
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
