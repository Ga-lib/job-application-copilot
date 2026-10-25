# Evaluation results

Model: `openai/gpt-oss-20b`. Web search is disabled during evals so runs are repeatable.

| Case | Score | Expected | In band | Letter routing | Unsupported numbers | Judge (rel/honest/tone) | Seconds |
|---|---|---|---|---|---|---|---|
| strong_ml_vs_ml_job | 90 | 70-100 | pass | pass | none | 5/5/5 | 7.8 |
| strong_ml_vs_analyst_job | 50 | 35-85 | pass | pass | none | 3/5/4 | 55.3 |
| webdev_vs_fullstack_job | 90 | 70-100 | pass | pass | none | 5/5/5 | 39.9 |
| webdev_vs_ml_job | 30 | 0-40 | pass | - | none | - | 28.8 |
| student_vs_ml_job | 25 | 0-35 | pass | pass | none | - | 50.9 |
| student_vs_analyst_job | 30 | 15-65 | pass | - | none | - | 23.2 |
| strong_ml_vs_fullstack_job | 35 | 15-60 | pass | - | none | 2/5/4 | 52.2 |

## Summary
- Cases run: 7 (errors: 0)
- Score in expected band: 1.0
- Cover-letter routing correct: 1.0
- Letters with unsupported numbers: 0
- Judge averages (1-5): relevance 3.75, honesty 5.0, tone 4.5
- Average seconds per case: 36.87
