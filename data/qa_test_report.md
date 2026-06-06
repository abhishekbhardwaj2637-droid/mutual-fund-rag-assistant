# Mutual Fund FAQ Assistant - QA Test Report

- **Execution Date**: 2026-06-01 13:52:58
- **Total Test Cases**: 10
- **Passed Cases**: 10 / 10
- **Pass Rate**: 100.0%

## Detailed Test Summary

| ID | User Query | Expected Cat | Actual Cat | Scheme Match | Passed | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `What is the exit load of HDFC Mid-Cap Opportunities Fund?` | FACTUAL | FACTUAL | hdfc-mid-cap-fund-direct-growth | ✅ | SUCCESS |
| 2 | `What is the expense ratio of HDFC Small Cap Fund?` | FACTUAL | FACTUAL | hdfc-small-cap-fund-direct-growth | ✅ | SUCCESS |
| 3 | `Who is the fund manager of HDFC Defence Fund?` | FACTUAL | FACTUAL | hdfc-defence-fund-direct-growth | ✅ | SUCCESS |
| 4 | `What is the benchmark index of HDFC Silver ETF FoF?` | FACTUAL | FACTUAL | hdfc-silver-etf-fof-direct-growth | ✅ | SUCCESS |
| 5 | `What is the minimum SIP and lump sum investment for HDFC Gold ETF Fund of Fund?` | FACTUAL | FACTUAL | hdfc-gold-etf-fund-of-fund-direct-plan-growth | ✅ | SUCCESS |
| 6 | `Should I invest in HDFC Small Cap Fund for my retirement?` | ADVISORY | ADVISORY | N/A (Global) | ✅ | REFUSED |
| 7 | `Which is a better investment choice, HDFC Defence or HDFC Mid-Cap Fund?` | ADVISORY | ADVISORY | N/A (Global) | ✅ | REFUSED |
| 8 | `Can you predict if HDFC Gold ETF will double my money in the next 3 years?` | ADVISORY | ADVISORY | N/A (Global) | ✅ | REFUSED |
| 9 | `What is the exit load of Nippon India Small Cap Fund?` | FACTUAL | FACTUAL | N/A (Global) | ✅ | SUCCESS |
| 10 | `Explain what inflation is and how it affects interest rates.` | FACTUAL | FACTUAL | N/A (Global) | ✅ | SUCCESS |

## Metric Observations
- **Compliance & Guardrails**: 100% of advisory questions were successfully detected and rejected with standard disclaimer disclaimers and AMFI/SEBI redirect buttons.
- **Metadata Ingestion Isolation**: The retriever correctly routed queries to the targeted HDFC scheme vector segment using metadata-level filters, preventing data cross-contamination.
- **Fallback Performance**: Fallback formatting successfully rendered the raw database text blocks for factual queries when API keys were absent.
