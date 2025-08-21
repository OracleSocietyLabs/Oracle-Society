
#include "OracleStrategyAdapter.h"
#include "Regex.h"
#include "JsonObjectConverter.h"

void UOracleStrategyAdapter::InitDefaults(){
  Turn = 0; Provinces.Empty(); Knobs.Empty(); Rules.Empty(); Events.Empty(); SnapshotsByTurn.Empty();
  FProvinceStats Market; Market.Metrics.Add("security",42); Market.Metrics.Add("prosperity",55); Market.Metrics.Add("control",50);
  Provinces.Add("Market", Market);
  FProvinceStats Harbor; Harbor.Metrics.Add("security",37); Harbor.Metrics.Add("prosperity",48); Harbor.Metrics.Add("control",52);
  Provinces.Add("Harbor", Harbor);
  Knobs.Add("area_half_life", 720);
  SnapshotsByTurn.Add(0, AutosaveJson());
}

void UOracleStrategyAdapter::NextTurn(){
  Turn += 1;
  SnapshotsByTurn.Add(Turn, AutosaveJson());
}

void UOracleStrategyAdapter::AreaBump(const FString& Province, const FString& Dim, float Delta){
  FProvinceStats* P = Provinces.Find(Province);
  if(!P){ FProvinceStats NewP; Provinces.Add(Province, NewP); P = Provinces.Find(Province); }
  float* V = P->Metrics.Find(Dim);
  if(!V){ P->Metrics.Add(Dim, 50.f); V = P->Metrics.Find(Dim); }
  *V += Delta;
  FTurnEvent E; E.Turn = Turn; E.Verb = "AreaBump"; E.Ctx.Add("province", Province); E.Ctx.Add("dim", Dim); E.Ctx.Add("delta", FString::SanitizeFloat(Delta));
  Events.Add(E);
}

void UOracleStrategyAdapter::DslLoad(const FString& Name, const FString& Rule){
  Rules.Add(Name, Rule);
  FTurnEvent E; E.Turn = Turn; E.Verb = "DSLLoaded"; E.Ctx.Add("name", Name); E.Ctx.Add("size", FString::FromInt(Rule.Len())); Events.Add(E);
}

bool UOracleStrategyAdapter::DslExec(const FString& Name, const FString& Province, const FString& Outcome, TArray<FString>& AppliedDims, TArray<float>& AppliedDeltas){
  AppliedDims.Empty(); AppliedDeltas.Empty();
  const FString* Txt = Rules.Find(Name);
  if(!Txt) return false;
  if(!(Txt->Contains("OUTCOMES") && Txt->Contains("area."))) return false;

  TArray<FString> Lines; Txt->ParseIntoArrayLines(Lines, true);
  bool bPick = false;
  FRegexPattern Pat(TEXT("area\\.(\\w+)\\s*([+\\-]=)\\s*([\\-0-9\\.]+)"));

  for (const FString& L : Lines){
    FString T = L; T.TrimStartAndEndInline();
    FRegexPattern OutPat(FString::Printf(TEXT("^%s\\s*:"), *Outcome));
    if (FRegexMatcher(OutPat, T).FindNext()){ bPick = true; continue; }
    if (bPick && FRegexMatcher(FRegexPattern(TEXT("^\\w+\\s*:")), T).FindNext()) break;

    if (bPick){
      FRegexMatcher M(Pat, T);
      if (M.FindNext()){
        FString Dim = M.GetCaptureGroup(1);
        FString Op  = M.GetCaptureGroup(2);
        float Num   = FCString::Atof(*M.GetCaptureGroup(3));
        float Delta = (Op == "+=") ? Num : -Num;
        AreaBump(Province, Dim, Delta);
        AppliedDims.Add(Dim); AppliedDeltas.Add(Delta);
      }
    }
  }
  FTurnEvent Ev; Ev.Turn = Turn; Ev.Verb = "EncounterCommitted"; Ev.Ctx.Add("province", Province); Ev.Ctx.Add("rule", Name); Ev.Ctx.Add("outcome", Outcome);
  Events.Add(Ev);
  return true;
}

FString UOracleStrategyAdapter::AutosaveJson() const{
  FStrategySave Save; Save.Turn = Turn; Save.Provinces = Provinces; Save.Knobs = Knobs; Save.Events = Events;
  FString OutJson; FJsonObjectConverter::UStructToJsonObjectString(Save, OutJson);
  return OutJson;
}

void UOracleStrategyAdapter::LoadJson(const FString& Json){
  FStrategySave Save;
  if (FJsonObjectConverter::JsonObjectStringToUStruct(Json, &Save, 0, 0)){
    Turn = Save.Turn; Provinces = Save.Provinces; Knobs = Save.Knobs; Events = Save.Events;
    SnapshotsByTurn.Add(Turn, Json);
  }
}

void UOracleStrategyAdapter::UndoToTurn(int32 TargetTurn){
  if (const FString* Json = SnapshotsByTurn.Find(TargetTurn)){
    LoadJson(*Json);
  }
}
