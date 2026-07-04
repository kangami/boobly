import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { fetchCatalog, API_BASE } from './api.js'
import { FALLBACK_CATALOG } from './data/products.js'
import { useCart } from './context/CartContext.jsx'

import Navbar from './components/Navbar.jsx'
import Hero from './components/Hero.jsx'
import Marquee from './components/Marquee.jsx'
import FlavorGrid from './components/FlavorGrid.jsx'
import Bottles from './components/Bottles.jsx'
import Bundles from './components/Bundles.jsx'
import HowItWorks from './components/HowItWorks.jsx'
import Reviews from './components/Reviews.jsx'
import Footer from './components/Footer.jsx'
import CartDrawer from './components/CartDrawer.jsx'
import TrackOrder from './components/TrackOrder.jsx'
import Confetti from './components/Confetti.jsx'

export default function App() {
  const [catalog, setCatalog] = useState(FALLBACK_CATALOG)
  const [toast, setToast] = useState(null)
  const [trackOpen, setTrackOpen] = useState(false)
  const { clear } = useCart()

  useEffect(() => {
    fetchCatalog().then(setCatalog)
  }, [])

  // Live catalog updates: when the admin changes a product, the backend pushes
  // an SSE 'change' event and we re-fetch — no page reload needed. EventSource
  // reconnects automatically if the connection drops.
  useEffect(() => {
    let es
    try {
      es = new EventSource(`${API_BASE}/events`)
      es.addEventListener('change', () => fetchCatalog().then(setCatalog))
    } catch {
      // EventSource unsupported or blocked — storefront still works, just not live.
    }
    return () => es && es.close()
  }, [])

  // Handle the redirect back from Stripe Checkout.
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const status = params.get('checkout')
    if (!status) return
    if (status === 'success') {
      clear()
      showToast('🎉 Payment successful — your flavor is on its way!')
      window.boobBurst?.(window.innerWidth / 2, 140)
    } else if (status === 'cancel') {
      showToast('Checkout cancelled — your bag is saved 💧')
    }
    // Strip the query params so a refresh doesn't re-trigger.
    window.history.replaceState({}, '', window.location.pathname)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function showToast(msg) {
    setToast(msg)
    clearTimeout(window.__boobToast)
    window.__boobToast = setTimeout(() => setToast(null), 2200)
  }

  return (
    <>
      <div className="bg-blobs">
        <div className="blob b1" />
        <div className="blob b2" />
        <div className="blob b3" />
        <div className="blob b4" />
      </div>

      <Confetti />
      <Navbar />
      <Hero />
      <Marquee />
      <FlavorGrid
        flavors={catalog.flavors}
        podPrice={catalog.pod_pack_price}
        podSize={catalog.pod_pack_size}
        onToast={showToast}
      />
      <Bottles bottles={catalog.bottles} onToast={showToast} />
      <Bundles bundles={catalog.bundles} onToast={showToast} />
      <HowItWorks />
      <Reviews />
      <Footer onToast={showToast} onTrack={() => setTrackOpen(true)} />
      <CartDrawer />
      <TrackOrder open={trackOpen} onClose={() => setTrackOpen(false)} />

      <AnimatePresence>
        {toast && (
          <motion.div
            className="toast"
            initial={{ opacity: 0, y: 30, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
          >
            {toast}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
