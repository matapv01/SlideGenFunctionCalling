# Results — DAPO round 2d

Config: [`config.yaml`](config.yaml) · run dir `qwen3_5_35b_dapo_r2d_20261013`

## Checklist before trusting these numbers
- [x] Baseline reproduced: base model run through our own pipeline (eval@0 = 3.142 on this run's eval split)
- [ ] Leakage audit passed — NOT YET. The 291-slide Wikipedia set and its human ratings were used to
      calibrate layout penalties, choose prompt changes and set thresholds. It is development data now.
      A fresh topic-disjoint test set is required for the final table and the second human study.
- [ ] >= 3 seeds for any comparison claim — one seed so far
- [ ] One thing changed at a time vs the baseline — no: see ablations below

## Single-factor evidence already measured (untrained proxy Qwen server, 291 dev slides, one sample)
| change | metric | without | with |
|---|---|---|---|
| capacity hints | slides with text cut off | 10.0% | 4.8% |
| capacity hints | lexical coverage | 0.577 | 0.580 |
| + language line | wrong-language slides | 27 | 0 |
| + language line | composite reward | 3.06 | 3.35 |
| + anti-fabrication sentence | slides with fabricated numbers | 5.7% | 5.1% (dropped: no effect) |

## Numbers (this run, eval split, 42 slides x 4 samples)
| step | reward | valid | dom | overflow | fabricated | language |
|---|---|---|---|---|---|---|
| 0 (base) | 3.142 | 0.863 | 0.858 | 0.354 | 0.028 | 1.000 |

## Ablations still owed for attribution
- same config without capacity hints (run 2c reached eval 3.08 at step 50, stopped at 75)
- same config with round-1 layout penalties
- 3 seeds of the final config

## Decision
- running
