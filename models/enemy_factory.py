import random
from models.entities import Character
from models.personality_factory import random_personality

ENEMIES_BY_DIFFICULTY = {
    "easy": [
        {"name": "Slime", "hp": 14, "attack": 4, "defense": 1, "ai": "basic"},
        {"name": "Bat", "hp": 16, "attack": 5, "defense": 1, "ai": "wild"},
    ],
    "normal": [
        {"name": "Goblin", "hp": 22, "attack": 6, "defense": 2, "ai": "aggressive"},
        {"name": "Wolf", "hp": 24, "attack": 7, "defense": 2, "ai": "wild"},
    ],
    "hard": [
        {"name": "Orc", "hp": 32, "attack": 9, "defense": 4, "ai": "aggressive"},
        {"name": "Knight", "hp": 35, "attack": 10, "defense": 5, "ai": "defensive"},
    ],
}

BOSS_ENEMIES = [
    {"name": "Demon King", "hp": 60, "attack": 14, "defense": 6, "ai": "boss"},
    {"name": "Ancient Dragon", "hp": 75, "attack": 16, "defense": 8, "ai": "boss"},
]

DIFFICULTY_REWARD_MULTIPLIER = {
    "easy": 0.8,
    "normal": 1.0,
    "hard": 1.4,
    "boss": 2.0,
}

def make_enemy(
    difficulty: str = "normal",
    is_boss: bool = False,
    bosses_defeated: int = 0
) -> Character:
    # bosses_defeated is now the progression stage
    scale_stage = bosses_defeated
    personality = random_personality()

    if is_boss:
        template = random.choice(BOSS_ENEMIES)
        reward_multiplier = DIFFICULTY_REWARD_MULTIPLIER["boss"]

        # Bosses scale only with progression, not selected difficulty
        hp = template["hp"] + (scale_stage * 6)
        attack = template["attack"] + (scale_stage * 2)
        defense = template["defense"] + scale_stage

    else:
        difficulty = difficulty.lower().strip()
        if difficulty not in ENEMIES_BY_DIFFICULTY:
            difficulty = "normal"

        template = random.choice(ENEMIES_BY_DIFFICULTY[difficulty])
        reward_multiplier = DIFFICULTY_REWARD_MULTIPLIER[difficulty]

        # Normal enemies scale with progression only,
        # while difficulty controls the base template/reward
        hp = template["hp"] + (scale_stage * 4)
        attack = template["attack"] + scale_stage
        defense = template["defense"] + (scale_stage // 2)

    return Character(
        name=template["name"],
        hp=hp,
        attack=attack,
        defense=defense,
        sp=0,
        is_boss=is_boss,
        reward_multiplier=reward_multiplier,
        ai_type=template.get("ai", "basic"),
        personality_name=personality["name"],
        personality_traits=personality["traits"],
        personality_description=personality["description"],
    )