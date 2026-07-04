import { motion } from 'framer-motion'
import { useCart } from '../context/CartContext.jsx'
import { burstFrom } from './Confetti.jsx'
import { hype } from '../lib/hype.js'

function heroBg(b) {
  const g = Array.isArray(b.gradient) && b.gradient.length >= 2
    ? b.gradient
    : [b.color || '#5c7cfa', b.color || '#a05cfa']
  return `linear-gradient(150deg, ${g[0]}, ${g[1]})`
}

export default function Bottles({ bottles, onToast }) {
  const { add } = useCart()

  function addBottle(b, e) {
    burstFrom(e)
    add({
      key: `bottle-${b.id}`,
      id: b.id,
      type: 'bottle',
      name: b.name,
      emoji: b.emoji,
      color: b.color,
      image: b.image,
      price: b.price,
      qty: 1,
    })
    onToast?.(`${b.emoji} ${b.name} added!`)
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
          {bottles.map((b, i) => {
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
                <div className="pcard-hero" style={{ background: heroBg(b) }}>
                  {b.image
                    ? <div className="pcard-img" style={{ backgroundImage: `url(${b.image})` }} />
                    : <div className="pcard-emoji">{b.emoji}</div>}
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
                  <div className="pcard-foot">
                    <div className="pcard-price">${b.price.toFixed(2)}</div>
                    <button className="btn btn-primary" onClick={(e) => addBottle(b, e)}>
                      Add to bag
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
