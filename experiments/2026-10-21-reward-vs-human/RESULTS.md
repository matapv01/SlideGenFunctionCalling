# DAPO's reward gain vs what the annotators saw (round 2)

Training reward = round-4 weights {"keypoint": 1.5, "semantic": 0.4, "numeric_fact": 0.7, "dom": 2.1, "aesthetic": 1.5, "image_loaded": 0.25, "lexical": 0.0} x language; invalid = -2.

## DAPO vs base

Test set (337 slides): mean training reward DAPO 4.889, base 4.735, gap +0.154; DAPO higher on 111, lower on 109, within 0.01 on 117.

### Where the mean gap comes from (per-slide mean contribution, sums to the gap)

| Component | Contribution | Share of gap |
|---|---|---|
| validity | +0.170 | +110% |
| dom | +0.053 | +34% |
| keypoint | -0.025 | -16% |
| aesthetic | -0.021 | -14% |
| numeric_fact | -0.014 | -9% |
| language | -0.005 | -3% |
| semantic | -0.003 | -2% |
| image_loaded | +0.000 | +0% |

### Reward gap vs human verdict (291 rated pairs)

| Reward gap DAPO - rival | Pairs | Human overall win rate | Human overall: DAPO wins / tie / loses | Sum of reward gap |
|---|---|---|---|---|
| < -0.3 | 59 | 0.449 | 13 / 23 / 23 | -42.47 |
| -0.3 .. -0.05 | 24 | 0.479 | 2 / 18 / 4 | -3.55 |
| -0.05 .. 0.05 | 137 | 0.502 | 5 / 127 / 5 | +0.11 |
| 0.05 .. 0.3 | 29 | 0.526 | 3 / 24 / 2 | +4.21 |
| >= 0.3 | 42 | 0.585 | 13 / 22 / 7 | +38.54 |

Sum of reward gap on rated pairs -3.15: on pairs where humans agree with the reward's direction -0.95, where humans call it a tie +3.48, where humans disagree -5.68.

### Per component: when it favours one side by > 0.05, does the matching human criterion follow?

| Component (criterion) | Favours DAPO: pairs, human win rate on criterion, ties | Favours rival: pairs, win rate, ties |
|---|---|---|
| validity (overall) | 0 | 0 |
| dom (layout) | 23, 0.587, ties 18 | 9, 0.444, ties 8 |
| aesthetic (aesthetic) | 57, 0.544, ties 51 | 67, 0.544, ties 56 |
| keypoint (coverage) | 19, 0.539, ties 15 | 34, 0.377, ties 18 |
| semantic (coverage) | 7, 0.607, ties 5 | 6, 0.458, ties 3 |
| numeric_fact (faithful) | 5, 0.500, ties 5 | 17, 0.500, ties 14 |
| language (language) | 1, 0.500, ties 1 | 1, 0.000, ties 0 |
| image_loaded (layout) | 0 | 0 |

Visible defect only on the base slide: 8 pairs, human layout win rate 0.719, overall 0.844; only on DAPO: 1 pairs, layout 0.000, overall 0.500.

## DAPO vs best4

Test set (337 slides): mean training reward DAPO 4.889, best4 5.308, gap -0.419; DAPO higher on 73, lower on 222, within 0.01 on 42.

### Where the mean gap comes from (per-slide mean contribution, sums to the gap)

| Component | Contribution | Share of gap |
|---|---|---|
| aesthetic | -0.136 | +33% |
| validity | -0.115 | +27% |
| dom | -0.069 | +16% |
| numeric_fact | -0.038 | +9% |
| keypoint | -0.034 | +8% |
| language | -0.020 | +5% |
| semantic | -0.008 | +2% |
| image_loaded | +0.000 | -0% |

### Reward gap vs human verdict (132 rated pairs)

