from flask import Blueprint, render_template, request
from models.entities import Character, Skill
from models.battle import Battle
from models.run import Run
from models.enemy_factory import make_enemy
from models.item_catalog import get_item
from models.shop_catalog import SHOP_STOCK, get_price

from services.llm_service import talk_to_enemy

battle_bp = Blueprint("battle", __name__)

def build_inventory_display(run):
    inventory_display = []

    for key, qty in run.inventory.items():
        item = get_item(key)
        if not item:
            continue

        inventory_display.append({
            "key": key,
            "name": item.name,
            "qty": qty,
            "description": item.description,
        })

    inventory_display.sort(key=lambda x: x["name"])
    return inventory_display

def make_player() -> Character:
    p = Character("Hero", 100, 8, defense=3, sp=30)
    p.skills = [
        Skill("fireball", "🔥Fireball", damage=10, sp_cost=3, description="Throws a fireball at the enemy. ",),
        Skill("slash", "🗡️Power Slash", damage=16, sp_cost=5, description="Cuts the enemy with a heavy slash. ",),
    ]
    return p

def make_enemy_for_run(run) -> Character:
    return make_enemy(
        difficulty=run.next_difficulty,
        is_boss=run.is_boss_encounter(),
        bosses_defeated=run.bosses_defeated
    )

def make_enemy_for_next_encounter(run) -> Character:
    next_encounter_number = run.encounter_number + 1
    is_boss = (next_encounter_number % 5 == 0)

    return make_enemy(
        difficulty=run.next_difficulty,
        is_boss=is_boss,
        bosses_defeated=run.bosses_defeated
    )

run = Run()
battle = Battle(run, make_player(), make_enemy_for_run(run))

@battle_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        action = request.form.get("action", "")



        # ========= Main menu actions =============
        if action == "start_run":
            run.reset()
            run.state = "battle"
            battle.new_run(make_player(), make_enemy_for_run(run))
            run.add_item("potion", 2)
            run.add_item("bomb", 1)


        # test test test 

        elif action == "open_talk":
            battle.process_action("open_talk")

        # elif action == "submit_talk":
        #     player_text = request.form.get("talk_input", "").strip()

        #     if not player_text:
        #         battle.menu = "talk"
        #         battle.log = "Say something first."
        #     else:
        #         result = talk_to_enemy(battle.enemy, player_text)

        #         reply = result.get("reply", "...")
        #         outcome = result.get("outcome", "none")
        #         strength = int(result.get("effect_strength", 0))

        #         battle.last_talk_reply = reply
        #         battle.log = f'You say: "{player_text}"\n{battle.enemy.name}: "{reply}"'

        #         # safe game-side interpretation
        #         if outcome == "anger":
        #             battle.enemy.add_effect("attack", 1 + strength, 2)
        #             battle.log += f"\n{battle.enemy.name} becomes enraged!"
        #         elif outcome == "fear":
        #             battle.enemy.add_effect("defense", -1 - strength, 2)
        #             battle.log += f"\n{battle.enemy.name} looks shaken!"
        #         elif outcome == "respect":
        #             battle.enemy.add_effect("attack", -1, 1)
        #             battle.log += f"\n{battle.enemy.name} hesitates."
        #         elif outcome == "confuse":
        #             battle.enemy.add_effect("defense", -1, 1)
        #             battle.log += f"\n{battle.enemy.name} seems confused."

        #         battle.menu = "main"

        #         if not battle.ended:
        #             battle._enemy_turn_if_needed()
        #             battle._check_end()

        elif action == "submit_talk":
            player_text = request.form.get("talk_input", "").strip()

            if not player_text:
                battle.menu = "talk"
                battle.log = "Say something first."
            else:
                result = talk_to_enemy(
                    enemy=battle.enemy,
                    player_message=player_text,
                    context={
                        "turn_number": battle.turn_number,
                        "player_actions_history": battle.player_actions_history[-6:],
                        "enemy_conversation_interest": battle.enemy_conversation_interest,
                        "in_conversation": battle.in_conversation,
                        "last_player_talk": battle.last_player_talk,
                        "last_enemy_talk": battle.last_enemy_talk,
                    }
                )

                battle.react_to_talk(player_text, result)


        elif action == "back_to_menu":
            run.state = "menu"

        # ===== Choose difficulty =======
        elif action.startswith("set_diff:"):
            diff = action.split(":", 1)[1]
            run.next_difficulty = diff

        # ======= Post Battle actions ========
        elif action == "new_run":
            run.reset()
            battle.new_run(make_player(), make_enemy_for_run(run))
            run.add_item("potion", 2)
            run.add_item("bomb", 1)

        elif action == "next_encounter":
            battle.next_encounter(make_enemy_for_next_encounter(run))

        # ====== Shop =========
        elif action == "open_shop":
            run.state = "shop"

        elif action == "leave_shop":
            run.state = "battle"

        elif action.startswith("buy:"):
            key = action.split(":", 1)[1]
            price = get_price(key)
            if price is not None and run.spend_gold(price):
                run.add_item(key, 1)

        else:
            battle.process_action(action)

    if run.state == "menu":
        return render_template("menu.html")

    if run.state == "shop":
        shop_items = []
        for key, data in SHOP_STOCK.items():
            item = get_item(key)
            if not item:
                continue
            shop_items.append({
                "key": key,
                "name": item.name,
                "price": data["price"],
                "owned": run.item_qty(key),
                "description": item.description,   # NEW
            })

        return render_template(
            "shop.html",
            gold=run.gold,
            shop_items=shop_items,
            world_level=run.bosses_defeated + 1,
        )

    return render_template(
        "battle.html",
        player=battle.player,
        enemy=battle.enemy,
        menu=battle.menu,
        log=battle.log,
        ended=battle.ended,
        result=battle.result,
        encounter_number=battle.run.encounter_number,
        next_difficulty=run.next_difficulty,
        inventory=run.inventory,
        gold=run.gold,
        inventory_display=build_inventory_display(run),
        is_next_boss=(battle.run.encounter_number + 1) % 5 == 0,
        world_level=run.bosses_defeated + 1,
        enemy_will_to_fight=battle.enemy_will_to_fight,
        escape_bonus=battle.escape_bonus,
    )