from controllers import battle_controller


def test_menu_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Start Run" in response.data or b"Main Menu" in response.data


def test_start_run_button(client):
    response = client.post("/", data={"action": "start_run"}, follow_redirects=True)

    assert response.status_code == 200
    assert battle_controller.run.state == "battle"
    assert b"World Level" in response.data or b"HP" in response.data


def test_open_skills_button(client):
    client.post("/", data={"action": "start_run"}, follow_redirects=True)
    response = client.post("/", data={"action": "open_skills"}, follow_redirects=True)

    assert response.status_code == 200
    assert b"Fireball" in response.data or battle_controller.battle.menu == "skills"


def test_open_items_button(client):
    client.post("/", data={"action": "start_run"}, follow_redirects=True)
    response = client.post("/", data={"action": "open_items"}, follow_redirects=True)

    assert response.status_code == 200
    assert b"Potion" in response.data or battle_controller.battle.menu == "items"


def test_attack_button(client):
    client.post("/", data={"action": "start_run"}, follow_redirects=True)
    old_hp = battle_controller.battle.enemy.hp

    response = client.post("/", data={"action": "do_attack"}, follow_redirects=True)

    assert response.status_code == 200
    assert battle_controller.battle.enemy.hp < old_hp


def test_shop_button_after_encounter_end(client):
    client.post("/", data={"action": "start_run"}, follow_redirects=True)

    battle_controller.battle.ended = True
    battle_controller.battle.result = "win"

    response = client.post("/", data={"action": "open_shop"}, follow_redirects=True)

    assert response.status_code == 200
    assert battle_controller.run.state == "shop"
    assert b"Shop" in response.data


def test_leave_shop_button(client):
    client.post("/", data={"action": "start_run"}, follow_redirects=True)
    battle_controller.run.state = "shop"

    response = client.post("/", data={"action": "leave_shop"}, follow_redirects=True)

    assert response.status_code == 200
    assert battle_controller.run.state == "battle"


def test_new_run_button(client):
    client.post("/", data={"action": "start_run"}, follow_redirects=True)

    battle_controller.run.gold = 999
    battle_controller.run.add_item("bomb", 5)

    response = client.post("/", data={"action": "new_run"}, follow_redirects=True)

    assert response.status_code == 200
    assert battle_controller.run.gold == 0
    assert battle_controller.run.encounter_number == 1


def test_next_encounter_button(client):
    client.post("/", data={"action": "start_run"}, follow_redirects=True)

    battle_controller.battle.ended = True
    battle_controller.battle.result = "win"
    current_encounter = battle_controller.run.encounter_number

    response = client.post("/", data={"action": "next_encounter"}, follow_redirects=True)

    assert response.status_code == 200
    assert battle_controller.run.encounter_number == current_encounter + 1


def test_back_to_menu_button(client):
    client.post("/", data={"action": "start_run"}, follow_redirects=True)

    response = client.post("/", data={"action": "back_to_menu"}, follow_redirects=True)

    assert response.status_code == 200
    assert battle_controller.run.state == "menu"


#===

def test_open_talk_button(client):
    client.post("/", data={"action": "start_run"}, follow_redirects=True)

    response = client.post("/", data={"action": "open_talk"}, follow_redirects=True)

    assert response.status_code == 200
    assert battle_controller.battle.menu in ("main", "talk")
    assert b"What do you say?" in response.data


def test_submit_talk_empty_input(client):
    client.post("/", data={"action": "start_run"}, follow_redirects=True)
    client.post("/", data={"action": "open_talk"}, follow_redirects=True)

    response = client.post("/", data={
        "action": "submit_talk",
        "talk_input": ""
    }, follow_redirects=True)

    assert response.status_code == 200
    assert battle_controller.battle.menu in ("main", "talk")
    assert "Say something first." in battle_controller.battle.log


def test_submit_talk_with_input(client):
    client.post("/", data={"action": "start_run"}, follow_redirects=True)
    client.post("/", data={"action": "open_talk"}, follow_redirects=True)

    response = client.post("/", data={
        "action": "submit_talk",
        "talk_input": "Please don't attack me"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert battle_controller.battle.menu in ("main", "talk")
    assert 'You say: "Please don\'t attack me"' in battle_controller.battle.log
    assert battle_controller.battle.enemy.name in battle_controller.battle.log