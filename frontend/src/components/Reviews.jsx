import { motion } from 'framer-motion'

const REVIEWS = [
  { name: 'Maya', age: '14', color: '#ff5e8a', emoji: '🍓', text: 'The strawberry-kiwi one is unreal. I bring my Boobly everywhere and everyone asks about it!' },
  { name: 'Leo', age: '11', color: '#48cae4', emoji: '🫐', text: 'I used to forget to drink water. Now I finish the whole bottle because blueberry tea is so good.' },
  { name: 'Zoé', age: '16', color: '#a05cfa', emoji: '🥭', text: 'Mango tea + the purple ocean bottle = my whole personality. Zero sugar is a huge plus.' },
  { name: 'Sam', age: '9', color: '#9be15d', emoji: '🍋', text: 'Lemon is my favorite! It tastes like candy but it is just water. So cool.' },
]

export default function Reviews() {
  return (
    <section className="section">
      <div className="wrap">
        <div className="section-head">
          <div className="eyebrow">The Squad Says</div>
          <h2>Loved by thousands of sippers 💛</h2>
          <p>4.9/5 average from over 12,000 happy Boobly fans.</p>
        </div>
        <div className="review-grid">
          {REVIEWS.map((r, i) => (
            <motion.div
              key={r.name}
              className="review-card"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08 }}
            >
              <div className="review-stars">★★★★★</div>
              <p>"{r.text}"</p>
              <div className="review-who">
                <div className="review-ava" style={{ background: r.color }}>{r.emoji}</div>
                <div>
                  <b>{r.name}</b>
                  <span>Age {r.age} · Verified sipper</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
