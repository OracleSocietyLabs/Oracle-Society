
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "OracleStrategyAdapter.generated.h"

USTRUCT(BlueprintType)
struct FProvinceStats {
  GENERATED_BODY()
  UPROPERTY(BlueprintReadWrite) TMap<FString, float> Metrics;
};

USTRUCT(BlueprintType)
struct FTurnEvent {
  GENERATED_BODY()
  UPROPERTY(BlueprintReadWrite) int32 Turn = 0;
  UPROPERTY(BlueprintReadWrite) FString Verb;
  UPROPERTY(BlueprintReadWrite) TMap<FString, FString> Ctx;
};

USTRUCT(BlueprintType)
struct FStrategySave {
  GENERATED_BODY()
  UPROPERTY(BlueprintReadWrite) int32 Turn = 0;
  UPROPERTY(BlueprintReadWrite) TMap<FString, FProvinceStats> Provinces;
  UPROPERTY(BlueprintReadWrite) TMap<FString, float> Knobs;
  UPROPERTY(BlueprintReadWrite) TArray<FTurnEvent> Events;
};

UCLASS(BlueprintType)
class UOracleStrategyAdapter : public UObject {
  GENERATED_BODY()
public:
  UPROPERTY(BlueprintReadOnly) int32 Turn = 0;
  UPROPERTY(BlueprintReadWrite) TMap<FString, FProvinceStats> Provinces;
  UPROPERTY(BlueprintReadWrite) TMap<FString, float> Knobs;
  UPROPERTY() TMap<FString, FString> Rules;
  UPROPERTY() TArray<FTurnEvent> Events;

  UFUNCTION(BlueprintCallable) void InitDefaults();
  UFUNCTION(BlueprintCallable) void NextTurn();
  UFUNCTION(BlueprintCallable) void AreaBump(const FString& Province, const FString& Dim, float Delta);
  UFUNCTION(BlueprintCallable) void DslLoad(const FString& Name, const FString& Rule);
  UFUNCTION(BlueprintCallable) bool DslExec(const FString& Name, const FString& Province, const FString& Outcome, TArray<FString>& AppliedDims, TArray<float>& AppliedDeltas);
  UFUNCTION(BlueprintCallable) FString AutosaveJson() const;
  UFUNCTION(BlueprintCallable) void LoadJson(const FString& Json);
  UFUNCTION(BlueprintCallable) void UndoToTurn(int32 TargetTurn);

private:
  TMap<int32, FString> SnapshotsByTurn; // JSON per turn
};
