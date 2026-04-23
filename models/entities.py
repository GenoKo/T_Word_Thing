class Skill:
    def __init__(
        self,
        key: str,
        name: str,
        damage: int,
        sp_cost: int,
        description: str = ""
    ):
        self.key = key
        self.name = name
        self.damage = damage
        self.sp_cost = sp_cost
        self.description = description


class Item:
    def __init__(
        self,
        key: str,
        name: str,
        heal: int = 0,
        damage: int = 0,
        effect_stat: str = None,
        effect_amount: int = 0,
        effect_turns: int = 0,
        target: str = "self",
        description: str = ""
    ):
        self.key = key
        self.name = name
        self.heal = heal
        self.damage = damage
        self.effect_stat = effect_stat
        self.effect_amount = effect_amount
        self.effect_turns = effect_turns
        self.target = target
        self.description = description

class Character:
    def __init__(
        self,
        name: str,
        hp: int,
        attack: int,
        defense: int = 0,
        sp: int = 20,
        is_boss: bool = False,
        reward_multiplier: float = 1.0,
        ai_type: str = "basic",
        personality_name: str = "",
        personality_traits: list[str] | None = None,
        personality_description: str = "",
    ):
        self.name = name
        self.max_hp = hp
        self.hp = hp

        self.base_attack = attack
        self.base_defense = defense
    
        self.max_sp = sp
        self.sp = sp

        self.is_boss = is_boss
        self.reward_multiplier = reward_multiplier

        self.skills = []
        self.active_effects = []

        self.ai_type = ai_type

        self.personality_name = personality_name
        self.personality_traits = personality_traits or []
        self.personality_description = personality_description

    @property
    def attack(self):
        bonus = sum(e["amount"] for e in self.active_effects if e["stat"] == "attack")
        return max(0, self.base_attack + bonus)

    @property
    def defense(self):
        bonus = sum(e["amount"] for e in self.active_effects if e["stat"] == "defense")
        return max(0, self.base_defense + bonus)

    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)

    def heal(self, amount: int) -> None:
        self.hp = min(self.max_hp, self.hp + amount)

    def spend_sp(self, amount: int) -> bool:
        if amount <= self.sp:
            self.sp -= amount
            return True
        return False
    
    def add_effect(self, stat: str, amount: int, turns: int):
        self.active_effects.append({
            "stat": stat,
            "amount": amount,
            "turns": turns
        })

    def tick_effects(self):
        for e in self.active_effects:
            e["turns"] -= 1

        self.active_effects = [e for e in self.active_effects if e["turns"] > 0]

    def get_effect_display(self):
        stat_names = {
            "attack": "ATK",
            "defense": "DEF",
        }

        effect_list = []

        for effect in self.active_effects:
            stat = stat_names.get(effect["stat"], effect["stat"].upper())
            amount = effect["amount"]
            turns = effect["turns"]

            sign = "+" if amount > 0 else ""

            effect_list.append({
                "text": f"{stat} {sign}{amount} ({turns}t)",
                "type": "buff" if amount > 0 else "debuff"
            })

        return effect_list