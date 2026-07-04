"""Boobly catalog — the single source of truth for bottles & flavor pods.

Each flavor maps to one cartridge on the real product sheet (booblyPerfume.jpg).
Colors drive the gradient cards on the storefront, so keep them juicy.
"""

# The three signature bottles from the hero shot (getBooblyMain.png)
BOTTLES = [
    {
        "id": "bottle-sunset",
        "name": "Boobly Sunset",
        "tagline": "Pink-to-orange like a beach sundown",
        "color": "#FF5E8A",
        "gradient": ["#FF5E8A", "#FF9F45"],
        "price": 19.90,
        "capacity_ml": 750,
        "emoji": "🌅",
    },
    {
        "id": "bottle-lime",
        "name": "Boobly Citrus",
        "tagline": "Zesty green-gold energy",
        "color": "#9BE15D",
        "gradient": ["#9BE15D", "#FFD93D"],
        "price": 19.90,
        "capacity_ml": 750,
        "emoji": "🍋",
    },
    {
        "id": "bottle-ocean",
        "name": "Boobly Ocean",
        "tagline": "Blue-to-purple galaxy vibes",
        "color": "#5C7CFA",
        "gradient": ["#5C7CFA", "#A05CFA"],
        "price": 19.90,
        "capacity_ml": 750,
        "emoji": "🌊",
    },
]

# The 12 flavor pods from booblyPerfume.jpg
FLAVORS = [
    {
        "id": "cherry-orange-apple",
        "name": "Cherry · Orange · Apple",
        "emoji": "🍒",
        "notes": "Juicy orchard mix with a cherry kick",
        "color": "#FF7A33",
        "gradient": ["#8FD14F", "#FF7A33"],
        "family": "Fruit",
        "caffeine": False,
        "vitamins": False,
    },
    {
        "id": "strawberry-blueberry",
        "name": "Strawberry · Blueberry",
        "emoji": "🍓",
        "notes": "Berry besties, sweet and tangy",
        "color": "#E63950",
        "gradient": ["#E63950", "#4361EE"],
        "family": "Fruit",
        "caffeine": False,
        "vitamins": False,
    },
    {
        "id": "strawberry-kiwi",
        "name": "Strawberry · Kiwi",
        "emoji": "🥝",
        "notes": "Tropical tang meets sweet berry",
        "color": "#E63950",
        "gradient": ["#E63950", "#7CB518"],
        "family": "Fruit",
        "caffeine": False,
        "vitamins": False,
    },
    {
        "id": "blueberries",
        "name": "Blueberries",
        "emoji": "🫐",
        "notes": "Big bold blueberry burst",
        "color": "#4361EE",
        "gradient": ["#4361EE", "#3A0CA3"],
        "family": "Fruit",
        "caffeine": False,
        "vitamins": False,
    },
    {
        "id": "passion-fruit",
        "name": "Passion Fruit",
        "emoji": "🌺",
        "notes": "Exotic, sunny and a little wild",
        "color": "#F72585",
        "gradient": ["#F72585", "#FFB703"],
        "family": "Fruit",
        "caffeine": False,
        "vitamins": False,
    },
    {
        "id": "lemon",
        "name": "Lemon",
        "emoji": "🍋",
        "notes": "Crisp, zingy, super refreshing",
        "color": "#FFC300",
        "gradient": ["#FFD60A", "#FAA307"],
        "family": "Fruit",
        "caffeine": False,
        "vitamins": False,
    },
    {
        "id": "strawberry",
        "name": "Strawberry",
        "emoji": "🍓",
        "notes": "Classic candy-sweet strawberry",
        "color": "#FF4D6D",
        "gradient": ["#FF4D6D", "#C9184A"],
        "family": "Fruit",
        "caffeine": False,
        "vitamins": False,
    },
    {
        "id": "cola",
        "name": "Cola",
        "emoji": "🥤",
        "notes": "Fizzy-feel cola, zero sugar",
        "color": "#6F4E37",
        "gradient": ["#6F4E37", "#241109"],
        "family": "Classic",
        "caffeine": False,
        "vitamins": False,
    },
    {
        "id": "blueberry-tea",
        "name": "Blueberry Tea",
        "emoji": "🧋",
        "notes": "Smooth iced tea with a berry twist + B vitamins",
        "color": "#48CAE4",
        "gradient": ["#48CAE4", "#0077B6"],
        "family": "Tea",
        "caffeine": False,
        "vitamins": True,
    },
    {
        "id": "honey-tea",
        "name": "Honey Tea",
        "emoji": "🍯",
        "notes": "Golden honey tea, cozy and smooth + B vitamins",
        "color": "#F4A261",
        "gradient": ["#FFD60A", "#F4A261"],
        "family": "Tea",
        "caffeine": False,
        "vitamins": True,
    },
    {
        "id": "blackberry",
        "name": "Blackberry",
        "emoji": "🫐",
        "notes": "Deep dark berry, lightly caffeinated + B vitamins",
        "color": "#9D4EDD",
        "gradient": ["#9D4EDD", "#3C096C"],
        "family": "Tea",
        "caffeine": True,
        "vitamins": True,
    },
    {
        "id": "mango-tea",
        "name": "Mango Tea",
        "emoji": "🥭",
        "notes": "Sunny mango tropical tea + B vitamins",
        "color": "#FB8500",
        "gradient": ["#FB8500", "#FFB703"],
        "family": "Tea",
        "caffeine": False,
        "vitamins": True,
    },
]

