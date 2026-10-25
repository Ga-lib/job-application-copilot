# Evaluation results

Model: `openai/gpt-oss-20b`. Web search is disabled during evals so runs are repeatable.

| Case | Score | Expected | In band | Letter routing | Unsupported numbers | Judge (rel/honest/tone) | Seconds |
|---|---|---|---|---|---|---|---|
| strong_ml_vs_ml_job | 90 | 70-100 | pass | pass | none | 5/5/5 | 12.2 |
| strong_ml_vs_analyst_job | 50 | 35-85 | pass | pass | none | 4/5/5 | 34.0 |
| webdev_vs_fullstack_job | 92 | 70-100 | pass | pass | none | 5/5/4 | 28.4 |
| webdev_vs_ml_job | 30 | 0-40 | pass | - | none | - | 32.8 |
| student_vs_ml_job | 20 | 0-35 | pass | pass | none | - | 19.4 |
| student_vs_analyst_job | error | 15-65 | - | - | - | - | - |
| strong_ml_vs_fullstack_job | error | 15-60 | - | - | - | - | - |

## Summary
- Cases run: 7 (errors: 2)
- Score in expected band: 1.0
- Cover-letter routing correct: 1.0
- Letters with unsupported numbers: 0
- Judge averages (1-5): relevance 4.67, honesty 5.0, tone 4.67
- Average seconds per case: 25.36
