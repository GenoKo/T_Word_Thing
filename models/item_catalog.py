from models.entities import Item

ITEMS = {
    "potion": {
        "name": "❤️ Potion",
        "heal": 30,
        "damage": 0,
        "description": "Restores 30 HP",
    },
    "hiPotion": {
        "name": "💖 Hi-Potion",
        "heal": 50,
        "damage": 0,
        "description": "Restores 50 HP",
    },
    "bomb": {
        "name": "💣 Bomb",
        "heal": 0,
        "damage": 15,
        "description": "Explodes and deals 15 damage to the enemy",
    },
    #For testing purposes only
    # "secretElixir": {
    #     "name": "💗 Secret-Elixir",
    #     "heal": 100,
    #     "damage": 0,
    #     "description": "Restores a whopping 50 HP! Keep this a secret between us ;)",
    # },
    "ragePotion": {
    "name": "⚔️ Strength Potion",
    "effect_stat": "attack",
    "effect_amount": 5,
    "effect_turns": 3,
    "target": "self",
    "description": "Slightly increases the player's attack for 3 turns",
    },
    "armorBreaker": {
        "name": "⛏ Armor breaker",
        "effect_stat": "defense",
        "effect_amount": -5,
        "effect_turns": 3,
        "target": "enemy",
        "description": "Slightly decreases the enemy's defense for 3 turns",
    },
}

def get_item(key: str) -> Item | None:
    data = ITEMS.get(key)
    if not data:
        return None

    return Item(
        key=key,
        name=data["name"],
        heal=data.get("heal", 0),
        damage=data.get("damage", 0),
        effect_stat=data.get("effect_stat"),
        effect_amount=data.get("effect_amount", 0),
        effect_turns=data.get("effect_turns", 0),
        target=data.get("target", "self"),
        description=data.get("description", "")
    )
