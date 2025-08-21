
#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "OracleRPGAdapter.h"
#include "Components/Button.h"
#include "Components/TextBlock.h"
#include "OracleDemoWidget.generated.h"

UCLASS()
class UOracleDemoWidget : public UUserWidget
{
    GENERATED_BODY()
public:
    UPROPERTY(meta=(BindWidget)) UButton* BtnUp;
    UPROPERTY(meta=(BindWidget)) UButton* BtnDown;
    UPROPERTY(meta=(BindWidget)) UButton* BtnCalm;
    UPROPERTY(meta=(BindWidget)) UButton* BtnRiot;
    UPROPERTY(meta=(BindWidget)) UTextBlock* TxtSecurity;

    UPROPERTY(EditAnywhere, BlueprintReadWrite) float Delta = 2.0f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) UOracleRPGAdapter* Adapter;

    virtual void NativeConstruct() override;

    UFUNCTION() void OnUp();
    UFUNCTION() void OnDown();
    UFUNCTION() void OnCalm();
    UFUNCTION() void OnRiot();

    UFUNCTION(BlueprintCallable) void RefreshLabel();
};
