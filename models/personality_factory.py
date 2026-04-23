import random

PERSONALITIES = [
    {
        "name": "Proud",
        "traits": ["arrogant", "honor-driven", "easily provoked"],
        "description": "Values pride and strength. Responds poorly to mockery but respects confidence."
    },
    {
        "name": "Cowardly",
        "traits": ["fearful", "self-preserving", "hesitant"],
        "description": "Avoids danger and may be easier to intimidate or scare."
    },
    {
        "name": "Hostile",
        "traits": ["aggressive", "short-tempered", "resentful"],
        "description": "Quick to anger and likely to react badly to insults or threats."
    },
    {
        "name": "Curious",
        "traits": ["inquisitive", "cautious", "thoughtful"],
        "description": "Interested in unusual speech and more willing to engage in conversation."
    },
    {
        "name": "Fanatical",
        "traits": ["unyielding", "zealous", "stubborn"],
        "description": "Deeply committed to its beliefs and difficult to persuade emotionally."
    },
]
def random_personality():
    return random.choice(PERSONALITIES)