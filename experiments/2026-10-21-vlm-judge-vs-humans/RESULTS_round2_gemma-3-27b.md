# Automatic judges vs human verdicts, round 2

Pairs with human ratings and a parsed VLM verdict: 576 (VLM file 634, human 576).
VLM: gemma-3-27b, each pair judged in both orders; vote = mean of the two.

## VLM self-consistency (same answer when A/B are swapped)

| Criterion | Same verdict both orders | Mean forward vote (+ = prefers first image) |
|---|---|---|
| faithful | 0.47 | -0.40 |
| coverage | 0.46 | -0.41 |
| language | 0.95 | +0.00 |
| layout | 0.47 | +0.21 |
| aesthetic | 0.46 | -0.10 |
| overall | 0.46 | -0.06 |

## Agreement with the human pair verdict (same side, on pairs both decided)

| Criterion | VLM (both orders) | VLM forward only | Metric Δ (faithful:numeric_fact, coverage:keypoint, language:language, layout:dom, aesthetic:aesthetic, overall:reward) | Human vs other human |
|---|---|---|---|---|
| faithful | 1.00 (12/12; decides 55%) | 0.73 (16/22; decides 100%) | 0.82 (9/11; decides 50%) | 1.00 (3/3; decides 43%) |
| coverage | 0.82 (40/49; decides 34%) | 0.59 (82/140; decides 96%) | 0.79 (45/57; decides 39%) | 0.92 (12/13; decides 41%) |
| language | 0.91 (10/11; decides 55%) | 1.00 (8/8; decides 40%) | 1.00 (8/8; decides 40%) | 1.00 (3/3; decides 60%) |
| layout | 0.70 (21/30; decides 70%) | 0.63 (27/43; decides 100%) | 0.90 (19/21; decides 49%) | 1.00 (7/7; decides 50%) |
| aesthetic | 0.55 (24/44; decides 52%) | 0.56 (47/84; decides 100%) | 0.53 (43/81; decides 96%) | 0.82 (9/11; decides 44%) |
| overall | 0.60 (58/96; decides 45%) | 0.57 (121/213; decides 100%) | 0.64 (134/211; decides 99%) | 0.73 (40/55; decides 82%) |

## VLM agreement by comparison

| Comparison | faithful | coverage | language | layout | aesthetic | overall |
|---|---|---|---|---|---|---|
| dapo_vs_base (291) | 1.00 (3/3; decides 43%) | 0.85 (17/20; decides 35%) | 0.50 (1/2; decides 50%) | 0.50 (3/6; decides 50%) | 0.55 (6/11; decides 44%) | 0.48 (14/29; decides 38%) |
| dapo_vs_best4 (132) | n/a | 0.50 (3/6; decides 18%) | 1.00 (1/1; decides 25%) | 0.75 (3/4; decides 44%) | 0.56 (5/9; decides 69%) | 0.60 (15/25; decides 45%) |
| dapo_vs_gemini (153) | 1.00 (9/9; decides 82%) | 0.87 (20/23; decides 42%) | 1.00 (8/8; decides 67%) | 0.75 (15/20; decides 91%) | 0.54 (13/24; decides 52%) | 0.69 (29/42; decides 52%) |

## DAPO win rate: humans vs VLM (deck bootstrap 95% CI)

| Comparison | Criterion | Humans (rated pairs) | VLM (same pairs) | VLM (all judged pairs) |
|---|---|---|---|---|
| dapo_vs_base | overall | 0.504 [0.481, 0.529] | 0.517 [0.491, 0.543] | 0.517 [0.493, 0.541] |
| dapo_vs_base | aesthetic | 0.525 [0.513, 0.536] | 0.515 [0.490, 0.543] | 0.518 [0.493, 0.543] |
| dapo_vs_base | coverage | 0.480 [0.463, 0.498] | 0.483 [0.465, 0.501] | 0.481 [0.465, 0.497] |
| dapo_vs_base | layout | 0.507 [0.498, 0.515] | 0.498 [0.473, 0.525] | 0.499 [0.474, 0.524] |
| dapo_vs_base | faithful | 0.497 [0.490, 0.503] | 0.489 [0.471, 0.508] | 0.487 [0.470, 0.503] |
| dapo_vs_best4 | overall | 0.485 [0.437, 0.536] | 0.562 [0.507, 0.625] | 0.551 [0.500, 0.607] |
| dapo_vs_best4 | aesthetic | 0.519 [0.496, 0.544] | 0.585 [0.524, 0.649] | 0.566 [0.509, 0.626] |
| dapo_vs_best4 | coverage | 0.468 [0.442, 0.497] | 0.464 [0.434, 0.495] | 0.464 [0.433, 0.498] |
| dapo_vs_best4 | layout | 0.500 [0.480, 0.525] | 0.542 [0.494, 0.596] | 0.532 [0.490, 0.580] |
| dapo_vs_best4 | faithful | 0.508 [0.498, 0.520] | 0.462 [0.431, 0.493] | 0.463 [0.430, 0.495] |
| dapo_vs_gemini | overall | 0.505 [0.456, 0.551] | 0.541 [0.480, 0.599] | 0.537 [0.490, 0.589] |
| dapo_vs_gemini | aesthetic | 0.520 [0.480, 0.555] | 0.523 [0.469, 0.572] | 0.524 [0.477, 0.574] |
| dapo_vs_gemini | coverage | 0.492 [0.457, 0.527] | 0.520 [0.479, 0.562] | 0.516 [0.478, 0.559] |
| dapo_vs_gemini | layout | 0.529 [0.503, 0.551] | 0.526 [0.465, 0.585] | 0.522 [0.470, 0.573] |
| dapo_vs_gemini | faithful | 0.521 [0.503, 0.541] | 0.525 [0.484, 0.566] | 0.521 [0.482, 0.562] |

## Length and brightness preferences (pairs where the judge takes a side)

Longer = A has > 1.1x or < 0.9x B's visible words; brighter = |mean luminance A - B| > 0.03.

| Criterion | Humans pick longer | VLM picks longer | Humans pick brighter | VLM picks brighter |
|---|---|---|---|---|
| faithful | 0.78 (14/18) | 0.76 (74/97) | 0.20 (1/5) | 0.51 (22/43) |
| coverage | 0.78 (96/123) | 0.80 (76/95) | 0.43 (12/28) | 0.53 (23/43) |
| language | 0.75 (12/16) | 0.65 (13/20) | 0.38 (3/8) | 0.40 (2/5) |
| layout | 0.42 (15/36) | 0.52 (70/135) | 0.64 (9/14) | 0.46 (28/61) |
| aesthetic | 0.46 (27/59) | 0.38 (51/135) | 0.84 (36/43) | 0.38 (17/45) |
| overall | 0.65 (108/166) | 0.47 (62/131) | 0.66 (40/61) | 0.43 (21/49) |

