SHOP_STOCK = {
    "potion":   {"price": 10},
    "hiPotion": {"price": 20},
    "bomb":     {"price": 15},
    # For testing:
    #"secretElixir": {"price": 1}
    "ragePotion": {"price": 15},
    "armorBreaker":{"price": 20},
}

def get_price(key: str) -> int | None:
    data = SHOP_STOCK.get(key)
    return data["price"] if data else None