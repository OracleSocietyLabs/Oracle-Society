
#include "OracleRPGAdapter.h"
#include "Misc/DateTime.h"
#include "Regex.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonWriter.h"
#include "Serialization/JsonSerializer.h"
#include "Policies/CondensedJsonPrintPolicy.h"
#include "JsonObjectConverter.h"

void UOracleRPGAdapter::InitDefaults(){
  Areas.Empty(); NPCs.Empty(); Knobs.Empty();
  FAreaStats Market; Market.Metrics.Add("security",45); Market.Metrics.Add("prosperity",55);
  Market.Metrics.Add("control",50); Market.Metrics.Add("culture",50); Market.Metrics.Add("ecology",50);
  Areas.Add("Market", Market);
  FAreaStats Harbor; Harbor.Metrics.Add("security",38); Harbor.Metrics.Add("prosperity",48);
  Harbor.Metrics.Add("control",52); Harbor.Metrics.Add("culture",46); Harbor.Metrics.Add("ecology",49);
  Areas.Add("Harbor", Harbor);

  FNPC N1; N1.Name="Aella"; N1.Beliefs.Add("player=arsonist", 0.8f); NPCs.Add("N1", N1);
  FNPC N2; N2.Name="Boros"; N2.Beliefs.Add("player=arsonist", 0.6f); NPCs.Add("N2", N2);

  Knobs.Add("memory_half_life",240); Knobs.Add("prestige_half_life",480); Knobs.Add("area_half_life",720);
}

void UOracleRPGAdapter::AreaBump(const FString& Area, const FString& Dim, float Delta){
  FAreaStats* A = Areas.Find(Area);
  if(!A){ FAreaStats NewA; Areas.Add(Area, NewA); A = Areas.Find(Area); }
  float* V = A->Metrics.Find(Dim);
  if(!V){ A->Metrics.Add(Dim, 50.f); V = A->Metrics.Find(Dim); }
  *V += Delta;
}

void UOracleRPGAdapter::Rumor(const FString& Hypothesis, const FString& Source, int32 Polarity, float Reliability){
  for (auto& It : NPCs){
    float* Val = It.Value.Beliefs.Find(Hypothesis);
    if(!Val){ It.Value.Beliefs.Add(Hypothesis, 0.5f); Val = It.Value.Beliefs.Find(Hypothesis); }
    *Val = FMath::Clamp(*Val + 0.05f * Polarity * Reliability, 0.f, 1.f);
  }
}

void UOracleRPGAdapter::DslLoad(const FString& Rule){ Dsl = Rule; }

bool UOracleRPGAdapter::DslExec(const FString& Area, const FString& Outcome, TArray<FString>& AppliedDims, TArray<float>& AppliedDeltas){
  AppliedDims.Empty(); AppliedDeltas.Empty();
  if(!(Dsl.Contains("OUTCOMES") && Dsl.Contains("area."))) return false;

  TArray<FString> Lines; Dsl.ParseIntoArrayLines(Lines, true);
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
        AreaBump(Area, Dim, Delta);
        AppliedDims.Add(Dim); AppliedDeltas.Add(Delta);
      }
    }
  }
  return true;
}

FString UOracleRPGAdapter::MakeSavegameJson() const{
  FRPGSavegame Save;
  Save.Areas = Areas; Save.NPCs = NPCs; Save.Knobs = Knobs;
  // Timeline left empty in this minimal example; add if you track it in-game.

  FString OutJson;
  FJsonObjectConverter::UStructToJsonObjectString(Save, OutJson);
  return OutJson;
}

void UOracleRPGAdapter::LoadSavegameJson(const FString& Json){
  FRPGSavegame Save;
  if (FJsonObjectConverter::JsonObjectStringToUStruct(Json, &Save, 0, 0)){
    Areas = Save.Areas; NPCs = Save.NPCs; Knobs = Save.Knobs;
  }
}
