
#include "Misc/AutomationTest.h"
#include "OracleRPGAdapter.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FOracleDSLCalmTest, "Oracle.DSL.CalmAppliesDelta", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOracleDSLCalmTest::RunTest(const FString& Parameters)
{
    UOracleRPGAdapter* Adapter = NewObject<UOracleRPGAdapter>();
    Adapter->InitDefaults();
    Adapter->DslLoad(TEXT("OUTCOMES:\n  calm:\n    area.security += 4"));

    float Before = 0.f;
    if (FAreaStats* A = Adapter->Areas.Find(TEXT("Market"))){
        if (float* V = A->Metrics.Find(TEXT("security"))) Before = *V;
    }

    TArray<FString> Dims; TArray<float> Deltas;
    const bool bMatched = Adapter->DslExec(TEXT("Market"), TEXT("calm"), Dims, Deltas);
    TestTrue("DSL matched", bMatched);

    float After = 0.f;
    if (FAreaStats* A2 = Adapter->Areas.Find(TEXT("Market"))){
        if (float* V2 = A2->Metrics.Find(TEXT("security"))) After = *V2;
    }
    TestEqual("Delta applied", After, Before + 4.0f);
    return true;
}
