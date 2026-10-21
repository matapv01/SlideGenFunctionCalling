# Automatic judges vs human verdicts, round 1

Pairs with human ratings and a parsed VLM verdict: 567 (VLM file 567, human 567).
VLM: qwen3-vl-32b, each pair judged in both orders; vote = mean of the two.

## VLM self-consistency (same answer when A/B are swapped)

| Criterion | Same verdict both orders | Mean forward vote (+ = prefers first image) |
|---|---|---|
| faithful | 0.71 | +0.09 |
| coverage | 0.72 | +0.10 |
| language | 0.62 | +0.10 |
| layout | 0.59 | +0.26 |
| aesthetic | 0.70 | +0.05 |
| overall | 0.66 | +0.14 |

## Agreement with the human pair verdict (same side, on pairs both decided)

| Criterion | VLM (both orders) | VLM forward only | Metric Δ (faithful:numeric_fact, coverage:keypoint, language:language, layout:dom, aesthetic:aesthetic, overall:reward) | Human vs other human |
|---|---|---|---|---|
| faithful | 0.76 (22/29; decides 55%) | 0.58 (31/53; decides 100%) | 0.86 (6/7; decides 13%) | 1.00 (5/5; decides 18%) |
| coverage | 0.80 (127/158; decides 71%) | 0.68 (152/222; decides 100%) | n/a | 0.86 (24/28; decides 57%) |
| language | 0.93 (67/72; decides 92%) | 0.89 (66/74; decides 95%) | 1.00 (33/33; decides 42%) | 0.97 (59/61; decides 79%) |
| layout | 0.81 (71/88; decides 65%) | 0.77 (66/86; decides 63%) | 0.85 (77/91; decides 67%) | 0.96 (50/52; decides 57%) |
| aesthetic | 0.72 (89/124; decides 65%) | 0.72 (91/127; decides 66%) | 0.64 (116/181; decides 94%) | 0.91 (61/67; decides 42%) |
| overall | 0.78 (174/224; decides 65%) | 0.69 (236/340; decides 99%) | 0.70 (240/341; decides 100%) | 0.81 (210/258; decides 76%) |

## VLM agreement by comparison

| Comparison | faithful | coverage | language | layout | aesthetic | overall |
|---|---|---|---|---|---|---|
| dapo_vs_base (254) | 0.67 (6/9; decides 60%) | 0.86 (43/50; decides 72%) | 0.97 (38/39; decides 91%) | 0.70 (21/30; decides 64%) | 0.58 (22/38; decides 58%) | 0.74 (66/89; decides 71%) |
| dapo_vs_best8 (145) | 0.75 (6/8; decides 67%) | 0.78 (39/50; decides 77%) | 0.83 (19/23; decides 100%) | 0.76 (16/21; decides 57%) | 0.68 (21/31; decides 65%) | 0.81 (52/64; decides 72%) |
| dapo_vs_gemini (168) | 0.83 (10/12; decides 46%) | 0.78 (45/58; decides 66%) | 1.00 (10/10; decides 83%) | 0.92 (34/37; decides 71%) | 0.84 (46/55; decides 70%) | 0.79 (56/71; decides 55%) |

## DAPO win rate: humans vs VLM (deck bootstrap 95% CI)

| Comparison | Criterion | Humans (rated pairs) | VLM (same pairs) | VLM (all judged pairs) |
|---|---|---|---|---|
| dapo_vs_base | overall | 0.565 [0.531, 0.599] | 0.513 [0.467, 0.559] | 0.513 [0.467, 0.559] |
| dapo_vs_base | aesthetic | 0.536 [0.514, 0.558] | 0.523 [0.497, 0.549] | 0.523 [0.497, 0.549] |
| dapo_vs_base | coverage | 0.501 [0.484, 0.518] | 0.502 [0.454, 0.550] | 0.502 [0.454, 0.550] |
| dapo_vs_base | layout | 0.527 [0.511, 0.543] | 0.522 [0.503, 0.541] | 0.522 [0.503, 0.541] |
| dapo_vs_base | faithful | 0.506 [0.498, 0.513] | 0.510 [0.463, 0.558] | 0.510 [0.463, 0.558] |
| dapo_vs_best8 | overall | 0.456 [0.417, 0.492] | 0.429 [0.367, 0.492] | 0.429 [0.367, 0.492] |
| dapo_vs_best8 | aesthetic | 0.468 [0.442, 0.491] | 0.495 [0.458, 0.531] | 0.495 [0.458, 0.531] |
| dapo_vs_best8 | coverage | 0.471 [0.446, 0.495] | 0.400 [0.344, 0.459] | 0.400 [0.344, 0.459] |
| dapo_vs_best8 | layout | 0.466 [0.439, 0.489] | 0.476 [0.441, 0.509] | 0.476 [0.441, 0.509] |
| dapo_vs_best8 | faithful | 0.496 [0.486, 0.505] | 0.398 [0.339, 0.459] | 0.398 [0.339, 0.459] |
| dapo_vs_gemini | overall | 0.458 [0.411, 0.505] | 0.396 [0.338, 0.451] | 0.396 [0.338, 0.451] |
| dapo_vs_gemini | aesthetic | 0.503 [0.474, 0.534] | 0.415 [0.375, 0.455] | 0.415 [0.375, 0.455] |
| dapo_vs_gemini | coverage | 0.451 [0.423, 0.479] | 0.375 [0.316, 0.434] | 0.375 [0.316, 0.434] |
| dapo_vs_gemini | layout | 0.537 [0.510, 0.566] | 0.493 [0.456, 0.527] | 0.493 [0.456, 0.527] |
| dapo_vs_gemini | faithful | 0.503 [0.485, 0.521] | 0.374 [0.314, 0.433] | 0.374 [0.314, 0.433] |

## Length and brightness preferences (pairs where the judge takes a side)

Longer = A has > 1.1x or < 0.9x B's visible words; brighter = |mean luminance A - B| > 0.03.

| Criterion | Humans pick longer | VLM picks longer | Humans pick brighter | VLM picks brighter |
|---|---|---|---|---|
| faithful | 0.48 (20/42) | 0.81 (193/239) | 0.57 (8/14) | 0.50 (47/94) |
| coverage | 0.65 (119/182) | 0.81 (194/239) | 0.53 (28/53) | 0.51 (46/90) |
| language | 0.65 (36/55) | 0.68 (154/228) | 0.44 (8/18) | 0.57 (52/91) |
| layout | 0.29 (29/101) | 0.54 (84/157) | 0.69 (38/55) | 0.71 (55/78) |
| aesthetic | 0.39 (53/135) | 0.54 (82/153) | 0.70 (61/87) | 0.60 (53/89) |
| overall | 0.54 (131/242) | 0.77 (172/223) | 0.63 (66/105) | 0.62 (61/98) |

