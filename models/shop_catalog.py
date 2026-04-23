SHOP_STOCK = {
    "potion":   {"price": 15},
    "hiPotion": {"price": 30},
    "bomb":     {"price": 25},
    "secretElixir": {"price": 1},
    "ragePotion": {"price": 20},
}

def get_price(key: str) -> int | None:
    data = SHOP_STOCK.get(key)
    return data["price"] if data else None