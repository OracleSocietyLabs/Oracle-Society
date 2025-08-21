
from rpg_adapter import RPGAdapter

RULE = """
WHEN area.security < 50
NPCS any
KIND crowd
STAKES "RPG demo"
OUTCOMES:
  calm:
    area.security += 4
  escalate:
    area.security -= 6
"""

if __name__ == "__main__":
    rpg = RPGAdapter()
    rpg.dsl_load(RULE)
    rpg.rumor("player=arsonist","tavern",1,0.9)
    rpg.dsl_exec("Market","calm")
    save = rpg.make_savegame()
    print("RPG savegame keys:", list(save.keys()))
    print("Market:", rpg.areas["Market"])
    print("Timeline len:", len(save["timeline"]))
