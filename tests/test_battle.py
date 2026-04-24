from models.battle import Battle
from models.run import Run
from models.entities import Character, Skill


def make_player():
    p = Character("Hero", hp=100, attack=8, defense=3, sp=30)
    p.skills = [
        Skill("fireball", "Fireball", damage=10, sp_cost=3, description="Fire spell"),
    ]
    return p


def make_enemy():
    return Character(
        "Goblin",
        hp=20,
        attack=5,
        defense=1,
        sp=0,
        ai_type="basic",
        personality_name="Curious",
        personality_traits=["curious"],
        personality_description="Interested in conversation.",
    )


def test_battle_initial_state():
    battle = Battle(Run(), make_player(), make_enemy())

    assert battle.menu == "main"
    assert battle.ended is False
    assert battle.result is None
    assert battle.enemy_will_to_fight == 100


def test_open_talk_menu():
    battle = Battle(Run(), make_player(), make_enemy())

    battle.process_action("open_talk")

    assert battle.menu == "talk"


def test_attack_changes_enemy_hp():
    battle = Battle(Run(), make_player(), make_enemy())

    old_hp = battle.enemy.hp
    battle.process_action("do_attack")

    assert battle.enemy.hp < old_hp
    assert "attack" in battle.player_actions_history


def test_skill_consumes_sp_and_damages_enemy():
    battle = Battle(Run(), make_player(), make_enemy())

    old_sp = battle.player.sp
    old_hp = battle.enemy.hp

    battle.process_action("do_skill:fireball")

    assert battle.player.sp < old_sp
    assert battle.enemy.hp < old_hp


def test_item_heals_player():
    run = Run()
    run.add_item("potion", 1)

    battle = Battle(run, make_player(), make_enemy())
    battle.player.hp = 50

    battle.process_action("do_item:potion")

    assert battle.player.hp > 50
    assert run.item_qty("potion") == 0


def test_item_damages_enemy():
    run = Run()
    run.add_item("bomb", 1)

    battle = Battle(run, make_player(), make_enemy())
    old_hp = battle.enemy.hp

    battle.process_action("do_item:bomb")

    assert battle.enemy.hp < old_hp
    assert run.item_qty("bomb") == 0


def test_react_to_talk_can_continue_conversation():
    battle = Battle(Run(), make_player(), make_enemy())

    result = {
        "reply": "Interesting. Continue.",
        "emotion": "curiosity",
        "interest_delta": 1,
        "enemy_action": "talk",
    }

    battle.react_to_talk("Can we stop fighting?", result)

    assert battle.menu == "talk"
    assert battle.in_conversation is True
    assert "Can we stop fighting?" in battle.log
    assert battle.enemy_conversation_interest >= 1


def test_react_to_talk_attack_response():
    battle = Battle(Run(), make_player(), make_enemy())

    result = {
        "reply": "Enough words!",
        "emotion": "anger",
        "interest_delta": -2,
        "enemy_action": "attack",
    }

    old_player_hp = battle.player.hp
    battle.react_to_talk("Please stop.", result)

    assert battle.menu == "main"
    assert battle.in_conversation is False
    assert battle.player.hp < old_player_hp


def test_react_to_talk_hesitate_response_increases_escape_bonus():
    battle = Battle(Run(), make_player(), make_enemy())

    result = {
        "reply": "I... do not know.",
        "emotion": "fear",
        "interest_delta": 1,
        "enemy_action": "hesitate",
    }

    battle.react_to_talk("You don't have to fight.", result)

    assert battle.menu == "main"
    assert battle.escape_bonus > 0


def test_enemy_surrender_peace_result():
    battle = Battle(Run(), make_player(), make_enemy())

    battle.enemy_will_to_fight = 5

    result = {
        "reply": "Fine. I yield.",
        "emotion": "respect",
        "interest_delta": 1,
        "enemy_action": "hesitate",
    }

    battle.react_to_talk("This fight is pointless.", result)

    assert battle.ended is True
    assert battle.result == "peace"