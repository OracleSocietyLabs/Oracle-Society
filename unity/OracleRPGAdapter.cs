
using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using UnityEngine;

[Serializable] public class OracleAreaStats : SerializableDictionary<string, float> { }
[Serializable] public class OracleAreas : SerializableDictionary<string, OracleAreaStats> { }
[Serializable] public class OracleBeliefs : SerializableDictionary<string, float> { }
[Serializable] public class OracleNPC { public string name; public OracleBeliefs beliefs = new(); }
[Serializable] public class OracleNPCs : SerializableDictionary<string, OracleNPC> { }
[Serializable] public class RPGEvent { public double t; public string verb; public Dictionary<string, object> ctx = new(); }

[Serializable]
public class RPGSavegame {
    public OracleAreas areas = new();
    public OracleNPCs npcs = new();
    public SerializableDictionary<string, float> knobs = new();
    public List<RPGEvent> timeline = new();
}

public class OracleRPGAdapter {
    public OracleAreas Areas = new();
    public OracleNPCs NPCs = new();
    public Dictionary<string, float> Knobs = new() {
        {"memory_half_life",240}, {"prestige_half_life",480}, {"area_half_life",720}
    };
    private string _dsl = "";
    private readonly List<RPGEvent> _timeline = new();

    public OracleRPGAdapter() {
        Areas["Market"] = new OracleAreaStats {["security"]=45,["prosperity"]=55,["control"]=50,["culture"]=50,["ecology"]=50};
        Areas["Harbor"] = new OracleAreaStats {["security"]=38,["prosperity"]=48,["control"]=52,["culture"]=46,["ecology"]=49};
        NPCs["N1"] = new OracleNPC { name="Aella", beliefs = new OracleBeliefs {["player=arsonist"]=0.8f} };
        NPCs["N2"] = new OracleNPC { name="Boros", beliefs = new OracleBeliefs {["player=arsonist"]=0.6f} };
    }

    private void Log(string verb, Dictionary<string, object> ctx){
        _timeline.Add(new RPGEvent { t = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()/1000.0, verb = verb, ctx = ctx });
    }

    public void AreaBump(string area, string dim, float delta){
        if (!Areas.ContainsKey(area)) Areas[area] = new OracleAreaStats();
        if (!Areas[area].ContainsKey(dim)) Areas[area][dim] = 50;
        Areas[area][dim] += delta;
        Log("AreaBump", new(){["area"]=area,["dim"]=dim,["delta"]=delta});
    }

    public void Rumor(string hypothesis, string source, int polarity, float reliability){
        foreach (var kv in NPCs){
            var b = kv.Value.beliefs;
            if (!b.ContainsKey(hypothesis)) b[hypothesis] = 0.5f;
            b[hypothesis] = Mathf.Clamp01(b[hypothesis] + 0.05f * polarity * reliability);
        }
        Log("RumorInjected", new(){["hypothesis"]=hypothesis,["source"]=source,["polarity"]=polarity,["reliability"]=reliability});
    }

    public void DslLoad(string rule){ _dsl = rule ?? ""; Log("DSLLoaded", new(){["size"]=_dsl.Length}); }

    public (bool matched, List<(string dim, float delta)> applied) DslExec(string area, string outcome){
        bool ok = _dsl.Contains("OUTCOMES") && _dsl.Contains("area.");
        var applied = new List<(string,float)>();
        if (ok){
            var lines = _dsl.Split(new[]{'\n','\r'}, StringSplitOptions.RemoveEmptyEntries);
            bool pick=false;
            var pat = new Regex(@"area\.(\w+)\s*([+\-]=)\s*([\-0-9\.]+)");
            foreach(var ln in lines){
                var trimmed = ln.Trim();
                if (Regex.IsMatch(trimmed, @"^"+Regex.Escape(outcome)+@"\s*:")) { pick=true; continue; }
                if (pick && Regex.IsMatch(trimmed, @"^\w+\s*:")) break;
                if (pick){
                    var m = pat.Match(trimmed);
                    if (m.Success){
                        string dim = m.Groups[1].Value;
                        string op  = m.Groups[2].Value;
                        float num  = float.Parse(m.Groups[3].Value, System.Globalization.CultureInfo.InvariantCulture);
                        float delta = (op == "+=") ? num : -num;
                        AreaBump(area, dim, delta);
                        applied.Add((dim, delta));
                    }
                }
            }
            Log("EncounterCommitted", new(){["area"]=area,["outcome"]=outcome,["applied"]=applied.Count});
        }
        return (ok, applied);
    }

    public string MakeSavegameJson(){
        var sg = new RPGSavegame{
            areas = Areas,
            npcs = NPCs,
            knobs = new SerializableDictionary<string,float>(Knobs),
            timeline = _timeline
        };
        return JsonUtility.ToJson(sg, true);
    }
    public void LoadSavegameJson(string json){
        var sg = JsonUtility.FromJson<RPGSavegame>(json);
        Areas = sg.areas; NPCs = sg.npcs; Knobs = new(sg.knobs);
        // timeline optional
    }
}