# Pricing for pods (per pack)
POD_PACK_PRICE = 7.90  # pack of 5 cartridges
POD_PACK_SIZE = 5

BUNDLES = [
    {
        "id": "starter-kit",
        "name": "Starter Splash Kit",
        "emoji": "✨",
        "desc": "1 bottle + pick any 3 flavor packs",
        "bottle_count": 1,
        "pod_packs": 3,
        "price": 36.90,
        "compare_at": 43.60,
        "badge": "MOST POPULAR",
    },
    {
        "id": "squad-pack",
        "name": "Squad Pack",
        "emoji": "🎉",
        "desc": "3 bottles + pick any 6 flavor packs",
        "bottle_count": 3,
        "pod_packs": 6,
        "price": 89.90,
        "compare_at": 107.10,
        "badge": "BEST VALUE",
    },
    {
        "id": "flavor-vault",
        "name": "Flavor Vault",
        "emoji": "🗝️",
        "desc": "1 bottle + all 12 flavors, the full collection",
        "bottle_count": 1,
        "pod_packs": 12,
        "price": 99.90,
        "compare_at": 114.70,
        "badge": "COLLECTOR",
    },
]


def catalog():
    return {
        "bottles": BOTTLES,
        "flavors": FLAVORS,
        "bundles": BUNDLES,
        "pod_pack_price": POD_PACK_PRICE,
        "pod_pack_size": POD_PACK_SIZE,
    }


# --- Server-side price authority -------------------------------------------
# Cart items arrive from the browser with a `price`, but that value must NEVER
# be trusted (a user could edit it to $0.01). These lookups are the single
# source of truth for what each catalog item actually costs.
_BOTTLES_BY_ID = {b["id"]: b for b in BOTTLES}
_BUNDLES_BY_ID = {b["id"]: b for b in BUNDLES}
_FLAVORS_BY_ID = {f["id"]: f for f in FLAVORS}


def lookup_item(item_type, item_id):
    """Resolve a cart line to its authoritative {name, price}, or None if unknown.

    `item_type` is one of 'bottle' | 'bundle' | 'pod' (see the frontend cart
    payloads). Pods are all sold at the flat POD_PACK_PRICE regardless of flavor.
    """
    if item_type == "bottle":
        b = _BOTTLES_BY_ID.get(item_id)
        if b:
            return {"name": b["name"], "price": b["price"]}
    elif item_type == "bundle":
        b = _BUNDLES_BY_ID.get(item_id)
        if b:
            return {"name": b["name"], "price": b["price"]}
    elif item_type == "pod":
        f = _FLAVORS_BY_ID.get(item_id)
        if f:
            return {"name": f"{f['name']} — pod pack", "price": POD_PACK_PRICE}
    return None
