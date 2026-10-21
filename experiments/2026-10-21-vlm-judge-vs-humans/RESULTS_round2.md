# Automatic judges vs human verdicts, round 2

Pairs with human ratings and a parsed VLM verdict: 576 (VLM file 634, human 576).
VLM: qwen2.5-vl-32b, each pair judged in both orders; vote = mean of the two.

## VLM self-consistency (same answer when A/B are swapped)

| Criterion | Same verdict both orders | Mean forward vote (+ = prefers first image) |
|---|---|---|
| faithful | 0.69 | +0.17 |
| coverage | 0.70 | +0.18 |
| language | 0.80 | +0.08 |
| layout | 0.49 | +0.34 |
| aesthetic | 0.55 | -0.24 |
| overall | 0.54 | +0.21 |

## Agreement with the human pair verdict (same side, on pairs both decided)

| Criterion | VLM (both orders) | VLM forward only | Metric Δ (faithful:numeric_fact, coverage:keypoint, language:language, layout:dom, aesthetic:aesthetic, overall:reward) | Human vs other human |
|---|---|---|---|---|
| faithful | 0.75 (12/16; decides 73%) | 0.64 (14/22; decides 100%) | 0.82 (9/11; decides 50%) | 1.00 (3/3; decides 43%) |
| coverage | 0.72 (78/108; decides 74%) | 0.68 (99/145; decides 99%) | 0.79 (45/57; decides 39%) | 0.92 (12/13; decides 41%) |
| language | 1.00 (14/14; decides 70%) | 1.00 (13/13; decides 65%) | 1.00 (8/8; decides 40%) | 1.00 (3/3; decides 60%) |
| layout | 0.67 (16/24; decides 56%) | 0.47 (17/36; decides 84%) | 0.90 (19/21; decides 49%) | 1.00 (7/7; decides 50%) |
| aesthetic | 0.60 (30/50; decides 60%) | 0.53 (42/79; decides 94%) | 0.53 (43/81; decides 96%) | 0.82 (9/11; decides 44%) |
| overall | 0.55 (62/112; decides 53%) | 0.54 (115/212; decides 100%) | 0.64 (134/211; decides 99%) | 0.73 (40/55; decides 82%) |

## VLM agreement by comparison

| Comparison | faithful | coverage | language | layout | aesthetic | overall |
|---|---|---|---|---|---|---|
| dapo_vs_base (291) | 0.50 (2/4; decides 57%) | 0.68 (30/44; decides 77%) | 1.00 (3/3; decides 75%) | 0.67 (4/6; decides 50%) | 0.67 (10/15; decides 60%) | 0.57 (20/35; decides 45%) |
| dapo_vs_best4 (132) | 0.00 (0/2; decides 50%) | 0.78 (18/23; decides 68%) | 1.00 (1/1; decides 25%) | 0.40 (2/5; decides 56%) | 0.38 (3/8; decides 62%) | 0.37 (10/27; decides 48%) |
| dapo_vs_gemini (153) | 1.00 (10/10; decides 91%) | 0.73 (30/41; decides 75%) | 1.00 (10/10; decides 83%) | 0.77 (10/13; decides 59%) | 0.63 (17/27; decides 59%) | 0.64 (32/50; decides 62%) |

## DAPO win rate: humans vs VLM (deck bootstrap 95% CI)

| Comparison | Criterion | Humans (rated pairs) | VLM (same pairs) | VLM (all judged pairs) |
|---|---|---|---|---|
| dapo_vs_base | overall | 0.504 [0.479, 0.529] | 0.420 [0.394, 0.448] | 0.423 [0.398, 0.448] |
| dapo_vs_base | aesthetic | 0.525 [0.514, 0.536] | 0.562 [0.534, 0.588] | 0.563 [0.537, 0.587] |
| dapo_vs_base | coverage | 0.480 [0.463, 0.498] | 0.374 [0.342, 0.409] | 0.376 [0.350, 0.405] |
| dapo_vs_base | layout | 0.507 [0.499, 0.515] | 0.506 [0.485, 0.528] | 0.502 [0.481, 0.525] |
| dapo_vs_base | faithful | 0.497 [0.490, 0.504] | 0.373 [0.341, 0.409] | 0.375 [0.346, 0.406] |
| dapo_vs_best4 | overall | 0.485 [0.437, 0.533] | 0.483 [0.436, 0.530] | 0.490 [0.450, 0.532] |
| dapo_vs_best4 | aesthetic | 0.519 [0.496, 0.543] | 0.587 [0.542, 0.637] | 0.577 [0.535, 0.622] |
| dapo_vs_best4 | coverage | 0.468 [0.442, 0.496] | 0.396 [0.340, 0.449] | 0.418 [0.367, 0.468] |
| dapo_vs_best4 | layout | 0.500 [0.479, 0.524] | 0.527 [0.484, 0.568] | 0.520 [0.482, 0.558] |
| dapo_vs_best4 | faithful | 0.508 [0.498, 0.520] | 0.403 [0.348, 0.458] | 0.420 [0.368, 0.471] |
| dapo_vs_gemini | overall | 0.505 [0.456, 0.551] | 0.453 [0.408, 0.498] | 0.442 [0.401, 0.485] |
| dapo_vs_gemini | aesthetic | 0.520 [0.480, 0.556] | 0.585 [0.540, 0.632] | 0.593 [0.546, 0.639] |
| dapo_vs_gemini | coverage | 0.492 [0.458, 0.526] | 0.404 [0.346, 0.465] | 0.383 [0.329, 0.441] |
| dapo_vs_gemini | layout | 0.529 [0.503, 0.552] | 0.516 [0.480, 0.556] | 0.516 [0.480, 0.556] |
| dapo_vs_gemini | faithful | 0.521 [0.505, 0.539] | 0.404 [0.346, 0.465] | 0.389 [0.333, 0.448] |

## Length and brightness preferences (pairs where the judge takes a side)

Longer = A has > 1.1x or < 0.9x B's visible words; brighter = |mean luminance A - B| > 0.03.

| Criterion | Humans pick longer | VLM picks longer | Humans pick brighter | VLM picks brighter |
|---|---|---|---|---|
| faithful | 0.78 (14/18) | 0.92 (201/219) | 0.20 (1/5) | 0.45 (29/64) |
| coverage | 0.78 (96/123) | 0.93 (202/218) | 0.43 (12/28) | 0.44 (28/63) |
| language | 0.75 (12/16) | 0.83 (75/90) | 0.38 (3/8) | 0.41 (14/34) |
| layout | 0.42 (15/36) | 0.53 (66/125) | 0.64 (9/14) | 0.50 (21/42) |
| aesthetic | 0.46 (27/59) | 0.18 (31/173) | 0.84 (36/43) | 0.34 (19/56) |
| overall | 0.65 (108/166) | 0.83 (123/149) | 0.66 (40/61) | 0.36 (21/58) |

