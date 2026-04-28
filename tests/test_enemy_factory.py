from unittest.mock import patch
from models.enemy_factory import make_enemy, ENEMIES_BY_DIFFICULTY, BOSS_ENEMIES


def test_make_normal_enemy():
    enemy = make_enemy(difficulty="normal", is_boss=False, bosses_defeated=0)

    assert enemy.is_boss is False
    assert enemy.hp > 0
    assert enemy.attack > 0
    assert enemy.defense >= 0
    assert enemy.personality_name != ""


def test_make_boss_enemy():
    enemy = make_enemy(difficulty="easy", is_boss=True, bosses_defeated=0)

    assert enemy.is_boss is True
    assert enemy.hp > 0
    assert enemy.ai_type == "boss"


def test_normal_enemy_scales_with_bosses_defeated():
    fixed_enemy = ENEMIES_BY_DIFFICULTY["normal"][0]

    with patch("models.enemy_factory.ENEMIES_BY_DIFFICULTY", {
        "normal": [fixed_enemy]
    }):
        e1 = make_enemy(difficulty="normal", is_boss=False, bosses_defeated=0)
        e2 = make_enemy(difficulty="normal", is_boss=False, bosses_defeated=3)

    assert e2.max_hp >= e1.max_hp
    assert e2.base_attack >= e1.base_attack
    assert e2.base_defense >= e1.base_defense


def test_boss_scales_with_bosses_defeated():
    fixed_boss = BOSS_ENEMIES[0]

    with patch("models.enemy_factory.BOSS_ENEMIES", [fixed_boss]):
        b1 = make_enemy(difficulty="easy", is_boss=True, bosses_defeated=0)
        b2 = make_enemy(difficulty="hard", is_boss=True, bosses_defeated=3)

    assert b2.max_hp >= b1.max_hp
    assert b2.base_attack >= b1.base_attack
    assert b2.base_defense >= b1.base_defense