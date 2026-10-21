# Automatic judges vs human verdicts, round 2

Pairs with human ratings and a parsed VLM verdict: 576 (VLM file 634, human 576).
VLM: qwen3-vl-32b, each pair judged in both orders; vote = mean of the two.

## VLM self-consistency (same answer when A/B are swapped)

| Criterion | Same verdict both orders | Mean forward vote (+ = prefers first image) |
|---|---|---|
| faithful | 0.69 | +0.14 |
| coverage | 0.68 | +0.18 |
| language | 0.62 | +0.14 |
| layout | 0.68 | +0.18 |
| aesthetic | 0.79 | +0.02 |
| overall | 0.66 | +0.15 |

## Agreement with the human pair verdict (same side, on pairs both decided)

| Criterion | VLM (both orders) | VLM forward only | Metric Δ (faithful:numeric_fact, coverage:keypoint, language:language, layout:dom, aesthetic:aesthetic, overall:reward) | Human vs other human |
|---|---|---|---|---|
| faithful | 0.75 (12/16; decides 73%) | 0.59 (13/22; decides 100%) | 0.82 (9/11; decides 50%) | 1.00 (3/3; decides 43%) |
| coverage | 0.81 (81/100; decides 68%) | 0.73 (106/146; decides 100%) | 0.79 (45/57; decides 39%) | 0.92 (12/13; decides 41%) |
| language | 0.93 (14/15; decides 75%) | 0.89 (16/18; decides 90%) | 1.00 (8/8; decides 40%) | 1.00 (3/3; decides 60%) |
| layout | 0.75 (18/24; decides 56%) | 0.66 (21/32; decides 74%) | 0.90 (19/21; decides 49%) | 1.00 (7/7; decides 50%) |
| aesthetic | 0.78 (38/49; decides 58%) | 0.72 (48/67; decides 80%) | 0.53 (43/81; decides 96%) | 0.82 (9/11; decides 44%) |
| overall | 0.73 (101/138; decides 65%) | 0.69 (147/213; decides 100%) | 0.64 (134/211; decides 99%) | 0.73 (40/55; decides 82%) |

## VLM agreement by comparison

| Comparison | faithful | coverage | language | layout | aesthetic | overall |
|---|---|---|---|---|---|---|
| dapo_vs_base (291) | 0.50 (2/4; decides 57%) | 0.74 (31/42; decides 74%) | 0.67 (2/3; decides 75%) | 0.75 (3/4; decides 33%) | 0.61 (11/18; decides 72%) | 0.64 (32/50; decides 65%) |
| dapo_vs_best4 (132) | 0.00 (0/1; decides 25%) | 0.95 (18/19; decides 56%) | 1.00 (2/2; decides 50%) | 0.67 (2/3; decides 33%) | 0.83 (5/6; decides 46%) | 0.81 (25/31; decides 55%) |
| dapo_vs_gemini (153) | 0.91 (10/11; decides 100%) | 0.82 (32/39; decides 71%) | 1.00 (10/10; decides 83%) | 0.76 (13/17; decides 77%) | 0.88 (22/25; decides 54%) | 0.77 (44/57; decides 71%) |

## DAPO win rate: humans vs VLM (deck bootstrap 95% CI)

| Comparison | Criterion | Humans (rated pairs) | VLM (same pairs) | VLM (all judged pairs) |
|---|---|---|---|---|
| dapo_vs_base | overall | 0.504 [0.478, 0.530] | 0.363 [0.331, 0.398] | 0.359 [0.330, 0.391] |
| dapo_vs_base | aesthetic | 0.525 [0.513, 0.536] | 0.485 [0.466, 0.505] | 0.483 [0.465, 0.502] |
| dapo_vs_base | coverage | 0.480 [0.462, 0.498] | 0.379 [0.356, 0.403] | 0.375 [0.354, 0.397] |
| dapo_vs_base | layout | 0.507 [0.498, 0.515] | 0.468 [0.449, 0.487] | 0.469 [0.450, 0.488] |
| dapo_vs_base | faithful | 0.497 [0.490, 0.503] | 0.371 [0.347, 0.396] | 0.366 [0.343, 0.391] |
| dapo_vs_best4 | overall | 0.485 [0.437, 0.535] | 0.383 [0.339, 0.431] | 0.401 [0.357, 0.445] |
| dapo_vs_best4 | aesthetic | 0.519 [0.495, 0.543] | 0.494 [0.458, 0.530] | 0.498 [0.465, 0.532] |
| dapo_vs_best4 | coverage | 0.468 [0.441, 0.496] | 0.377 [0.340, 0.416] | 0.391 [0.353, 0.427] |
| dapo_vs_best4 | layout | 0.500 [0.479, 0.524] | 0.466 [0.439, 0.496] | 0.474 [0.449, 0.500] |
| dapo_vs_best4 | faithful | 0.508 [0.498, 0.520] | 0.384 [0.347, 0.426] | 0.396 [0.358, 0.432] |
| dapo_vs_gemini | overall | 0.505 [0.456, 0.551] | 0.366 [0.317, 0.418] | 0.364 [0.320, 0.412] |
| dapo_vs_gemini | aesthetic | 0.520 [0.480, 0.556] | 0.459 [0.415, 0.499] | 0.448 [0.408, 0.488] |
| dapo_vs_gemini | coverage | 0.492 [0.458, 0.526] | 0.379 [0.329, 0.432] | 0.376 [0.331, 0.424] |
| dapo_vs_gemini | layout | 0.529 [0.503, 0.552] | 0.448 [0.408, 0.491] | 0.444 [0.408, 0.480] |
| dapo_vs_gemini | faithful | 0.521 [0.505, 0.539] | 0.382 [0.330, 0.436] | 0.380 [0.334, 0.429] |

## Length and brightness preferences (pairs where the judge takes a side)

Longer = A has > 1.1x or < 0.9x B's visible words; brighter = |mean luminance A - B| > 0.03.

| Criterion | Humans pick longer | VLM picks longer | Humans pick brighter | VLM picks brighter |
|---|---|---|---|---|
| faithful | 0.78 (14/18) | 0.89 (185/209) | 0.20 (1/5) | 0.49 (31/63) |
| coverage | 0.78 (96/123) | 0.89 (186/208) | 0.43 (12/28) | 0.48 (29/60) |
| language | 0.75 (12/16) | 0.82 (157/192) | 0.38 (3/8) | 0.48 (30/62) |
| layout | 0.42 (15/36) | 0.75 (97/129) | 0.64 (9/14) | 0.56 (37/66) |
| aesthetic | 0.46 (27/59) | 0.61 (65/107) | 0.84 (36/43) | 0.34 (24/71) |
| overall | 0.65 (108/166) | 0.87 (177/204) | 0.66 (40/61) | 0.44 (36/82) |

