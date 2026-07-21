import { motion } from 'framer-motion'
import { useCart } from '../context/CartContext.jsx'
import { burstFrom } from './Confetti.jsx'
import { hype } from '../lib/hype.js'

export default function Bundles({ bundles, onToast }) {
  const { add } = useCart()

  function addBundle(b, e) {
    burstFrom(e)
    add({
      key: `bundle-${b.id}`,
      id: b.id,
      type: 'bundle',
      name: b.name,
      emoji: b.emoji,
      color: '#a05cfa',
      image: b.image,
      price: b.price,
      qty: 1,
    })
    onToast?.(`${b.emoji} ${b.name} added!`)
  }

  return (
    <section id="bundles" className="section">
      <div className="wrap">
        <div className="section-head">
          <div className="eyebrow">Save More</div>
          <h2>Grab a bundle 🎁</h2>
          <p>Mix bottles and flavor packs — the more you grab, the more you save.</p>
        </div>
        <div className="bundle-grid">
          {bundles.map((b, i) => {
            const hasCompare = b.compare_at && b.compare_at > b.price
            const save = hasCompare ? Math.round(((b.compare_at - b.price) / b.compare_at) * 100) : 0
            const { rating, count } = hype(b.id)
            return (
              <motion.div
                key={b.id}
                className="pcard"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                <div
                  className="pcard-hero"
                  style={{ background: 'linear-gradient(150deg, #a05cfa, #f72585)' }}
                >
                  {b.badge && <div className="pcard-flag">{b.badge}</div>}
                  {b.image
                    ? <div className="pcard-img" style={{ backgroundImage: `url("${b.image}")` }} />
                    : <div className="pcard-emoji">{b.emoji}</div>}
                  <div className="pcard-rating">
                    <span className="stars">★★★★★</span> {rating}
                    <span className="count">· {count} squads</span>
                  </div>
                </div>
                <div className="pcard-body">
                  <div className="pcard-eyebrow">Boobly Bundle</div>
                  <h3 className="pcard-title">{b.name}</h3>
                  {hasCompare && <span className="pcard-badge">🎉 Save {save}% today</span>}
                  <p className="pcard-desc">{b.desc}</p>
                  <div className="pcard-foot">
                    <div className="pcard-price">
                      ${b.price.toFixed(2)}
                      {hasCompare && (
                        <span className="compare">${b.compare_at.toFixed(2)}</span>
                      )}
                    </div>
                    <button className="btn btn-primary" onClick={(e) => addBundle(b, e)}>
                      Add bundle
                    </button>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
