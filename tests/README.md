Test status for tests adapted from https://github.com/mattjgalloway/cgtcalc/tree/main/Tests/CGTCalcCoreTests/Examples/Inputs

| Name | Status | Details |
|------|---------|---------|
| AssetEventsNotFullSale | ❌ ⚠️ | See https://github.com/mattjgalloway/cgtcalc/issues/15. Handles this case in straightforward way, different from cgtcalc |
| AssetEventsNotFullSale2 | ❌ ⚠️ | See https://github.com/mattjgalloway/cgtcalc/issues/15. Handles this case in straightforward way, different from cgtcalc |
| Blank | ✅ |  |
| BuySellAllBuyAgainCapitalReturn | ✅ |  |
| CarryLoss | ✅ |  |
| HMRCExample1 | ✅ |  |
| MultipleMatches | ✅ |  |
| SameDayMerge | ✅ ⚠️ | Does not fully merge same-day events |
| SameDayMergeInterleaved | ✅ ⚠️ | Does not fully merge same-day events |
| Simple | ✅ |  |
| WithAssetEvents | ✅ |  |
| WithAssetEventsBB | ✅ |  |
| WithAssetEventsMultipleYears | ✅ |  |
| WithAssetEventsSameDay | ✅ |  |
| WithSplitBB | ❌ | Split for Bed&Breakfast case not handled yet |
| WithSplitS104 | ❌ | Split handling not guaranteed to be fully implemented yet |
| WithUnsplitBB | ❌ | Split handling not guaranteed to be fully implemented yet |
| WithUnsplitS104 | ❌ | Split handling not guaranteed to be fully implemented yet |