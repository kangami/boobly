import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'

const EMOJIS = ['🌈', '✨', '💧', '🍓', '🥝', '🍋', '🫐', '🎉', '⭐', '🥭']

let idSeed = 0

// Imperative confetti: call window.boobBurst(x, y)
export default function Confetti() {
  const [bursts, setBursts] = useState([])

  useEffect(() => {
    window.boobBurst = (x, y) => {
      const id = ++idSeed
      const pieces = Array.from({ length: 14 }, (_, i) => ({
        i,
        emoji: EMOJIS[Math.floor(Math.random() * EMOJIS.length)],
        dx: (Math.random() - 0.5) * 260,
        dy: -(Math.random() * 220 + 80),
        rot: (Math.random() - 0.5) * 540,
      }))
      setBursts((b) => [...b, { id, x, y, pieces }])
      setTimeout(() => setBursts((b) => b.filter((bb) => bb.id !== id)), 1100)
    }
    return () => { delete window.boobBurst }
  }, [])

  return (
    <AnimatePresence>
      {bursts.map((burst) =>
        burst.pieces.map((p) => (
          <motion.div
            key={`${burst.id}-${p.i}`}
            className="confetti-pop"
            initial={{ x: burst.x, y: burst.y, opacity: 1, scale: 1 }}
            animate={{
              x: burst.x + p.dx,
              y: burst.y + p.dy,
              opacity: 0,
              scale: 1.4,
              rotate: p.rot,
            }}
            transition={{ duration: 1, ease: 'easeOut' }}
          >
            {p.emoji}
          </motion.div>
        )),
      )}
    </AnimatePresence>
  )
}

export function burstFrom(e) {
  const x = e?.clientX ?? window.innerWidth / 2
  const y = e?.clientY ?? window.innerHeight / 2
  window.boobBurst?.(x, y)
}
