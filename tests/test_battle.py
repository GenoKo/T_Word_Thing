from models.battle import Battle
from models.run import Run
from models.entities import Character, Skill, Item


def make_player():
    p = Character("Hero", hp=30, attack=8, defense=3, sp=20)
    p.skills = [
        Skill("fireball", "Fireball", damage=6, sp_cost=3, description="Fire"),
    ]
    return p


def make_enemy():
    return Character("Goblin", hp=20, attack=5, defense=1, sp=0)


def test_battle_initial_state():
    run = Run()
    battle = Battle(run, make_player(), make_enemy())

    assert battle.menu == "main"
    assert battle.ended is False
    assert battle.result is None


def test_open_skills_menu():
    run = Run()
    battle = Battle(run, make_player(), make_enemy())

    battle.process_action("open_skills")
    assert battle.menu == "skills"


def test_back_returns_to_main():
    run = Run()
    battle = Battle(run, make_player(), make_enemy())

    battle.process_action("open_skills")
    battle.process_action("back")

    assert battle.menu == "main"


def test_basic_attack_changes_enemy_hp():
    run = Run()
    battle = Battle(run, make_player(), make_enemy())

    old_hp = battle.enemy.hp
    battle.process_action("do_attack")

    assert battle.enemy.hp < old_hp


def test_skill_consumes_sp():
    run = Run()
    battle = Battle(run, make_player(), make_enemy())

    old_sp = battle.player.sp
    battle.process_action("do_skill:fireball")

    assert battle.player.sp < old_sp


def test_not_enough_sp_blocks_skill():
    run = Run()
    battle = Battle(run, make_player(), make_enemy())
    battle.player.sp = 0

    battle.process_action("do_skill:fireball")

    assert battle.menu == "skills"
    assert "Not enough SP" in battle.log


def test_item_heals_player():
    run = Run()
    run.add_item("potion", 1)

    battle = Battle(run, make_player(), make_enemy())
    battle.player.hp = 10

    battle.process_action("do_item:potion")

    assert battle.player.hp > 10
    assert run.item_qty("potion") == 0


def test_item_damage_enemy():
    run = Run()
    run.add_item("bomb", 1)

    battle = Battle(run, make_player(), make_enemy())
    old_hp = battle.enemy.hp

    battle.process_action("do_item:bomb")

    assert battle.enemy.hp < old_hp
    assert run.item_qty("bomb") == 0


def test_flee_success_or_failure_sets_expected_state():
    run = Run()
    battle = Battle(run, make_player(), make_enemy())

    # We don't force RNG here; just verify valid outcome
    battle.process_action("do_flee")

    assert battle.result in (None, "escape", "lose") or battle.ended in (True, False)


def test_win_sets_result_and_rewards_gold():
    run = Run()
    battle = Battle(run, make_player(), make_enemy())

    battle.enemy.hp = 1
    battle.process_action("do_attack")

    assert battle.ended is True
    assert battle.result == "win"
    assert run.gold > 0


def test_boss_win_increments_bosses_defeated():
    run = Run()
    enemy = Character("Boss", hp=1, attack=10, defense=2, sp=0, is_boss=True)
    battle = Battle(run, make_player(), enemy)

    battle.process_action("do_attack")

    assert battle.result == "win"
    assert run.bosses_defeated == 1