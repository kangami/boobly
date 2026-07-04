// Stable, playful social-proof numbers so every product card feels loved.
// (No real review system yet — derived from the id so it's consistent, not random.)
export function hype(id = '') {
  let h = 0
  for (let i = 0; i < id.length; i++) h = (h * 31 + id.charCodeAt(i)) >>> 0
  const rating = (4.6 + (h % 4) * 0.1).toFixed(1) // 4.6–4.9
  const count = 80 + (h % 520) // 80–599
  return { rating, count }
}
