
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "OracleRPGAdapter.generated.h"

USTRUCT(BlueprintType)
struct FAreaStats {
  GENERATED_BODY()
  UPROPERTY(BlueprintReadWrite) TMap<FString, float> Metrics;
};

USTRUCT(BlueprintType)
struct FNPC {
  GENERATED_BODY()
  UPROPERTY(BlueprintReadWrite) FString Name;
  UPROPERTY(BlueprintReadWrite) TMap<FString, float> Beliefs;
};

USTRUCT(BlueprintType)
struct FRPGEvent {
  GENERATED_BODY()
  UPROPERTY(BlueprintReadWrite) float T = 0.f;
  UPROPERTY(BlueprintReadWrite) FString Verb;
  UPROPERTY(BlueprintReadWrite) TMap<FString, FString> Ctx;
};

USTRUCT(BlueprintType)
struct FRPGSavegame {
  GENERATED_BODY()
  UPROPERTY(BlueprintReadWrite) TMap<FString, FAreaStats> Areas;
  UPROPERTY(BlueprintReadWrite) TMap<FString, FNPC> NPCs;
  UPROPERTY(BlueprintReadWrite) TMap<FString, float> Knobs;
  UPROPERTY(BlueprintReadWrite) TArray<FRPGEvent> Timeline;
};

UCLASS(BlueprintType)
class UOracleRPGAdapter : public UObject {
  GENERATED_BODY()
public:
  UPROPERTY(BlueprintReadWrite) TMap<FString, FAreaStats> Areas;
  UPROPERTY(BlueprintReadWrite) TMap<FString, FNPC> NPCs;
  UPROPERTY(BlueprintReadWrite) TMap<FString, float> Knobs;

  UFUNCTION(BlueprintCallable) void InitDefaults();
  UFUNCTION(BlueprintCallable) void AreaBump(const FString& Area, const FString& Dim, float Delta);
  UFUNCTION(BlueprintCallable) void Rumor(const FString& Hypothesis, const FString& Source, int32 Polarity, float Reliability);
  UFUNCTION(BlueprintCallable) void DslLoad(const FString& Rule);
  UFUNCTION(BlueprintCallable) bool DslExec(const FString& Area, const FString& Outcome, TArray<FString>& AppliedDims, TArray<float>& AppliedDeltas);

  UFUNCTION(BlueprintCallable) FString MakeSavegameJson() const;
  UFUNCTION(BlueprintCallable) void LoadSavegameJson(const FString& Json);

private:
  FString Dsl;
};
