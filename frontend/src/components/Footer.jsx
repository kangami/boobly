import { useState } from 'react'
import { subscribeNewsletter } from '../api.js'

export default function Footer({ onToast, onTrack }) {
  const [email, setEmail] = useState('')
  const [busy, setBusy] = useState(false)

  async function subscribe(e) {
    e.preventDefault()
    if (!email || busy) return
    setBusy(true)
    const res = await subscribeNewsletter(email)
    setBusy(false)
    if (res.error) {
      onToast?.(`😅 ${res.error}`)
      return
    }
    onToast?.('🎉 You\'re in! Watch your inbox for flavor drops.')
    setEmail('')
  }

  return (
    <>
      <section className="section">
        <div className="wrap">
          <div className="cta-band">
            <h2>Join the Boobly squad 🌈</h2>
            <p>Get 10% off your first bottle + first dibs on new flavors.</p>
            <form className="news-form" onSubmit={subscribe}>
              <input
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <button className="btn btn-dark" type="submit" disabled={busy}>
                {busy ? 'Joining…' : 'Get my 10% →'}
              </button>
            </form>
          </div>
        </div>
      </section>

      <footer className="footer">
        <div className="wrap">
          <div className="footer-top">
            <div className="footer-col" style={{ maxWidth: 280 }}>
              <div className="logo" style={{ fontSize: 28 }}>boobly</div>
              <p style={{ opacity: 0.7, marginTop: 8 }}>
                Stay Fresh, Stay You. Sugar-free flavor for your water, in 12 wild colors.
              </p>
            </div>
            <div className="footer-col">
              <h5>Shop</h5>
              <a href="#flavors">Flavor pods</a>
              <a href="#bottles">Bottles</a>
              <a href="#bundles">Bundles</a>
            </div>
            <div className="footer-col">
              <h5>Help</h5>
              <a href="#how">How it works</a>
              <a href="#" onClick={(e) => { e.preventDefault(); onTrack?.() }}>Track my order</a>
              <a href="#">Contact us</a>
            </div>
            <div className="footer-col">
              <h5>Follow</h5>
              <a href="#">TikTok</a>
              <a href="#">Instagram</a>
              <a href="#">YouTube</a>
            </div>
          </div>
          <div className="footer-bottom">
            © {new Date().getFullYear()} Boobly. Made with 💧 for thirsty humans. Zero sugar, all fun.
          </div>
        </div>
      </footer>
    </>
  )
}
