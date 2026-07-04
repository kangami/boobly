import { createContext, useContext, useEffect, useMemo, useReducer, useState } from 'react'

const CartContext = createContext(null)

function reducer(state, action) {
  switch (action.type) {
    case 'ADD': {
      const found = state.find((i) => i.key === action.item.key)
      if (found) {
        return state.map((i) =>
          i.key === action.item.key ? { ...i, qty: i.qty + (action.item.qty || 1) } : i,
        )
      }
      return [...state, { ...action.item, qty: action.item.qty || 1 }]
    }
    case 'INC':
      return state.map((i) => (i.key === action.key ? { ...i, qty: i.qty + 1 } : i))
    case 'DEC':
      return state
        .map((i) => (i.key === action.key ? { ...i, qty: i.qty - 1 } : i))
        .filter((i) => i.qty > 0)
    case 'REMOVE':
      return state.filter((i) => i.key !== action.key)
    case 'CLEAR':
      return []
    case 'INIT':
      return action.items
    default:
      return state
  }
}

const STORAGE_KEY = 'boobly-cart-v1'

export function CartProvider({ children }) {
  const [items, dispatch] = useReducer(reducer, [])
  const [open, setOpen] = useState(false)

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (raw) dispatch({ type: 'INIT', items: JSON.parse(raw) })
    } catch {}
  }, [])

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
    } catch {}
  }, [items])

  const count = useMemo(() => items.reduce((n, i) => n + i.qty, 0), [items])
  const total = useMemo(() => items.reduce((n, i) => n + i.qty * i.price, 0), [items])

  const value = {
    items,
    open,
    setOpen,
    count,
    total,
    add: (item) => {
      dispatch({ type: 'ADD', item })
    },
    inc: (key) => dispatch({ type: 'INC', key }),
    dec: (key) => dispatch({ type: 'DEC', key }),
    remove: (key) => dispatch({ type: 'REMOVE', key }),
    clear: () => dispatch({ type: 'CLEAR' }),
  }

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>
}

export function useCart() {
  const ctx = useContext(CartContext)
  if (!ctx) throw new Error('useCart must be used within CartProvider')
  return ctx
}
