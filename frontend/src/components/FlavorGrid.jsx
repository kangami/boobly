import { useMemo, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { useCart } from '../context/CartContext.jsx'
import { burstFrom } from './Confetti.jsx'
import { hype } from '../lib/hype.js'

const FAMILIES = ['All', 'Fruit', 'Tea', 'Classic']

// Products created from the DB/admin may not have a gradient — fall back to the
// item's color (or a brand default) so the storefront never crashes.
function gradientCss(item) {
  const g = Array.isArray(item.gradient) && item.gradient.length >= 2
    ? item.gradient
    : [item.color || '#a05cfa', item.color || '#f72585']
  return `linear-gradient(150deg, ${g[0]}, ${g[1]})`
}

export default function FlavorGrid({ flavors, podPrice, podSize, onToast }) {
  const { add } = useCart()
  const [filter, setFilter] = useState('All')
  const [active, setActive] = useState(null)

  const shown = useMemo(
    () => (filter === 'All' ? flavors : flavors.filter((f) => f.family === filter)),
    [flavors, filter],
  )

  function addFlavor(flavor, e) {
    e?.stopPropagation()
    burstFrom(e)
    add({
      key: `pod-${flavor.id}`,
      id: flavor.id,
      type: 'pod',
      name: `${flavor.name} pods`,
      emoji: flavor.emoji,
      color: flavor.color,
      image: flavor.image,
      price: podPrice,
      qty: 1,
    })
    onToast?.(`${flavor.emoji} ${flavor.name} added!`)
  }

  return (
    <section id="flavors" className="section">
      <div className="wrap">
        <div className="section-head">
          <div className="eyebrow">The Flavor Lab</div>
          <h2>Pick your aroma pods</h2>
          <p>Each pack has {podSize} cartridges. Clip one in, swap anytime, taste the rainbow.</p>
        </div>

        <div className="filters">
          {FAMILIES.map((f) => (
            <button
              key={f}
              className={`chip ${filter === f ? 'active' : ''}`}
              onClick={() => setFilter(f)}
            >
              {f}
            </button>
          ))}
        </div>

        <motion.div layout className="flavor-grid">
          <AnimatePresence>
            {shown.map((flavor) => {
              const { rating, count } = hype(flavor.id)
              return (
                <motion.div
                  key={flavor.id}
                  layout
                  initial={{ opacity: 0, scale: 0.85 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.85 }}
                  transition={{ type: 'spring', stiffness: 260, damping: 22 }}
                  className="pcard"
                  style={{ cursor: 'pointer' }}
                  onClick={() => setActive(flavor)}
                >
                  <div className="pcard-hero" style={{ background: gradientCss(flavor) }}>
                    <div className="pcard-flag">{flavor.family || 'Fruit'}</div>
                    {flavor.image
                      ? <div className="pcard-img" style={{ backgroundImage: `url(${flavor.image})` }} />
                      : <div className="pcard-emoji">{flavor.emoji}</div>}
                    <div className="pcard-rating">
                      <span className="stars">★★★★★</span> {rating}
                      <span className="count">· {count} sips</span>
                    </div>
                  </div>
                  <div className="pcard-body">
                    <div className="pcard-eyebrow">Aroma Pod</div>
                    <h3 className="pcard-title">{flavor.name}</h3>
                    <span className="pcard-badge">
                      🚫 Zero sugar{flavor.vitamins ? ' · B Vitamins' : ''}{flavor.caffeine ? ' · Caffeine' : ''}
                    </span>
                    <p className="pcard-desc">{flavor.notes}</p>
                    <div className="pcard-foot">
                      <div className="pcard-price">
                        ${podPrice.toFixed(2)}
                        <span className="save">/ {podSize}-pack</span>
                      </div>
                      <button
                        className="pcard-add"
                        style={{ background: gradientCss(flavor) }}
                        aria-label={`Add ${flavor.name}`}
                        onClick={(e) => addFlavor(flavor, e)}
                      >
                        +
                      </button>
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </AnimatePresence>
        </motion.div>
      </div>

      <FlavorModal
        flavor={active}
        podPrice={podPrice}
        podSize={podSize}
        onClose={() => setActive(null)}
        onAdd={addFlavor}
      />
    </section>
  )
}

function FlavorModal({ flavor, podPrice, podSize, onClose, onAdd }) {
  return (
    <AnimatePresence>
      {flavor && (
        <motion.div
          className="modal-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <motion.div
            className="modal"
            initial={{ scale: 0.8, y: 30 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.8, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 300, damping: 25 }}
            onClick={(e) => e.stopPropagation()}
          >
            <div
              className="modal-top"
              style={
                flavor.image
                  ? {
                      backgroundImage: `linear-gradient(180deg, rgba(0,0,0,0.15), rgba(0,0,0,0.55)), url(${flavor.image})`,
                      backgroundSize: 'cover',
                      backgroundPosition: 'center',
                    }
                  : { background: gradientCss(flavor) }
              }
            >
              {!flavor.image && <div className="emoji">{flavor.emoji}</div>}
              <h2>{flavor.name}</h2>
            </div>
            <div className="modal-body">
              <p>{flavor.notes}. Drop a cartridge into any Boobly bottle, give it a
                shake, and enjoy a refreshing burst of {(flavor.family || 'fruit').toLowerCase()} flavor —
                with zero sugar and zero calories.</p>
              <div className="modal-meta">
                <span className="meta-pill">🚫 Zero sugar</span>
                <span className="meta-pill">⚡ Zero calories</span>
                <span className="meta-pill">🌿 Natural flavors</span>
                {flavor.vitamins && <span className="meta-pill">💊 B Vitamins</span>}
                {flavor.caffeine && <span className="meta-pill">☕ Caffeine</span>}
                <span className="meta-pill">📦 {podSize} cartridges</span>
              </div>
              <button
                className="btn btn-primary"
                onClick={(e) => { onAdd(flavor, e); onClose() }}
              >
                Add pack — ${podPrice.toFixed(2)}
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
