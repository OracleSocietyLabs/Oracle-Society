
using UnityEngine;
using UnityEngine.UI;

public class OracleUnityDemo : MonoBehaviour
{
    public Text MarketSecurityText;
    public Slider DeltaSlider;
    public Button BumpUpBtn;
    public Button BumpDownBtn;
    public Button CalmBtn;
    public Button RiotBtn;

    private OracleRPGAdapter rpg;

    void Awake(){
        rpg = new OracleRPGAdapter();
        rpg.DslLoad(@"WHEN area.security < 50
NPCS any
KIND crowd
STAKES ""Unity Demo""
OUTCOMES:
  calm:
    area.security += 4
  riot:
    area.security -= 6");
    }

    void Start(){
        if (BumpUpBtn) BumpUpBtn.onClick.AddListener(()=> {
            rpg.AreaBump("Market","security", Mathf.Abs(DeltaSlider? DeltaSlider.value : 1f));
            Refresh();
        });
        if (BumpDownBtn) BumpDownBtn.onClick.AddListener(()=> {
            rpg.AreaBump("Market","security", -(Mathf.Abs(DeltaSlider? DeltaSlider.value : 1f)));
            Refresh();
        });
        if (CalmBtn) CalmBtn.onClick.AddListener(()=> {
            rpg.DslExec("Market","calm"); Refresh();
        });
        if (RiotBtn) RiotBtn.onClick.AddListener(()=> {
            rpg.DslExec("Market","riot"); Refresh();
        });
        Refresh();
    }

    void Refresh(){
        float val = 0f;
        if (rpg.Areas.ContainsKey("Market") && rpg.Areas["Market"].ContainsKey("security"))
            val = rpg.Areas["Market"]["security"];
        if (MarketSecurityText) MarketSecurityText.text = $"Market.security = {val:0.0}";
    }
}
