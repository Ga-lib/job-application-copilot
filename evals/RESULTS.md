# Evaluation results

Model: `openai/gpt-oss-20b`. Web search is disabled during evals so runs are repeatable.

| Case | Score | Expected | In band | Letter routing | Unsupported numbers | Judge (rel/honest/tone) | Seconds |
|---|---|---|---|---|---|---|---|
| strong_ml_vs_ml_job | 90 | 70-100 | pass | pass | none | 5/5/5 | 14.3 |
| strong_ml_vs_analyst_job | 50 | 35-85 | pass | pass | none | 3/3/4 | 44.9 |
| webdev_vs_fullstack_job | 85 | 70-100 | pass | pass | none | 5/5/4 | 46.3 |
| webdev_vs_ml_job | 25 | 0-40 | pass | - | none | - | 17.6 |
| student_vs_ml_job | 20 | 0-35 | pass | pass | none | - | 32.8 |
| student_vs_analyst_job | 35 | 15-65 | pass | - | none | 3/5/4 | 53.7 |
| strong_ml_vs_fullstack_job | 44 | 15-60 | pass | pass | none | - | 25.0 |

## Summary
- Cases run: 7 (errors: 0)
- Score in expected band: 1.0
- Cover-letter routing correct: 1.0
- Letters with unsupported numbers: 0
- Judge averages (1-5): relevance 4.0, honesty 4.5, tone 4.25
- Average seconds per case: 33.51
