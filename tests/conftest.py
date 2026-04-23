import pytest

from app import app
from controllers import battle_controller
from models.run import Run
from models.battle import Battle


@pytest.fixture
def client():
    app.config["TESTING"] = True

    # Reset global controller state before each test
    battle_controller.run = Run()
    battle_controller.battle = Battle(
        battle_controller.run,
        battle_controller.make_player(),
        battle_controller.make_enemy_for_run(battle_controller.run),
    )

    with app.test_client() as client:
        yield client