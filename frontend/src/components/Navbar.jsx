import { useCart } from '../context/CartContext.jsx'

export default function Navbar() {
  const { count, setOpen } = useCart()
  return (
    <nav className="nav">
      <div className="wrap nav-inner">
        <a href="#top" className="logo">boobly</a>
        <div className="nav-links">
          <a href="#flavors">Flavors</a>
          <a href="#bottles">Bottles</a>
          <a href="#bundles">Bundles</a>
          <a href="#how">How it works</a>
          <button className="cart-btn" onClick={() => setOpen(true)}>
            🛒 Cart
            {count > 0 && <span className="cart-bubble">{count}</span>}
          </button>
        </div>
      </div>
    </nav>
  )
}
