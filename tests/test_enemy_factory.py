from models.enemy_factory import make_enemy


def test_make_normal_enemy():
    enemy = make_enemy(difficulty="normal", is_boss=False, bosses_defeated=0)

    assert enemy.is_boss is False
    assert enemy.hp > 0
    assert enemy.attack >= 0
    assert enemy.defense >= 0


def test_make_boss_enemy():
    enemy = make_enemy(difficulty="easy", is_boss=True, bosses_defeated=0)

    assert enemy.is_boss is True
    assert enemy.hp > 0
    assert enemy.attack > 0


def test_boss_ignores_difficulty_but_scales_with_progression():
    boss1 = make_enemy(difficulty="easy", is_boss=True, bosses_defeated=0)
    boss2 = make_enemy(difficulty="hard", is_boss=True, bosses_defeated=3)

    assert boss2.max_hp >= boss1.max_hp
    assert boss2.base_attack >= boss1.base_attack
    assert boss2.base_defense >= boss1.base_defense


def test_normal_enemy_scales_with_bosses_defeated():
    e1 = make_enemy(difficulty="normal", is_boss=False, bosses_defeated=0)
    e2 = make_enemy(difficulty="normal", is_boss=False, bosses_defeated=3)

    assert e2.max_hp >= e1.max_hp
    assert e2.base_attack >= e1.base_attack
    assert e2.base_defense >= e1.base_defense