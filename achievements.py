"""
achievements.py
===============
Defines achievements and tracks progress.
"""

from typing import Dict, Any, List
from save_manager import SaveManager

ACHIEVEMENTS_DB: Dict[str, Dict[str, Any]] = {
    "first_blood": {"title": "First Blood", "desc": "Kill your first enemy", "reward": 50},
    "combo_10": {"title": "Matrix Flow", "desc": "Reach a 10x Combo", "reward": 200},
    "combo_20": {"title": "The One", "desc": "Reach a 20x Combo", "reward": 500},
    "score_10k": {"title": "High Scorer", "desc": "Score 10,000 points", "reward": 300},
    "boss_killer": {"title": "Boss Killer", "desc": "Defeat the Space Boss", "reward": 500},
}

_pending_toasts: List[Dict[str, Any]] = []

def check_achievement(save_mgr: SaveManager, ach_id: str, condition: bool) -> None:
    if condition:
        unlocked = save_mgr.get_unlocked_achievements()
        if ach_id not in unlocked and ach_id in ACHIEVEMENTS_DB:
            save_mgr.unlock_achievement(ach_id)
            ach = ACHIEVEMENTS_DB[ach_id]
            save_mgr.add_coins(ach["reward"])
            _pending_toasts.append(ach)

def get_pending_toasts() -> List[Dict[str, Any]]:
    global _pending_toasts
    t = _pending_toasts[:]
    _pending_toasts.clear()
    return t
