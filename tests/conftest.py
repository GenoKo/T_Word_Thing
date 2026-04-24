import pytest

from app import app
from controllers import battle_controller
from models.run import Run
from models.battle import Battle


@pytest.fixture
def client(monkeypatch):
    app.config["TESTING"] = True

    # Mock Gemini / LLM call so tests do not use real API
    def fake_talk_to_enemy(enemy, player_message, context=None):
        return {
            "reply": "Hm. Go on.",
            "emotion": "curiosity",
            "interest_delta": 1,
            "enemy_action": "talk",
        }

    monkeypatch.setattr(battle_controller, "talk_to_enemy", fake_talk_to_enemy)

    battle_controller.run = Run()
    battle_controller.battle = Battle(
        battle_controller.run,
        battle_controller.make_player(),
        battle_controller.make_enemy_for_run(battle_controller.run),
    )

    with app.test_client() as client:
        yield client