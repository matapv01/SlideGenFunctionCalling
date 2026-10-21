# Automatic judges vs human verdicts, round 1

Pairs with human ratings and a parsed VLM verdict: 567 (VLM file 567, human 567).
VLM: qwen2.5-vl-32b, each pair judged in both orders; vote = mean of the two.

## VLM self-consistency (same answer when A/B are swapped)

| Criterion | Same verdict both orders | Mean forward vote (+ = prefers first image) |
|---|---|---|
| faithful | 0.67 | +0.19 |
| coverage | 0.67 | +0.19 |
| language | 0.72 | +0.15 |
| layout | 0.48 | +0.37 |
| aesthetic | 0.53 | -0.28 |
| overall | 0.57 | +0.22 |

## Agreement with the human pair verdict (same side, on pairs both decided)

| Criterion | VLM (both orders) | VLM forward only | Metric Δ (faithful:numeric_fact, coverage:keypoint, language:language, layout:dom, aesthetic:aesthetic, overall:reward) | Human vs other human |
|---|---|---|---|---|
| faithful | 0.79 (27/34; decides 64%) | 0.74 (39/53; decides 100%) | 0.86 (6/7; decides 13%) | 1.00 (5/5; decides 18%) |
| coverage | 0.79 (119/151; decides 68%) | 0.67 (149/221; decides 100%) | n/a | 0.86 (24/28; decides 57%) |
| language | 0.98 (54/55; decides 71%) | 0.84 (42/50; decides 64%) | 1.00 (33/33; decides 42%) | 0.97 (59/61; decides 79%) |
| layout | 0.84 (62/74; decides 54%) | 0.70 (87/124; decides 91%) | 0.85 (77/91; decides 67%) | 0.96 (50/52; decides 57%) |
| aesthetic | 0.44 (37/84; decides 44%) | 0.49 (85/173; decides 90%) | 0.64 (116/181; decides 94%) | 0.91 (61/67; decides 42%) |
| overall | 0.67 (130/193; decides 56%) | 0.60 (202/336; decides 98%) | 0.70 (240/341; decides 100%) | 0.81 (210/258; decides 76%) |

## VLM agreement by comparison

| Comparison | faithful | coverage | language | layout | aesthetic | overall |
|---|---|---|---|---|---|---|
| dapo_vs_base (254) | 0.70 (7/10; decides 67%) | 0.76 (38/50; decides 72%) | 1.00 (32/32; decides 74%) | 0.83 (20/24; decides 51%) | 0.34 (10/29; decides 45%) | 0.68 (50/74; decides 59%) |
| dapo_vs_best8 (145) | 0.88 (7/8; decides 67%) | 0.83 (34/41; decides 63%) | 0.93 (14/15; decides 65%) | 0.82 (18/22; decides 59%) | 0.56 (15/27; decides 56%) | 0.73 (33/45; decides 51%) |
| dapo_vs_gemini (168) | 0.81 (13/16; decides 62%) | 0.78 (47/60; decides 68%) | 1.00 (8/8; decides 67%) | 0.86 (24/28; decides 54%) | 0.43 (12/28; decides 35%) | 0.64 (47/74; decides 58%) |

## DAPO win rate: humans vs VLM (deck bootstrap 95% CI)

| Comparison | Criterion | Humans (rated pairs) | VLM (same pairs) | VLM (all judged pairs) |
|---|---|---|---|---|
| dapo_vs_base | overall | 0.565 [0.530, 0.600] | 0.521 [0.487, 0.554] | 0.521 [0.487, 0.554] |
| dapo_vs_base | aesthetic | 0.536 [0.515, 0.557] | 0.472 [0.432, 0.510] | 0.472 [0.432, 0.510] |
| dapo_vs_base | coverage | 0.501 [0.484, 0.518] | 0.514 [0.469, 0.559] | 0.514 [0.469, 0.559] |
| dapo_vs_base | layout | 0.527 [0.510, 0.543] | 0.523 [0.497, 0.548] | 0.523 [0.497, 0.548] |
| dapo_vs_base | faithful | 0.506 [0.498, 0.514] | 0.517 [0.472, 0.561] | 0.517 [0.472, 0.561] |
| dapo_vs_best8 | overall | 0.456 [0.419, 0.492] | 0.505 [0.457, 0.548] | 0.505 [0.457, 0.548] |
| dapo_vs_best8 | aesthetic | 0.468 [0.443, 0.491] | 0.571 [0.536, 0.608] | 0.571 [0.536, 0.608] |
| dapo_vs_best8 | coverage | 0.471 [0.446, 0.495] | 0.429 [0.380, 0.476] | 0.429 [0.380, 0.476] |
| dapo_vs_best8 | layout | 0.466 [0.439, 0.489] | 0.526 [0.483, 0.566] | 0.526 [0.483, 0.566] |
| dapo_vs_best8 | faithful | 0.496 [0.486, 0.505] | 0.434 [0.384, 0.481] | 0.434 [0.384, 0.481] |
| dapo_vs_gemini | overall | 0.458 [0.411, 0.504] | 0.423 [0.371, 0.476] | 0.423 [0.371, 0.476] |
| dapo_vs_gemini | aesthetic | 0.503 [0.474, 0.533] | 0.513 [0.460, 0.564] | 0.513 [0.460, 0.564] |
| dapo_vs_gemini | coverage | 0.451 [0.423, 0.481] | 0.375 [0.324, 0.429] | 0.375 [0.324, 0.429] |
| dapo_vs_gemini | layout | 0.537 [0.509, 0.565] | 0.510 [0.465, 0.556] | 0.510 [0.465, 0.556] |
| dapo_vs_gemini | faithful | 0.503 [0.485, 0.522] | 0.378 [0.326, 0.433] | 0.378 [0.326, 0.433] |

## Length and brightness preferences (pairs where the judge takes a side)

Longer = A has > 1.1x or < 0.9x B's visible words; brighter = |mean luminance A - B| > 0.03.

| Criterion | Humans pick longer | VLM picks longer | Humans pick brighter | VLM picks brighter |
|---|---|---|---|---|
| faithful | 0.48 (20/42) | 0.84 (196/234) | 0.57 (8/14) | 0.54 (44/82) |
| coverage | 0.65 (119/182) | 0.85 (199/234) | 0.53 (28/53) | 0.54 (44/82) |
| language | 0.65 (36/55) | 0.71 (80/112) | 0.44 (8/18) | 0.53 (30/57) |
| layout | 0.29 (29/101) | 0.41 (61/149) | 0.69 (38/55) | 0.59 (44/74) |
| aesthetic | 0.39 (53/135) | 0.25 (44/174) | 0.70 (61/87) | 0.43 (26/60) |
| overall | 0.54 (131/242) | 0.66 (127/192) | 0.63 (66/105) | 0.45 (38/84) |

