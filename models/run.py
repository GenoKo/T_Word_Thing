class Run:
    def __init__(self):
        self.encounter_number = 1
        self.state = "menu"
        self.next_difficulty = "normal"
        self.gold = 0
        self.inventory: dict[str, int] = {}
        self.bosses_defeated = 0   # NEW

    def reset(self):
        self.encounter_number = 1
        self.next_difficulty = "normal"
        self.gold = 0
        self.inventory = {}
        self.bosses_defeated = 0

    def advance(self):
        self.encounter_number += 1

    def is_boss_encounter(self) -> bool:
        return self.encounter_number % 5 == 0

    def add_gold(self, amount: int):
        self.gold = max(0, self.gold + int(amount))

    def spend_gold(self, amount: int) -> bool:
        amount = int(amount)
        if amount <= self.gold:
            self.gold -= amount
            return True
        return False

    def item_qty(self, key: str) -> int:
        return int(self.inventory.get(key, 0))

    def add_item(self, key: str, qty: int = 1):
        qty = int(qty)
        if qty <= 0:
            return
        self.inventory[key] = self.item_qty(key) + qty

    def remove_item(self, key: str, qty: int = 1) -> bool:
        qty = int(qty)
        if qty <= 0:
            return True
        have = self.item_qty(key)
        if have < qty:
            return False
        new_qty = have - qty
        if new_qty <= 0:
            self.inventory.pop(key, None)
        else:
            self.inventory[key] = new_qty
        return True