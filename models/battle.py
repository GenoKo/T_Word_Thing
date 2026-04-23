import random
from models.entities import Character, Skill, Item
from models.run import Run
from models.item_catalog import get_item

PERSONALITY_INTEREST = {
    "Curious": 2,
    "Proud": 0,
    "Cowardly": 1,
    "Hostile": -1,
    "Fanatical": -2,
}

class Battle:
    def __init__(self, run: Run, player: Character, enemy: Character):
        self.run = run
        self.player = player
        self.enemy = enemy

        self.menu = "main"
        self.log = "Choose an action."
        self.ended = False
        self.result = None  # None / "win" / "lose" / "escape"

        self.last_talk_reply = ""

        #Enemy remembering
        self.turn_number = 1
        self.player_actions_history = []
        self.enemy_conversation_interest = PERSONALITY_INTEREST.get(self.enemy.personality_name, 0)
        self.in_conversation = False
        self.last_player_talk = ""
        self.last_enemy_talk = ""

        self.enemy_will_to_fight = 100
        self.enemy_has_surrendered = False
        self.escape_bonus = 0.0

    # -------- Run / Encounter Controls --------
    def new_run(self, new_player: Character, new_enemy: Character) -> None:
        self.run.reset()
        self.player = new_player
        self.enemy = new_enemy
        self.enemy_conversation_interest = PERSONALITY_INTEREST.get(self.enemy.personality_name, 0)
        self.player_actions_history = []
        self.in_conversation = False
        self.last_player_talk = ""
        self.last_enemy_talk = ""
        self.turn_number = 1
        self._reset_encounter_state()
        self.log = "A new run begins!"

        self.enemy_will_to_fight = 100
        self.enemy_has_surrendered = False
        self.escape_bonus = 0.0

    def next_encounter(self, new_enemy: Character) -> None:
        """
        Keeps player as-is, but resets enemy and encounter state.
        """
        self.run.advance()
        self.enemy = new_enemy
        self.enemy_conversation_interest = PERSONALITY_INTEREST.get(self.enemy.personality_name, 0)
        self.player_actions_history = []
        self.in_conversation = False
        self.last_player_talk = ""
        self.last_enemy_talk = ""
        self.turn_number = 1
        self._reset_encounter_state()
        self.log = f"Encounter {self.run.encounter_number} begins!"


    def _reset_encounter_state(self) -> None:
        self.menu = "main"
        self.ended = False
        self.result = None

    # -------- Main API --------
    def process_action(self, action: str) -> None:
        # Allow run/encounter buttons even if ended
        if action == "new_run":
            return  # controller handles calling new_run()
        if action == "next_encounter":
            return  # controller handles calling next_encounter()
    

        if self.ended:
            self.log = "Encounter ended. Choose Next Encounter or New Run."
            return

        # navigation
        if action == "open_skills":
            self.menu = "skills"
            self.log = "Choose a skill."
            return
        if action == "open_items":
            self.menu = "items"
            self.log = "Choose an item."
            return
        if action == "back":
            self.menu = "main"
            self.log = "Choose an action."
            return

        # main actions
        if action == "do_attack":
            self.player_actions_history.append("attack")
            self.in_conversation = False
            self.log = self._basic_attack(self.player, self.enemy)
            self.menu = "main"
            self.enemy_conversation_interest -= 1
            self._after_player_action()
            return
        
        if action == "open_talk":
            self.menu = "talk"
            self.log = f"You attempt to talk to {self.enemy.name}."
            return

        # if action == "back":
        #     self.menu = "main"
        #     self.log = "Choose an action."
        #     return

        if action == "do_flee":
            base_escape_chance = 0.5
            final_escape_chance = min(0.95, base_escape_chance + self.escape_bonus)

            success = random.random() < final_escape_chance
            self.log = (
                f"You fled successfully! There's no shame in running away."
                if success else
                "You couldn't escape!"
            )
            self.menu = "main"

            if success:
                self.ended = True
                self.result = "escape"
            else:
                self._enemy_turn_if_needed()
                self._check_end()
            return

        # skill selection
        if action.startswith("do_skill:"):
            key = action.split(":", 1)[1]
            skill = self._find_skill(key)
            if not skill:
                self.menu = "skills"
                self.log = "Skill not found."
                return

            if skill.sp_cost and not self.player.spend_sp(skill.sp_cost):
                self.menu = "skills"
                self.log = "Not enough SP!"
                return

            self.player_actions_history.append(f"skill:{skill.key}")
            self.in_conversation = False
            self.log = self._use_skill(self.player, self.enemy, skill)
            self.menu = "main"
            self.enemy_conversation_interest -= 1
            self._after_player_action()
            return


        # item selection (comes from run.inventory now)
        if action.startswith("do_item:"):
            key = action.split(":", 1)[1]

            if self.run.item_qty(key) <= 0:
                self.menu = "items"
                self.log = "You don't have that item."
                return

            item = get_item(key)
            if not item:
                self.menu = "items"
                self.log = "Item not found."
                return

            # consume 1 item
            self.run.remove_item(key, 1)

            self.player_actions_history.append(f"item:{item.key}")
            self.in_conversation = False
            self.log = self._use_item(self.player, item)
            self.menu = "main"
            self.enemy_conversation_interest -= 1
            self._after_player_action()
            return

        self.log = "Unknown action."
        self.menu = "main"

    # -------- Turn flow helpers --------
    def _after_player_action(self) -> None:
        self._check_end()
        if not self.ended:
            self._enemy_turn_if_needed()
            self._check_end()

        self.player.tick_effects()
        self.enemy.tick_effects()
        self.turn_number += 1

    def _enemy_turn_if_needed(self) -> None:
        if self.enemy.is_alive() and self.player.is_alive():
            self._enemy_action()

    def _check_end(self) -> None:
        if not self.player.is_alive():
            self.log += "\nYou were defeated..."
            self.ended = True
            self.result = "lose"
        elif not self.enemy.is_alive():
            reward = self._gold_reward_for_win()
            self.run.add_gold(reward)

            self.log += f"\nYou won! +{reward} gold."

            if self.enemy.is_boss:
                self.run.bosses_defeated += 1
                self.run.add_item("bomb", 1)
                self.log += "\nBoss defeated! You obtained a Bomb."
                self.log += f"\nBosses defeated: {self.run.bosses_defeated}"

            self.ended = True
            self.result = "win"
            
    # -------- Core actions --------

    def _basic_attack(self, attacker: Character, defender: Character) -> str:
        dmg = self._calculate_damage(attacker, defender, attacker.attack)
        defender.take_damage(dmg)
        return f"{attacker.name} attacks for {dmg} damage!"

    def _calculate_damage(self, attacker: Character, defender: Character, base_attack: int) -> int:
        multiplier = random.uniform(0.7, 1.3)
        raw_damage = int(round(base_attack * multiplier))
        final_damage = raw_damage - defender.defense

        # Always deal at least 1 damage
        return max(1, final_damage)

    def _use_skill(self, user: Character, target: Character, skill: Skill) -> str:
        dmg = self._calculate_damage(user, target, skill.damage)
        target.take_damage(dmg)
        cost_txt = f" (SP -{skill.sp_cost})" if skill.sp_cost else ""
        return f"{user.name} uses {skill.name}{cost_txt} for {dmg} damage!"

    def _use_skill(self, user: Character, target: Character, skill: Skill) -> str:
        target.take_damage(skill.damage)
        cost_txt = f" (SP -{skill.sp_cost})" if skill.sp_cost else ""
        return f"{user.name} uses {skill.name}{cost_txt} for {skill.damage} damage!"

    def _use_item(self, user: Character, item: Item) -> str:
        messages = []

        # Healing
        if item.heal > 0:
            user.heal(item.heal)
            messages.append(f"{user.name} heals {item.heal} HP")

        # Damage
        if item.damage > 0:
            dmg = self._calculate_damage(user, self.enemy, item.damage)
            self.enemy.take_damage(dmg)
            messages.append(f"{self.enemy.name} takes {dmg} damage")

        # Buff / Debuff
        if item.effect_stat and item.effect_turns > 0:
            target = user if item.target == "self" else self.enemy
            target.add_effect(item.effect_stat, item.effect_amount, item.effect_turns)

            if item.effect_amount > 0:
                messages.append(f"{target.name}'s {item.effect_stat} increased for {item.effect_turns} turns")
            else:
                messages.append(f"{target.name}'s {item.effect_stat} decreased for {item.effect_turns} turns")

        if not messages:
            return f"{user.name} uses {item.name}, but nothing happens."

        return f"{user.name} uses {item.name}! " + "; ".join(messages)

    def _find_skill(self, key: str):
        return next((s for s in self.player.skills if s.key == key), None)

    def _find_item(self, key: str):
        return next((i for i in self.player.items if i.key == key), None)
    
    def _gold_reward_for_win(self) -> int:
        base = 10 + (self.run.encounter_number - 1) * 2

        reward = int(round(base * self.enemy.reward_multiplier))

        # optional extra boss bonus
        if self.enemy.is_boss:
            reward += 10

        return reward
    

    def _enemy_action(self):
        enemy = self.enemy
        player = self.player

        action = None

        # ---- AI decision ----
        if enemy.ai_type == "basic":
            action = "attack"

        elif enemy.ai_type == "aggressive":
            action = "attack" if random.random() < 0.85 else "heavy"

        elif enemy.ai_type == "defensive":
            if enemy.hp < enemy.max_hp * 0.5 and random.random() < 0.4:
                action = "debuff"
            else:
                action = "attack"

        elif enemy.ai_type == "wild":
            action = random.choice(["attack", "heavy"])

        elif enemy.ai_type == "boss":
            r = random.random()
            if r < 0.6:
                action = "attack"
            elif r < 0.85:
                action = "heavy"
            else:
                action = "debuff"

        else:
            action = "attack"

        # ---- Execute action ----
        if action == "attack":
            msg = self._basic_attack(enemy, player)

        elif action == "heavy":
            dmg = self._calculate_damage(enemy, player, int(enemy.attack * 1.4))
            player.take_damage(dmg)
            msg = f"{enemy.name} uses a heavy attack! {player.name} takes {dmg} damage"

        elif action == "debuff":
            player.add_effect("defense", -2, 2)
            msg = f"{enemy.name} weakens {player.name}'s defense!"

        else:
            msg = self._basic_attack(enemy, player)

        self.log += "\n" + msg

    #talking thing
    def react_to_talk(self, player_text: str, result: dict) -> None:
        self.player_actions_history.append("talk")
        self.last_player_talk = player_text

        reply = result.get("reply", "...")
        emotion = result.get("emotion", result.get("outcome", "none"))
        interest_delta = int(result.get("interest_delta", 0))
        enemy_action = result.get("enemy_action", "attack")

        self.enemy_conversation_interest += interest_delta
        self.last_enemy_talk = reply
        self.last_talk_reply = reply

        self.log = f'You say: "{player_text}"\n{self.enemy.name}: "{reply}"'

        if emotion == "anger":
            self.enemy.add_effect("attack", 1, 2)
            self.enemy_will_to_fight += 5
            self.log += f"\n{self.enemy.name} becomes enraged!"
            self.in_conversation = False

        elif emotion == "fear":
            self.enemy.add_effect("defense", -1, 2)
            self.enemy_will_to_fight -= 20
            self.escape_bonus += 0.2
            self.log += f"\n{self.enemy.name} looks shaken!"

        elif emotion == "respect":
            self.enemy_will_to_fight -= 15
            self.escape_bonus += 0.1
            self.log += f"\n{self.enemy.name} seems to respect your words."

        elif emotion == "curiosity":
            self.enemy_will_to_fight -= 10
            self.log += f"\n{self.enemy.name} seems interested in talking."

        else:
            self.enemy_will_to_fight -= 5


        # Enemy reaction consumes its turn
        if not self.ended:
            if enemy_action == "attack":
                self._enemy_action()
                self.in_conversation = False

            elif enemy_action == "talk":
                self.log += f"\n{self.enemy.name} continues the conversation instead of attacking."
                self.enemy_will_to_fight -= 5
                self.in_conversation = True

            elif enemy_action == "hesitate":
                self.log += f"\n{self.enemy.name} hesitates instead of attacking."
                self.enemy_will_to_fight -= 10
                self.escape_bonus += 0.25
                self.in_conversation = False

            else:
                self._enemy_action()
                self.in_conversation = False

            self._check_end()
            self.player.tick_effects()
            self.enemy.tick_effects()
            self.turn_number += 1

        self.enemy_will_to_fight = max(0, min(100, self.enemy_will_to_fight))
        self.escape_bonus = max(0.0, min(0.45, self.escape_bonus))

        self._check_surrender()
        self.menu = "talk" if self.in_conversation and not self.ended else "main"

        

    def _check_surrender(self) -> None:
        if self.enemy_will_to_fight <= 0 and not self.ended:
            self.enemy_has_surrendered = True
            self.ended = True
            self.result = "peace"

            reward = self._gold_reward_for_win()
            self.run.add_gold(reward)

            self.log += f"\n{self.enemy.name} no longer wants to fight."
            self.log += f"\nYou resolved the battle peacefully! +{reward} gold."