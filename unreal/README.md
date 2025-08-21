
# Unreal Integration (RPG & Strategy Adapters)

Files:
- `OracleRPGAdapter.h/.cpp` — in-process RPG system (AreaBump, Rumor, DSL Exec, Save/Load JSON).
- `OracleStrategyAdapter.h/.cpp` — per-turn Strategy system (NextTurn, UndoToTurn, DSL Exec, Autosave JSON).

## Setup
1. Copy `.h/.cpp` to your Unreal project's Source module.
2. In your `*.Build.cs`, add:
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "Json", "JsonUtilities" });
```
3. Include the headers where needed and expose to Blueprints if desired.

## Usage (Blueprint)
- Construct `UOracleRPGAdapter`, call `InitDefaults()` once.
- Call `DslLoad`, then `DslExec("Market","calm")`, or `AreaBump`/`Rumor` during gameplay.
- Use `MakeSavegameJson()` to persist; `LoadSavegameJson()` to restore.
- For Strategy: `InitDefaults()` → `NextTurn()` each turn → `DslExec(...)` → `AutosaveJson()`; `UndoToTurn(T)` restores older snapshot.
