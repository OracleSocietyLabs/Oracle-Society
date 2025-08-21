
# Unity Demo (no server)
1) Create a Canvas with:
   - Text `MarketSecurityText`
   - Slider `DeltaSlider` (min 1, max 10, wholeNumbers true)
   - Buttons: `BumpUpBtn`, `BumpDownBtn`, `CalmBtn`, `RiotBtn`
2) Add `OracleUnityDemo` on an empty GameObject and assign references.
3) Press Play. Use the slider + buttons to change Market.security and trigger DSL outcomes.


---

## Sample Scene (Hierarchy layout)

Create a new Scene and build this minimal UI:

```
Canvas (UI Scale Mode: Scale With Screen Size)
└── Panel (Anchor: Stretch, Padding all sides 40)
    ├── Text (name: MarketSecurityText, Font Size 28, Anchor TopLeft)
    ├── Slider (name: DeltaSlider, Min:1 Max:10 WholeNumbers:On, Width: 300)
    ├── HorizontalLayout (empty GameObject + HorizontalLayoutGroup)
    │   ├── Button (name: BumpUpBtn, Text: "+Δ")
    │   ├── Button (name: BumpDownBtn, Text: "-Δ")
    ├── HorizontalLayout (empty GameObject + HorizontalLayoutGroup)
    │   ├── Button (name: CalmBtn, Text: "Calm")
    │   ├── Button (name: RiotBtn, Text: "Riot")
└── Empty GameObject (name: OracleDemoHost)
    └─ Add Component: OracleUnityDemo
       - Assign:
         MarketSecurityText -> Text
         DeltaSlider        -> Slider
         BumpUpBtn          -> Button
         BumpDownBtn        -> Button
         CalmBtn            -> Button
         RiotBtn            -> Button
```

> Tip: Στον `OracleUnityDemo`, μπορείς να αλλάξεις τη DSL που φορτώνεται στο `Awake()` για να τεστάρεις διαφορετικά outcomes.

### Quick sanity check
- Πατάς `+Δ`/`-Δ` → αλλάζει το `Market.security` κατά το value του slider.
- Πατάς `Calm` → εκτελεί `area.security += 4` στο outcome `calm`.
- Πατάς `Riot` → εκτελεί `area.security -= 6` στο outcome `riot`.
