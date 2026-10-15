# Results — DAPO round 4 (key-point reward, fixed font sizes), three seeds

Config: [`config.yaml`](config.yaml) · final model `qwen3_5_35b_dapo_r4_20261014/checkpoint-175` (HF `round4/`)

## Checklist before trusting these numbers
- [x] Baseline on the same prompts and slides (base_r4_t03 on dev, base_final_* on test)
- [x] >= 3 seeds (42, 7, 2026) on the dev set
- [x] Held-out, topic-disjoint test set run once for the final model (testset_v2, 337 slides)
- [x] Images inspected at every training milestone and for 30+ dev/test slides vs the base model
- [ ] Human judgement on this round — not yet (predicted preference only)
- [ ] Gemini 3.5 Flash on the test set — waiting for an API key

## Dev set (291 slides, T=0.3)
| system | valid | usable | visible | keypoint | P(preferred over base), predicted |
|---|---|---|---|---|---|
| base | 97.6% | 90.0% | 7.6% | 0.817 | n/a |
| round 4, seed 42 (final) | 99.0% | 95.2% | 3.8% | 0.791 | 0.509 [0.493, 0.524] |
| round 4, seed 7 | 97.6% | 92.4% | 5.2% | 0.800 | 0.498 [0.485, 0.510] |
| round 4, seed 2026 | 99.3% | 94.5% | 4.8% | 0.798 | 0.513 [0.500, 0.529] |
| round 4 mean ± std | 98.6 ± 0.9 | 94.0 ± 1.4 | 4.6 ± 0.7 | 0.796 ± 0.005 | 0.507 ± 0.008 |

## Held-out test set (337 slides)
| system | reward | valid | usable | visible | keypoint |
|---|---|---|---|---|---|
| base, T=0.3 | 3.597 | 95.0% | 90.2% | 4.7% | 0.811 |
| round 4 final, T=0.3 | 3.715 | 97.6% | 94.7% | 3.0% | 0.788 |
| base, best-of-4 at T=1.0 | 4.059 | 99.1% | 97.0% | 2.1% | 0.815 |
| round 4 final, best-of-4 at T=1.0 | 4.069 | 99.4% | 97.3% | 2.1% | 0.817 |

## Conclusions
- RL reliably lowers visible defects at one sample (dev 7.6% -> 4.6% ± 0.7 over seeds; test 4.7% -> 3.0%) at a key-point cost of about 0.02.
- With reward-based selection of 4 samples, base and round 4 are equal: RL buys inference cost, not a higher ceiling.
- Seeds peak at very different steps (50, 175, 175); early stopping on eval reward is required.
- Too-many-items tool calls (7 of 8 invalid test slides) occur at the same rate in the base model; not caused by RL.

## Gemini 3.5 Flash on the dev set (old round-1 outputs, rescored; T=1.0, round-1 prompt without capacity hints)
| system | valid | usable | visible | cutoff | keypoint |
|---|---|---|---|---|---|
| Gemini, 1 sample | 96.2% | 73.2% | 23.0% | 15.8% | 0.858 |
| Gemini, best-of-4 | 98.6% | 82.8% | 15.8% | 12.4% | 0.879 |
Predicted P(round 4 final preferred over Gemini) = 0.573 [0.548, 0.598]; not a fair comparison (prompt and temperature differ).

## Aesthetic judges vs round-1 human raters (generated slides)
| judge | aesthetic (192 pairs) | overall (342 pairs) |
|---|---|---|
| ViT | 60.4% | 57.0% |
| composite reward | 69.8% | 70.2% |
| Qwen3.5-35B-A3B VLM zero-shot | 71.6% | 65.2% |
On the 193 synthetic held-out pairs: CLIP 47.9%, VLM 97.4%, ViT 97.9%.
