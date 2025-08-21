
from strategy_adapter import StrategyAdapter

RULE = """
WHEN area.security < 50
NPCS any
KIND unrest
STAKES "Strategy demo"
OUTCOMES:
  suppress:
    area.security += 3
  riot:
    area.security -= 8
"""

if __name__ == "__main__":
    s = StrategyAdapter()
    s.dsl_load("unrest_rule", RULE)
    s.next_turn()
    s.dsl_exec("unrest_rule","Market","suppress")
    auto = s.autosave()
    print("Turn:", auto["turn"])
    print("Market:", s.provinces["Market"])
    s.next_turn()
    s.area_bump("Market","prosperity",+5)
    s.undo_to_turn(1)
    print("After undo -> Market:", s.provinces["Market"])
