const ITEMS = [
  '💧 ZERO SUGAR', '🌈 12 FLAVORS', '♻️ REFILL FOREVER', '✨ ZERO CALORIES',
  '🧊 STAY HYDRATED', '🎉 SWITCH ANYTIME', '🌟 NATURAL FLAVORS',
]

export default function Marquee() {
  const loop = [...ITEMS, ...ITEMS]
  return (
    <div className="marquee">
      <div className="marquee-track">
        {loop.map((t, i) => (
          <span key={i}>{t} <span aria-hidden>·</span></span>
        ))}
      </div>
    </div>
  )
}
