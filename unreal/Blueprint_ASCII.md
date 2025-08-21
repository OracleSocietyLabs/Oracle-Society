
# Blueprint Wiring (ASCII guide)

## Demo: Use RPG Adapter in Level Blueprint

Nodes:
```
Event BeginPlay
  └─ Construct Object (Class=OracleRPGAdapter)
       └─ Promote to variable: RPGAdapter
  └─ Call: RPGAdapter.InitDefaults()
  └─ Call: RPGAdapter.DslLoad("OUTCOMES:\n  calm:\n    area.security += 4\n  riot:\n    area.security -= 6")
```

Bind UI Buttons (in UMG Widget or Level Blueprint):
```
OnClicked (BtnUp)   → RPGAdapter.AreaBump("Market","security", +2.0)
OnClicked (BtnDown) → RPGAdapter.AreaBump("Market","security", -2.0)
OnClicked (BtnCalm) → RPGAdapter.DslExec("Market","calm")
OnClicked (BtnRiot) → RPGAdapter.DslExec("Market","riot")
```

Update label:
```
RPGAdapter.Areas["Market"].Metrics["security"] 
  → Format Text "Market.security = {0}"
     → SetText (TxtSecurity)
```
