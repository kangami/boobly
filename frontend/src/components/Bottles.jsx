import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { useCart } from '../context/CartContext.jsx'
import { burstFrom } from './Confetti.jsx'
import { hype } from '../lib/hype.js'

function heroBg(b) {
  const g = Array.isArray(b.gradient) && b.gradient.length >= 2
    ? b.gradient
    : [b.color || '#5c7cfa', b.color || '#a05cfa']
  return `linear-gradient(150deg, ${g[0]}, ${g[1]})`
}

function BottleCard({ b, i, onAdd }) {
  const { rating, count } = hype(b.id)
  // Only colour variants that actually have an image are selectable.
  const variants = Array.isArray(b.variants) ? b.variants.filter((v) => v && v.image) : []
  const [sel, setSel] = useState(0)
  const active = variants[sel]
  const activeImage = active?.image || b.image || ''

  return (
    <motion.div
      className="pcard"
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay: i * 0.1 }}
    >
      <div className="pcard-hero" style={{ background: heroBg(b) }}>
        <AnimatePresence mode="wait" initial={false}>
          <motion.div
            key={activeImage || 'emoji'}
            className="pcard-media"
            initial={{ opacity: 0, scale: 0.92 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.04 }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
          >
            {activeImage
              ? <div className="pcard-img" style={{ backgroundImage: `url(${activeImage})` }} />
              : <div className="pcard-emoji">{b.emoji}</div>}
          </motion.div>
        </AnimatePresence>
        <div className="pcard-rating">
          <span className="stars">★★★★★</span> {rating}
          <span className="count">· {count} sips</span>
        </div>
      </div>
      <div className="pcard-body">
        <div className="pcard-eyebrow">Boobly Bottle</div>
        <h3 className="pcard-title">{b.name}</h3>
        <span className="pcard-badge">💧 750ml · BPA-free · leak-proof</span>
        <p className="pcard-desc">{b.tagline}</p>
        {variants.length > 0 && (
          <div className="pcard-swatches" role="radiogroup" aria-label="Choose a color">
            {variants.map((v, idx) => (
              <button
                key={v.id}
                type="button"
                className={`swatch ${idx === sel ? 'active' : ''}`}
                style={{ background: v.color || '#ccc' }}
                onClick={() => setSel(idx)}
                aria-label={v.label}
                aria-pressed={idx === sel}
                title={v.label}
              />
            ))}
          </div>
        )}
        <div className="pcard-foot">
          <div className="pcard-price">${b.price.toFixed(2)}</div>
          <button
            className="btn btn-primary"
            onClick={(e) => onAdd(b, active, activeImage, e)}
          >
            Add to bag
          </button>
        </div>
      </div>
    </motion.div>
  )
}

export default function Bottles({ bottles, onToast }) {
  const { add } = useCart()

  function addBottle(b, variant, image, e) {
    burstFrom(e)
    add({
      key: `bottle-${b.id}${variant ? `-${variant.id}` : ''}`,
      id: b.id,
      type: 'bottle',
      name: variant ? `${b.name} — ${variant.label}` : b.name,
      variant: variant ? { id: variant.id, label: variant.label } : null,
      emoji: b.emoji,
      color: variant?.color || b.color,
      image: image || b.image,
      price: b.price,
      qty: 1,
    })
    onToast?.(`${b.emoji} ${b.name}${variant ? ` (${variant.label})` : ''} added!`)
  }

  return (
    <section id="bottles" className="section">
      <div className="wrap">
        <div className="section-head">
          <div className="eyebrow">The Bottle</div>
          <h2>Choose your color 🌈</h2>
          <p>BPA-free, 750ml, leak-proof flip cap with a built-in flavor chamber.</p>
        </div>
        <div className="bottle-row">
          {bottles.map((b, i) => (
            <BottleCard key={b.id} b={b} i={i} onAdd={addBottle} />
          ))}
        </div>
      </div>
    </section>
  )
}
