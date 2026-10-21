# Automatic judges vs human verdicts, round 1

Pairs with human ratings and a parsed VLM verdict: 567 (VLM file 567, human 567).
VLM: gemma-3-27b, each pair judged in both orders; vote = mean of the two.

## VLM self-consistency (same answer when A/B are swapped)

| Criterion | Same verdict both orders | Mean forward vote (+ = prefers first image) |
|---|---|---|
| faithful | 0.41 | -0.47 |
| coverage | 0.41 | -0.48 |
| language | 0.89 | -0.02 |
| layout | 0.47 | +0.19 |
| aesthetic | 0.49 | -0.06 |
| overall | 0.47 | -0.02 |

## Agreement with the human pair verdict (same side, on pairs both decided)

| Criterion | VLM (both orders) | VLM forward only | Metric Δ (faithful:numeric_fact, coverage:keypoint, language:language, layout:dom, aesthetic:aesthetic, overall:reward) | Human vs other human |
|---|---|---|---|---|
| faithful | 0.64 (9/14; decides 26%) | 0.55 (29/53; decides 100%) | 0.86 (6/7; decides 13%) | 1.00 (5/5; decides 18%) |
| coverage | 0.68 (50/73; decides 33%) | 0.58 (124/213; decides 96%) | n/a | 0.86 (24/28; decides 57%) |
| language | 0.64 (25/39; decides 50%) | 0.67 (24/36; decides 46%) | 1.00 (33/33; decides 42%) | 0.97 (59/61; decides 79%) |
| layout | 0.77 (53/69; decides 51%) | 0.63 (84/134; decides 99%) | 0.85 (77/91; decides 67%) | 0.96 (50/52; decides 57%) |
| aesthetic | 0.59 (51/87; decides 45%) | 0.54 (102/189; decides 98%) | 0.64 (116/181; decides 94%) | 0.91 (61/67; decides 42%) |
| overall | 0.62 (94/152; decides 44%) | 0.57 (194/340; decides 99%) | 0.70 (240/341; decides 100%) | 0.81 (210/258; decides 76%) |

## VLM agreement by comparison

| Comparison | faithful | coverage | language | layout | aesthetic | overall |
|---|---|---|---|---|---|---|
| dapo_vs_base (254) | 0.60 (3/5; decides 33%) | 0.79 (19/24; decides 35%) | 0.73 (16/22; decides 51%) | 0.68 (13/19; decides 40%) | 0.52 (14/27; decides 42%) | 0.53 (25/47; decides 38%) |
| dapo_vs_best8 (145) | 1.00 (4/4; decides 33%) | 0.65 (13/20; decides 31%) | 0.46 (6/13; decides 57%) | 0.76 (13/17; decides 46%) | 0.55 (11/20; decides 42%) | 0.71 (27/38; decides 43%) |
| dapo_vs_gemini (168) | 0.40 (2/5; decides 19%) | 0.62 (18/29; decides 33%) | 0.75 (3/4; decides 33%) | 0.82 (27/33; decides 63%) | 0.65 (26/40; decides 51%) | 0.63 (42/67; decides 52%) |

## DAPO win rate: humans vs VLM (deck bootstrap 95% CI)

| Comparison | Criterion | Humans (rated pairs) | VLM (same pairs) | VLM (all judged pairs) |
|---|---|---|---|---|
| dapo_vs_base | overall | 0.565 [0.529, 0.600] | 0.505 [0.477, 0.531] | 0.505 [0.477, 0.531] |
| dapo_vs_base | aesthetic | 0.536 [0.516, 0.558] | 0.469 [0.428, 0.509] | 0.469 [0.428, 0.509] |
| dapo_vs_base | coverage | 0.501 [0.484, 0.518] | 0.542 [0.506, 0.581] | 0.542 [0.506, 0.581] |
| dapo_vs_base | layout | 0.527 [0.512, 0.542] | 0.517 [0.490, 0.542] | 0.517 [0.490, 0.542] |
| dapo_vs_base | faithful | 0.506 [0.498, 0.514] | 0.536 [0.501, 0.576] | 0.536 [0.501, 0.576] |
| dapo_vs_best8 | overall | 0.456 [0.417, 0.493] | 0.484 [0.438, 0.530] | 0.484 [0.438, 0.530] |
| dapo_vs_best8 | aesthetic | 0.468 [0.442, 0.491] | 0.516 [0.468, 0.563] | 0.516 [0.468, 0.563] |
| dapo_vs_best8 | coverage | 0.471 [0.446, 0.494] | 0.457 [0.425, 0.490] | 0.457 [0.425, 0.490] |
| dapo_vs_best8 | layout | 0.466 [0.439, 0.490] | 0.481 [0.434, 0.528] | 0.481 [0.434, 0.528] |
| dapo_vs_best8 | faithful | 0.496 [0.485, 0.505] | 0.462 [0.429, 0.496] | 0.462 [0.429, 0.496] |
| dapo_vs_gemini | overall | 0.458 [0.411, 0.504] | 0.536 [0.488, 0.579] | 0.536 [0.488, 0.579] |
| dapo_vs_gemini | aesthetic | 0.503 [0.474, 0.534] | 0.516 [0.466, 0.564] | 0.516 [0.466, 0.564] |
| dapo_vs_gemini | coverage | 0.451 [0.423, 0.481] | 0.509 [0.472, 0.548] | 0.509 [0.472, 0.548] |
| dapo_vs_gemini | layout | 0.537 [0.509, 0.565] | 0.570 [0.521, 0.619] | 0.570 [0.521, 0.619] |
| dapo_vs_gemini | faithful | 0.503 [0.485, 0.523] | 0.506 [0.469, 0.545] | 0.506 [0.469, 0.545] |

## Length and brightness preferences (pairs where the judge takes a side)

Longer = A has > 1.1x or < 0.9x B's visible words; brighter = |mean luminance A - B| > 0.03.

| Criterion | Humans pick longer | VLM picks longer | Humans pick brighter | VLM picks brighter |
|---|---|---|---|---|
| faithful | 0.48 (20/42) | 0.72 (94/131) | 0.57 (8/14) | 0.55 (35/64) |
| coverage | 0.65 (119/182) | 0.70 (88/125) | 0.53 (28/53) | 0.58 (38/65) |
| language | 0.65 (36/55) | 0.61 (30/49) | 0.44 (8/18) | 0.55 (6/11) |
| layout | 0.29 (29/101) | 0.38 (55/144) | 0.69 (38/55) | 0.57 (40/70) |
| aesthetic | 0.39 (53/135) | 0.31 (52/169) | 0.70 (61/87) | 0.53 (33/62) |
| overall | 0.54 (131/242) | 0.38 (58/153) | 0.63 (66/105) | 0.58 (38/66) |

