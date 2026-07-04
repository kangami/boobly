// Frontend fallback catalog — mirrors backend/products.py.
// The app fetches /api/catalog first and falls back to this if offline.

export const BOTTLES = [
  { id: 'bottle-sunset', name: 'Boobly Sunset', tagline: 'Pink-to-orange like a beach sundown', color: '#FF5E8A', gradient: ['#FF5E8A', '#FF9F45'], price: 19.9, capacity_ml: 750, emoji: '🌅' },
  { id: 'bottle-lime', name: 'Boobly Citrus', tagline: 'Zesty green-gold energy', color: '#9BE15D', gradient: ['#9BE15D', '#FFD93D'], price: 19.9, capacity_ml: 750, emoji: '🍋' },
  { id: 'bottle-ocean', name: 'Boobly Ocean', tagline: 'Blue-to-purple galaxy vibes', color: '#5C7CFA', gradient: ['#5C7CFA', '#A05CFA'], price: 19.9, capacity_ml: 750, emoji: '🌊' },
]

export const FLAVORS = [
  { id: 'cherry-orange-apple', name: 'Cherry · Orange · Apple', emoji: '🍒', notes: 'Juicy orchard mix with a cherry kick', color: '#FF7A33', gradient: ['#8FD14F', '#FF7A33'], family: 'Fruit', caffeine: false, vitamins: false },
  { id: 'strawberry-blueberry', name: 'Strawberry · Blueberry', emoji: '🍓', notes: 'Berry besties, sweet and tangy', color: '#E63950', gradient: ['#E63950', '#4361EE'], family: 'Fruit', caffeine: false, vitamins: false },
  { id: 'strawberry-kiwi', name: 'Strawberry · Kiwi', emoji: '🥝', notes: 'Tropical tang meets sweet berry', color: '#E63950', gradient: ['#E63950', '#7CB518'], family: 'Fruit', caffeine: false, vitamins: false },
  { id: 'blueberries', name: 'Blueberries', emoji: '🫐', notes: 'Big bold blueberry burst', color: '#4361EE', gradient: ['#4361EE', '#3A0CA3'], family: 'Fruit', caffeine: false, vitamins: false },
  { id: 'passion-fruit', name: 'Passion Fruit', emoji: '🌺', notes: 'Exotic, sunny and a little wild', color: '#F72585', gradient: ['#F72585', '#FFB703'], family: 'Fruit', caffeine: false, vitamins: false },
  { id: 'lemon', name: 'Lemon', emoji: '🍋', notes: 'Crisp, zingy, super refreshing', color: '#FFC300', gradient: ['#FFD60A', '#FAA307'], family: 'Fruit', caffeine: false, vitamins: false },
  { id: 'strawberry', name: 'Strawberry', emoji: '🍓', notes: 'Classic candy-sweet strawberry', color: '#FF4D6D', gradient: ['#FF4D6D', '#C9184A'], family: 'Fruit', caffeine: false, vitamins: false },
  { id: 'cola', name: 'Cola', emoji: '🥤', notes: 'Fizzy-feel cola, zero sugar', color: '#6F4E37', gradient: ['#6F4E37', '#241109'], family: 'Classic', caffeine: false, vitamins: false },
  { id: 'blueberry-tea', name: 'Blueberry Tea', emoji: '🧋', notes: 'Smooth iced tea with a berry twist + B vitamins', color: '#48CAE4', gradient: ['#48CAE4', '#0077B6'], family: 'Tea', caffeine: false, vitamins: true },
  { id: 'honey-tea', name: 'Honey Tea', emoji: '🍯', notes: 'Golden honey tea, cozy and smooth + B vitamins', color: '#F4A261', gradient: ['#FFD60A', '#F4A261'], family: 'Tea', caffeine: false, vitamins: true },
  { id: 'blackberry', name: 'Blackberry', emoji: '🫐', notes: 'Deep dark berry, lightly caffeinated + B vitamins', color: '#9D4EDD', gradient: ['#9D4EDD', '#3C096C'], family: 'Tea', caffeine: true, vitamins: true },
  { id: 'mango-tea', name: 'Mango Tea', emoji: '🥭', notes: 'Sunny mango tropical tea + B vitamins', color: '#FB8500', gradient: ['#FB8500', '#FFB703'], family: 'Tea', caffeine: false, vitamins: true },
]

export const BUNDLES = [
  { id: 'starter-kit', name: 'Starter Splash Kit', emoji: '✨', desc: '1 bottle + pick any 3 flavor packs', bottle_count: 1, pod_packs: 3, price: 36.9, compare_at: 43.6, badge: 'MOST POPULAR' },
  { id: 'squad-pack', name: 'Squad Pack', emoji: '🎉', desc: '3 bottles + pick any 6 flavor packs', bottle_count: 3, pod_packs: 6, price: 89.9, compare_at: 107.1, badge: 'BEST VALUE' },
  { id: 'flavor-vault', name: 'Flavor Vault', emoji: '🗝️', desc: '1 bottle + all 12 flavors, the full collection', bottle_count: 1, pod_packs: 12, price: 99.9, compare_at: 114.7, badge: 'COLLECTOR' },
]

export const POD_PACK_PRICE = 7.9
export const POD_PACK_SIZE = 5

export const FALLBACK_CATALOG = {
  bottles: BOTTLES,
  flavors: FLAVORS,
  bundles: BUNDLES,
  pod_pack_price: POD_PACK_PRICE,
  pod_pack_size: POD_PACK_SIZE,
}
