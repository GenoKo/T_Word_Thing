from models.run import Run


def test_run_initial_values():
    run = Run()

    assert run.encounter_number == 1
    assert run.state == "menu"
    assert run.next_difficulty == "normal"
    assert run.gold == 0
    assert run.inventory == {}
    assert run.bosses_defeated == 0


def test_run_reset():
    run = Run()
    run.encounter_number = 5
    run.next_difficulty = "hard"
    run.gold = 100
    run.inventory = {"potion": 2}
    run.bosses_defeated = 2

    run.reset()

    assert run.encounter_number == 1
    assert run.next_difficulty == "normal"
    assert run.gold == 0
    assert run.inventory == {}
    assert run.bosses_defeated == 0


def test_run_advance():
    run = Run()
    run.advance()
    assert run.encounter_number == 2


def test_boss_encounter_every_fifth():
    run = Run()

    run.encounter_number = 4
    assert run.is_boss_encounter() is False

    run.encounter_number = 5
    assert run.is_boss_encounter() is True


def test_gold_add_and_spend():
    run = Run()
    run.add_gold(50)

    assert run.spend_gold(20) is True
    assert run.gold == 30

    assert run.spend_gold(100) is False
    assert run.gold == 30


def test_inventory_add_remove():
    run = Run()

    run.add_item("potion", 2)
    assert run.item_qty("potion") == 2

    assert run.remove_item("potion", 1) is True
    assert run.item_qty("potion") == 1

    assert run.remove_item("potion", 1) is True
    assert run.item_qty("potion") == 0