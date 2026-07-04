import { motion } from 'framer-motion'

const STEPS = [
  { n: 1, e: '🍶', t: 'Fill it up', d: 'Pop water into your Boobly bottle tap, fountain, anywhere.' },
  { n: 2, e: '🧪', t: 'Clip a pod', d: 'Snap an aroma cartridge into the cap chamber. No spills.' },
  { n: 3, e: '🤩', t: 'Shake & sip', d: 'Give it a wiggle and taste a flavor-packed, sugar-free splash.' },
  { n: 4, e: '🔁', t: 'Swap anytime', d: 'Bored? Switch flavors in seconds. One bottle, endless moods.' },
]

export default function HowItWorks() {
  return (
    <section id="how" className="section">
      <div className="wrap">
        <div className="section-head">
          <div className="eyebrow">Super Simple</div>
          <h2>How Boobly works ⚡</h2>
          <p>Four steps to the most fun water you'll ever drink.</p>
        </div>
        <div className="steps">
          {STEPS.map((s, i) => (
            <motion.div
              key={s.n}
              className="step"
              initial={{ opacity: 0, scale: 0.85 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
            >
              <div className="step-num">{s.n}</div>
              <div style={{ fontSize: 40, marginBottom: 8 }}>{s.e}</div>
              <h4>{s.t}</h4>
              <p>{s.d}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
