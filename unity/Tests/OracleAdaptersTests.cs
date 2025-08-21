
using NUnit.Framework;
using UnityEngine;

public class OracleAdaptersTests
{
    [Test]
    public void RPG_AreaBump_ChangesMetric()
    {
        var rpg = new OracleRPGAdapter();
        float before = rpg.Areas["Market"]["security"];
        rpg.AreaBump("Market","security", +3);
        Assert.AreEqual(before + 3, rpg.Areas["Market"]["security"], 0.001f);
    }

    [Test]
    public void RPG_Rumor_ShiftsBeliefWithin01()
    {
        var rpg = new OracleRPGAdapter();
        rpg.Rumor("player=arsonist","tavern",+1,0.9f);
        Assert.That(rpg.NPCs["N1"].beliefs["player=arsonist"], Is.InRange(0f,1f));
        Assert.That(rpg.NPCs["N2"].beliefs["player=arsonist"], Is.InRange(0f,1f));
    }

    [Test]
    public void RPG_DslExec_AppliesOutcome()
    {
        var rpg = new OracleRPGAdapter();
        rpg.DslLoad("OUTCOMES:\n  calm:\n    area.security += 4");
        float before = rpg.Areas["Market"]["security"];
        var res = rpg.DslExec("Market","calm");
        Assert.IsTrue(res.matched);
        Assert.AreEqual(before + 4, rpg.Areas["Market"]["security"], 0.001f);
    }

    [Test]
    public void Strategy_UndoToTurn_RestoresSnapshot()
    {
        var s = new OracleStrategyAdapter();
        s.DslLoad("unrest","OUTCOMES:\n  suppress:\n    area.security += 3");
        s.NextTurn();
        s.DslExec("unrest","Market","suppress");
        var after = s.Provinces["Market"]["security"];
        s.NextTurn();
        s.AreaBump("Market","security",-10);
        s.UndoToTurn(1);
        Assert.AreEqual(after, s.Provinces["Market"]["security"], 0.001f);
    }
}
