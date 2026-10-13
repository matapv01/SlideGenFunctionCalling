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

## More single-factor checks on the proxy Qwen server (291 dev slides, raw Qwen-native output, one sample)
| arm | reward | valid | usable | visible-defect slides | lexical | numeric_fact |
|---|---|---|---|---|---|---|
| prompt of this run, T=1.0 | 3.441 | 0.921 | 0.852 | 20 | 0.648 | 0.823 |
| + JSON-quote reminder line | – | 0.921 | – | – | – | – |
| joint capacity + max-items hints (v2), T=1.0 | 3.399 | 0.918 | 0.880 | 11 | 0.623 | 0.805 |
| prompt of this run, T=0.6 | 3.618 | 0.945 | 0.876 | 20 | 0.664 | 0.831 |
| prompt of this run, T=0.3 | 3.661 | 0.948 | 0.876 | 21 | 0.673 | 0.842 |

- JSON-quote reminder: no effect on validity (negative result, not adopted).
- Hints v2 halve visible defects but lose content; composite reward is not higher (negative result, not adopted;
  file kept as rl/data/tool_text_capacity_v2_joint.json).
- Lower decoding temperature raises reward by 0.22 with no retraining. Decoding temperature is an inference
  setting: choose it per system on dev data, then apply unchanged to the fresh test set.

## Numbers (this run, eval split, 42 slides x 4 samples) — continued
| step | reward | valid | dom | overflow | fabricated | language |
|---|---|---|---|---|---|---|
| 25 | 3.362 | 0.899 | 0.872 | 0.338 | 0.034 | 1.000 |
| 50 | 3.421 | 0.911 | 0.889 | 0.310 | 0.037 | 1.000 |
| 75 | 3.517 | 0.923 | 0.892 | 0.276 | 0.019 | 1.000 |
| 100 | 3.617 | 0.946 | 0.876 | 0.281 | 0.036 | 1.000 |
| 125 | 3.569 | 0.934 | 0.908 | 0.256 | 0.043 | 1.000 |

## Ablations still owed for attribution
- same config without capacity hints (run 2c reached eval 3.08 at step 50, stopped at 75)
- same config with round-1 layout penalties
- 3 seeds of the final config

## Decision
- running
