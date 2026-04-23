from models.entities import Character, Skill, Item


def test_character_damage_and_heal():
    c = Character("Hero", hp=30, attack=8, defense=3, sp=20)

    c.take_damage(10)
    assert c.hp == 20

    c.heal(5)
    assert c.hp == 25

    c.heal(999)
    assert c.hp == 30


def test_character_spend_sp():
    c = Character("Mage", hp=20, attack=5, defense=1, sp=10)

    assert c.spend_sp(3) is True
    assert c.sp == 7

    assert c.spend_sp(20) is False
    assert c.sp == 7


def test_character_effects_change_stats():
    c = Character("Hero", hp=30, attack=10, defense=5, sp=20)

    assert c.attack == 10
    assert c.defense == 5

    c.add_effect("attack", 3, 2)
    c.add_effect("defense", -2, 1)

    assert c.attack == 13
    assert c.defense == 3


def test_character_tick_effects():
    c = Character("Hero", hp=30, attack=10, defense=5, sp=20)
    c.add_effect("attack", 3, 1)

    assert c.attack == 13
    c.tick_effects()
    assert c.attack == 10


def test_skill_and_item_creation():
    s = Skill("fireball", "Fireball", damage=6, sp_cost=3, description="Fire damage")
    i = Item("bomb", "Bomb", damage=10, description="Deals damage")

    assert s.key == "fireball"
    assert s.description == "Fire damage"
    assert i.key == "bomb"
    assert i.damage == 10
    assert i.description == "Deals damage"