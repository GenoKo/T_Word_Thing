import json
import os
from typing import Any

from google import genai
from google.genai import types


def _fallback_response(enemy, reason: str = "") -> dict[str, Any]:

    # Default return for when the AI thing fails
    reply = f"{enemy.name} refuses to answer."
    if reason:
        reply = f"{enemy.name} hesitates. ({reason})"

    return {
        "reply": reply,
        "emotion": "none",
        "interest_delta": 0,
        "enemy_action": "attack",
    }


def talk_to_enemy(enemy, player_message: str, context: dict | None = None) -> dict[str, Any]:
    """
    Returns a structured response:
    {
      "reply": str,
      "emotion": "anger|fear|respect|curiosity|none",
      "interest_delta": int,
      "enemy_action": "attack|talk|hesitate"
    }
    """
    context = context or {}

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return _fallback_response(enemy, "missing API key")

    turn_number = context.get("turn_number", 1)
    player_actions_history = context.get("player_actions_history", [])
    enemy_conversation_interest = context.get("enemy_conversation_interest", 0)
    in_conversation = context.get("in_conversation", False)
    last_player_talk = context.get("last_player_talk", "")
    last_enemy_talk = context.get("last_enemy_talk", "")

    attacked_before = (
        "attack" in player_actions_history
        or any(str(a).startswith("skill:") for a in player_actions_history)
    )

    # The prompt
    
    system_prompt = f"""
You are an enemy in a turn-based RPG battle.

Enemy name: {enemy.name}
Enemy personality: {enemy.personality_name}
Enemy traits: {", ".join(enemy.personality_traits)}
Enemy personality description: {enemy.personality_description}

Current HP: {enemy.hp}/{enemy.max_hp}
Enemy is boss: {enemy.is_boss}
Enemy AI type: {enemy.ai_type}

Conversation interest score: {enemy_conversation_interest}
Currently in conversation: {in_conversation}

Turn number: {turn_number}
Recent player actions: {player_actions_history}
Player has attacked before talking: {attacked_before}

Previous player line: {last_player_talk if last_player_talk else "None"}
Previous enemy line: {last_enemy_talk if last_enemy_talk else "None"}

Player says:
"{player_message}"

Your job:
1. Reply in character.
2. Decide the emotional reaction.
3. Decide how the conversation interest changes.
4. Decide whether the enemy attacks, keeps talking, or hesitates.

Rules:
- If the player has already attacked and then suddenly talks, hostile / proud / fanatical personalities should usually react worse.
- Curious enemies are more willing to continue talking.
- Cowardly enemies may hesitate.
- If the enemy is interested in talking, they may choose "talk" instead of "attack".
- If the player angers the enemy, choose "attack".
- Keep the reply short, natural, and in-character.
- Do not narrate gameplay rules. Just return JSON.

Allowed emotion values:
anger, fear, respect, curiosity, none

Allowed enemy_action values:
attack, talk, hesitate
"""

    schema = {
        "type": "object",
        "properties": {
            "reply": {"type": "string"},
            "emotion": {
                "type": "string",
                "enum": ["anger", "fear", "respect", "curiosity", "none"],
            },
            "interest_delta": {"type": "integer"},
            "enemy_action": {
                "type": "string",
                "enum": ["attack", "talk", "hesitate"],
            },
        },
        "required": ["reply", "emotion", "interest_delta", "enemy_action"],
    }

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=system_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_json_schema=schema,
                temperature=0.8,
            ),
        )

        text = response.text.strip()
        data = json.loads(text)

        # final validation
        reply = str(data.get("reply", "...")).strip() or "..."
        emotion = data.get("emotion", "none")
        interest_delta = int(data.get("interest_delta", 0))
        enemy_action = data.get("enemy_action", "attack")

        if emotion not in {"anger", "fear", "respect", "curiosity", "none"}:
            emotion = "none"

        if enemy_action not in {"attack", "talk", "hesitate"}:
            enemy_action = "attack"

        return {
            "reply": reply,
            "emotion": emotion,
            "interest_delta": interest_delta,
            "enemy_action": enemy_action,
        }

    except Exception as e:
        return _fallback_response(enemy, str(e))