
using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using UnityEngine;

[Serializable] public class ProvinceStats : SerializableDictionary<string, float> { }
[Serializable] public class Provinces : SerializableDictionary<string, ProvinceStats> { }
[Serializable] public class TurnEvent { public int turn; public string verb; public Dictionary<string, object> ctx = new(); }

[Serializable]
public class StrategySave {
    public int turn;
    public Provinces provinces = new();
    public SerializableDictionary<string,float> knobs = new();
    public List<TurnEvent> events = new();
}

public class OracleStrategyAdapter {
    public int Turn { get; private set; } = 0;
    public Provinces Provinces = new();
    public Dictionary<string,float> Knobs = new() { {"area_half_life", 720} };
    private readonly Dictionary<string,string> _rules = new();
    private readonly List<TurnEvent> _events = new();
    private readonly Dictionary<int, StrategySave> _snapshots = new();

    public OracleStrategyAdapter() {
        Provinces["Market"] = new ProvinceStats {["security"]=42,["prosperity"]=55,["control"]=50};
        Provinces["Harbor"] = new ProvinceStats {["security"]=37,["prosperity"]=48,["control"]=52};
        _snapshots[0] = MakeSave();
    }

    private void Log(string verb, Dictionary<string, object> ctx){ _events.Add(new TurnEvent { turn = Turn, verb = verb, ctx = ctx }); }

    public void NextTurn(){ Turn += 1; _snapshots[Turn] = MakeSave(); }

    public void AreaBump(string province, string dim, float delta){
        if (!Provinces.ContainsKey(province)) Provinces[province] = new ProvinceStats();
        if (!Provinces[province].ContainsKey(dim)) Provinces[province][dim] = 50;
        Provinces[province][dim] += delta;
        Log("AreaBump", new(){["province"]=province,["dim"]=dim,["delta"]=delta});
    }

    public void DslLoad(string name, string rule){ _rules[name] = rule ?? ""; Log("DSLLoaded", new(){["name"]=name,"size"]=_rules[name].Length}); }

    public (bool matched, List<(string dim, float delta)> applied) DslExec(string name, string province, string outcome){
        if (!_rules.TryGetValue(name, out var txt)) return (false, new());
        bool ok = txt.Contains("OUTCOMES") && txt.Contains("area.");
        var applied = new List<(string,float)>();
        if (ok){
            var lines = txt.Split(new[]{'\n','\r'}, StringSplitOptions.RemoveEmptyEntries);
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
                        AreaBump(province, dim, delta);
                        applied.Add((dim, delta));
                    }
                }
            }
            Log("EncounterCommitted", new(){["province"]=province,["rule"]=name,["outcome"]=outcome,["applied"]=applied.Count});
        }
        return (ok, applied);
    }

    public StrategySave MakeSave(){
        return new StrategySave {
            turn = Turn, provinces = Provinces, knobs = new SerializableDictionary<string,float>(Knobs), events = new List<TurnEvent>(_events)
        };
    }
    public string AutosaveJson(){ return JsonUtility.ToJson(MakeSave(), true); }
    public void LoadJson(string json){
        var s = JsonUtility.FromJson<StrategySave>(json);
        Turn = s.turn; Provinces = s.provinces; Knobs = new(s.knobs); _events.Clear(); _events.AddRange(s.events);
        _snapshots[Turn] = s;
    }
    public void UndoToTurn(int t){
        if (!_snapshots.TryGetValue(t, out var snap)) throw new Exception($"No snapshot for turn {t}");
        Turn = snap.turn; Provinces = snap.provinces; Knobs = new(snap.knobs);
        Log("UndoToTurn", new(){["turn"]=t});
    }
}
