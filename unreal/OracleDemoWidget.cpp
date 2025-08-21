
#include "OracleDemoWidget.h"
#include "Components/Button.h"
#include "Components/TextBlock.h"

void UOracleDemoWidget::NativeConstruct(){
    Super::NativeConstruct();
    if (!Adapter){
        Adapter = NewObject<UOracleRPGAdapter>(this);
        Adapter->InitDefaults();
        Adapter->DslLoad(TEXT("OUTCOMES:\n  calm:\n    area.security += 4\n  riot:\n    area.security -= 6"));
    }
    if (BtnUp)   BtnUp->OnClicked.AddDynamic(this, &UOracleDemoWidget::OnUp);
    if (BtnDown) BtnDown->OnClicked.AddDynamic(this, &UOracleDemoWidget::OnDown);
    if (BtnCalm) BtnCalm->OnClicked.AddDynamic(this, &UOracleDemoWidget::OnCalm);
    if (BtnRiot) BtnRiot->OnClicked.AddDynamic(this, &UOracleDemoWidget::OnRiot);
    RefreshLabel();
}

void UOracleDemoWidget::OnUp(){
    if (Adapter){ Adapter->AreaBump(TEXT("Market"), TEXT("security"), FMath::Abs(Delta)); RefreshLabel(); }
}
void UOracleDemoWidget::OnDown(){
    if (Adapter){ Adapter->AreaBump(TEXT("Market"), TEXT("security"), -FMath::Abs(Delta)); RefreshLabel(); }
}
void UOracleDemoWidget::OnCalm(){
    if (Adapter){
        TArray<FString> Dims; TArray<float> Deltas;
        Adapter->DslExec(TEXT("Market"), TEXT("calm"), Dims, Deltas);
        RefreshLabel();
    }
}
void UOracleDemoWidget::OnRiot(){
    if (Adapter){
        TArray<FString> Dims; TArray<float> Deltas;
        Adapter->DslExec(TEXT("Market"), TEXT("riot"), Dims, Deltas);
        RefreshLabel();
    }
}

void UOracleDemoWidget::RefreshLabel(){
    if (!TxtSecurity || !Adapter) return;
    float Val = 0.f;
    if (FAreaStats* A = Adapter->Areas.Find(TEXT("Market"))){
        if (float* V = A->Metrics.Find(TEXT("security"))) Val = *V;
    }
    TxtSecurity->SetText(FText::FromString(FString::Printf(TEXT("Market.security = %.1f"), Val)));
}
