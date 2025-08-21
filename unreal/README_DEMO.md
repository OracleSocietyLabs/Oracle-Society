
# Unreal UMG Demo (no server)
1) Add `OracleRPGAdapter.h/.cpp` and `OracleDemoWidget.h/.cpp` to your module. Build with dependencies: "UMG", "UMGEditor" (for designer), "Json", "JsonUtilities".
2) Create a UMG Widget Blueprint (e.g., `WBP_OracleDemo`), set Parent Class = `OracleDemoWidget`.
3) In Designer, add:
   - Buttons named `BtnUp`, `BtnDown`, `BtnCalm`, `BtnRiot`
   - TextBlock named `TxtSecurity`
4) Place the widget in a simple level via `Create Widget` and `Add to Viewport` from PlayerController/Level Blueprint.
5) Play: use buttons to bump/trigger DSL outcomes; label shows current Market.security.