| Reward gap DAPO - rival | Pairs | Human overall win rate | Human overall: DAPO wins / tie / loses | Sum of reward gap |
|---|---|---|---|---|
| < -0.3 | 53 | 0.465 | 11 / 26 / 16 | -52.00 |
| -0.3 .. -0.05 | 26 | 0.481 | 2 / 19 / 5 | -4.03 |
| -0.05 .. 0.05 | 31 | 0.540 | 5 / 24 / 2 | -0.18 |
| 0.05 .. 0.3 | 9 | 0.528 | 3 / 4 / 2 | +1.55 |
| >= 0.3 | 13 | 0.410 | 3 / 3 / 7 | +11.72 |

Sum of reward gap on rated pairs -42.94: on pairs where humans agree with the reward's direction -14.33, where humans call it a tie -24.04, where humans disagree -4.57.

### Per component: when it favours one side by > 0.05, does the matching human criterion follow?

| Component (criterion) | Favours DAPO: pairs, human win rate on criterion, ties | Favours rival: pairs, win rate, ties |
|---|---|---|
| validity (overall) | 0 | 0 |
| dom (layout) | 5, 0.700, ties 3 | 18, 0.472, ties 14 |
| aesthetic (aesthetic) | 21, 0.488, ties 19 | 54, 0.523, ties 49 |
| keypoint (coverage) | 10, 0.475, ties 3 | 17, 0.446, ties 11 |
| semantic (coverage) | 4, 0.375, ties 2 | 7, 0.500, ties 7 |
| numeric_fact (faithful) | 4, 0.500, ties 4 | 25, 0.520, ties 24 |
| language (language) | 0 | 2, 0.250, ties 1 |
| image_loaded (layout) | 0 | 0 |

## DAPO vs gemini

Test set (337 slides): mean training reward DAPO 4.889, gemini 4.452, gap +0.437; DAPO higher on 192, lower on 127, within 0.01 on 18.

### Where the mean gap comes from (per-slide mean contribution, sums to the gap)

| Component | Contribution | Share of gap |
|---|---|---|
| dom | +0.187 | +43% |
| language | +0.170 | +39% |
| validity | +0.061 | +14% |
| aesthetic | +0.033 | +8% |
| numeric_fact | -0.012 | -3% |
| keypoint | -0.005 | -1% |
| semantic | +0.003 | +1% |
| image_loaded | +0.000 | +0% |

### Reward gap vs human verdict (153 rated pairs)

| Reward gap DAPO - rival | Pairs | Human overall win rate | Human overall: DAPO wins / tie / loses | Sum of reward gap |
|---|---|---|---|---|
| < -0.3 | 41 | 0.421 | 8 / 16 / 17 | -42.25 |
| -0.3 .. -0.05 | 11 | 0.386 | 1 / 5 / 5 | -1.92 |
| -0.05 .. 0.05 | 24 | 0.406 | 1 / 17 / 6 | +0.01 |
| 0.05 .. 0.3 | 12 | 0.583 | 4 / 6 / 2 | +1.44 |
| >= 0.3 | 65 | 0.600 | 25 / 29 / 11 | +101.83 |

Sum of reward gap on rated pairs +59.11: on pairs where humans agree with the reward's direction +50.65, where humans call it a tie +3.95, where humans disagree +4.51.

### Per component: when it favours one side by > 0.05, does the matching human criterion follow?

| Component (criterion) | Favours DAPO: pairs, human win rate on criterion, ties | Favours rival: pairs, win rate, ties |
|---|---|---|
| validity (overall) | 0 | 0 |
| dom (layout) | 34, 0.566, ties 27 | 5, 0.300, ties 3 |
| aesthetic (aesthetic) | 47, 0.589, ties 32 | 45, 0.494, ties 31 |
| keypoint (coverage) | 26, 0.635, ties 15 | 29, 0.397, ties 19 |
| semantic (coverage) | 13, 0.808, ties 5 | 14, 0.470, ties 7 |
| numeric_fact (faithful) | 17, 0.618, ties 12 | 20, 0.475, ties 19 |
| language (language) | 6, 0.875, ties 1 | 2, 0.375, ties 1 |
| image_loaded (layout) | 0 | 0 |

