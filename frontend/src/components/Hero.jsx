import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'

// Each slide pairs an image with its own caption. Add more here and the
// rotation / dots adapt automatically.
const SLIDES = [
  {
    img: '/getBooblyMain.png',
    alt: 'Boobly bottles on the beach',
    pill: '🌈 Stay Fresh, Stay You',
    title: (
      <>
        Make water <span className="grad">WAY</span>
        <br />more fun
      </>
    ),
    sub: 'One color-pop bottle. Twelve crazy-good aroma pods. Zero sugar, zero calories — just clip in a flavor and sip your rainbow.',
  },
  {
    img: '/3flavourRedesign.png',
    alt: 'The redesigned trio of Boobly bottles',
    pill: '🎨 New Look, Same Fizz',
    title: (
      <>
        Three shades of <span className="grad">wow</span>
        <br />in your hand
      </>
    ),
    sub: 'Meet the redesigned trio — grab-and-go bottles in poppin’ new colors, each ready for any of your 12 flavor pods.',
  },
]

const ROTATE_MS = 5200

export default function Hero() {
  const [i, setI] = useState(0)

  useEffect(() => {
    const id = setInterval(() => setI((n) => (n + 1) % SLIDES.length), ROTATE_MS)
    return () => clearInterval(id)
  }, [])

  const slide = SLIDES[i]

  return (
    <header id="top" className="hero">
      <div className="wrap">
        <motion.div
          className="hero-card"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: 'easeOut' }}
        >
          {/* Crossfading image with a slow Ken-Burns zoom */}
          <AnimatePresence>
            <motion.img
              key={slide.img}
              className="hero-img"
              src={slide.img}
              alt={slide.alt}
              initial={{ opacity: 0, scale: 1.12 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.04 }}
              transition={{
                opacity: { duration: 1.1 },
                scale: { duration: ROTATE_MS / 1000, ease: 'linear' },
              }}
            />
          </AnimatePresence>
          <div className="hero-overlay" />

          <div className="hero-stats">
            {[
              { b: '12', s: 'Flavors' },
              { b: '0g', s: 'Sugar' },
              { b: '∞', s: 'Refills' },
            ].map((c, idx) => (
              <motion.div
                key={c.s}
                className="stat-chip"
                initial={{ opacity: 0, x: 30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + idx * 0.12 }}
              >
                <b>{c.b}</b>
                <span>{c.s}</span>
              </motion.div>
            ))}
          </div>

          <div className="hero-content">
            {/* Swapping caption — slides up as it crossfades */}
            <AnimatePresence mode="popLayout">
              <motion.div
                key={i}
                className="hero-caption"
                initial={{ opacity: 0, y: 26 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -18 }}
                transition={{ duration: 0.6, ease: 'easeOut' }}
              >
                <div className="hero-pill">{slide.pill}</div>
                <h1>{slide.title}</h1>
                <p className="sub">{slide.sub}</p>
              </motion.div>
            </AnimatePresence>

            <div className="hero-cta">
              <a className="btn btn-primary" href="#flavors">Pick your flavors →</a>
              <a className="btn btn-ghost" href="#bundles">See bundles</a>
            </div>

            <div className="hero-dots" role="tablist" aria-label="Hero slides">
              {SLIDES.map((s, idx) => (
                <button
                  key={s.img}
                  type="button"
                  className={`hero-dot${idx === i ? ' active' : ''}`}
                  aria-label={`Show slide ${idx + 1}`}
                  aria-selected={idx === i}
                  onClick={() => setI(idx)}
                />
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </header>
  )
}
