# Round-2 decomposition (exploration split)

Ratings: 651 from ['A1', 'A2']; pairs: 533.

## dapo_vs_base (268 pairs, 176 with different visible text)

### Win rate of DAPO by criterion: all pairs vs differing pairs vs differing and defect-free

| Criterion / subset | Pairs | Win | Tie | Loss | Win rate [95% CI] |
|---|---|---|---|---|---|
| overall · all | 268 | 31 | 206 | 31 | 0.507 [0.478, 0.537] |
| overall · differing | 176 | 27 | 118 | 31 | 0.500 [0.458, 0.542] |
| overall · differing, both defect-free | 163 | 22 | 110 | 31 | 0.485 [0.439, 0.530] |
| aesthetic · all | 268 | 17 | 248 | 3 | 0.524 [0.512, 0.538] |
| aesthetic · differing | 176 | 13 | 160 | 3 | 0.526 [0.509, 0.544] |
| aesthetic · differing, both defect-free | 163 | 9 | 151 | 3 | 0.518 [0.500, 0.536] |
| layout · all | 268 | 6 | 259 | 3 | 0.504 [0.495, 0.513] |
| layout · differing | 176 | 6 | 167 | 3 | 0.506 [0.492, 0.520] |
| layout · differing, both defect-free | 163 | 2 | 159 | 2 | 0.498 [0.488, 0.509] |
| coverage · all | 268 | 15 | 225 | 28 | 0.481 [0.464, 0.500] |
| coverage · differing | 176 | 15 | 133 | 28 | 0.472 [0.444, 0.500] |
| coverage · differing, both defect-free | 163 | 11 | 125 | 27 | 0.463 [0.436, 0.492] |
| language · all | 268 | 1 | 265 | 2 | 0.499 [0.493, 0.505] |
| language · differing | 176 | 1 | 173 | 2 | 0.499 [0.490, 0.507] |
| language · differing, both defect-free | 163 | 1 | 160 | 2 | 0.498 [0.490, 0.507] |
| faithful · all | 268 | 2 | 261 | 5 | 0.497 [0.489, 0.505] |
| faithful · differing | 176 | 2 | 169 | 5 | 0.496 [0.484, 0.508] |
| faithful · differing, both defect-free | 163 | 2 | 156 | 5 | 0.495 [0.482, 0.508] |

### Coverage and overall by length (DAPO visible words / rival visible words), differing pairs

| Length ratio | Pairs | Coverage win rate | Overall win rate | Aesthetic win rate |
|---|---|---|---|---|
| < 0.70 | 30 | 0.433 | 0.500 | 0.542 |
| 0.70–0.85 | 35 | 0.450 | 0.464 | 0.514 |
| 0.85–1.00 | 79 | 0.481 | 0.491 | 0.509 |
| ≥ 1.00 | 32 | 0.508 | 0.562 | 0.562 |

Coverage win rate, ratio < 0.85 minus ≥ 0.85: -0.046 [-0.117, +0.022]

### What decides the overall verdict (pair verdicts; rows = criterion, cols = overall)

| Criterion verdict | Overall DAPO wins | Overall tie | Overall DAPO loses |
|---|---|---|---|
| aesthetic: DAPO wins | 16 | 1 | 0 |
| aesthetic: DAPO loses | 0 | 0 | 3 |
| coverage: DAPO wins | 15 | 0 | 0 |
| coverage: DAPO loses | 1 | 3 | 24 |
| layout: DAPO wins | 5 | 1 | 0 |
| layout: DAPO loses | 0 | 1 | 2 |
| faithful: DAPO wins | 2 | 0 | 0 |
| faithful: DAPO loses | 0 | 1 | 4 |

### By slide type (differing pairs)

| Slide type | Pairs | Overall | Aesthetic | Coverage |
|---|---|---|---|---|
| CHART_TOOLS | 9 | 0.500 | 0.500 | 0.500 |
| CONTENT_TOOLS | 140 | 0.495 | 0.525 | 0.466 |
| INTRO_TOOLS | 14 | 0.500 | 0.500 | 0.500 |
| TEAM_TOOLS | 1 | 0.000 | 0.500 | 0.000 |
| THANK_YOU_TOOLS | 10 | 0.650 | 0.600 | 0.550 |
| TRANSITION_TOOLS | 2 | 0.375 | 0.500 | 0.375 |

### What DAPO leaves out, by coverage verdict (differing pairs)

Source numbers / proper names that the rival shows and DAPO does not (mean per pair), and automatic metric differences DAPO minus rival.

| Coverage verdict | Pairs | Words DAPO/rival | Numbers dropped | Names dropped | Δ keypoint | Δ numeric_fact | Δ ViT |
|---|---|---|---|---|---|---|---|
| DAPO loses | 28 | 0.78 | 0.29 | 0.50 | -0.172 | -0.049 | -0.068 |
| tie | 133 | 0.91 | 0.19 | 0.12 | -0.011 | -0.025 | -0.030 |
| DAPO wins | 15 | 0.84 | 0.40 | 0.13 | +0.004 | -0.014 | +0.106 |

Examples (dapo_vs_base): {"coverage_loss": ["2039_02", "2043_02", "2040_04", "2027_04", "2050_04", "2048_06", "2030_05", "2006_03", "2012_04", "2006_02", "2025_02", "2000_05", "2027_06", "2026_04", "2015_02", "2035_02", "2002_04", "2021_04", "2013_02", "2022_01", "2049_05", "2033_04", "2024_02", "2011_03", "2024_03", "2032_02", "2017_03", "2018_04"], "aesthetic_win_clean": ["2036_04", "2047_02", "2014_06", "2016_05", "2049_07", "2026_02", "2020_07", "2047_07", "2021_04"], "overall_loss": ["2039_02", "2043_02", "2006_06", "2040_04", "2027_04", "2050_04", "2030_05", "2048_01", "2014_04", "2006_03", "2012_04", "2006_02", "2027_06", "2024_04", "2026_04", "2015_02", "2035_02", "2002_04", "2033_03", "2013_02", "2022_01", "2021_06", "2006_07", "2049_05", "2033_04", "2024_02", "2011_03", "2024_03", "2032_02", "2017_03", "2018_04"]}

## dapo_vs_best4 (120 pairs, 106 with different visible text)

### Win rate of DAPO by criterion: all pairs vs differing pairs vs differing and defect-free

| Criterion / subset | Pairs | Win | Tie | Loss | Win rate [95% CI] |
|---|---|---|---|---|---|
| overall · all | 120 | 19 | 76 | 25 | 0.490 [0.442, 0.539] |
| overall · differing | 106 | 17 | 64 | 25 | 0.481 [0.430, 0.534] |
| overall · differing, both defect-free | 101 | 15 | 62 | 24 | 0.475 [0.420, 0.530] |
| aesthetic · all | 120 | 10 | 107 | 3 | 0.525 [0.498, 0.553] |
| aesthetic · differing | 106 | 8 | 95 | 3 | 0.521 [0.495, 0.550] |
| aesthetic · differing, both defect-free | 101 | 7 | 91 | 3 | 0.517 [0.491, 0.544] |
| layout · all | 120 | 4 | 111 | 5 | 0.498 [0.473, 0.525] |
| layout · differing | 106 | 4 | 97 | 5 | 0.498 [0.468, 0.528] |
| layout · differing, both defect-free | 101 | 3 | 95 | 3 | 0.500 [0.476, 0.523] |
| coverage · all | 120 | 6 | 95 | 19 | 0.463 [0.435, 0.491] |
| coverage · differing | 106 | 6 | 81 | 19 | 0.458 [0.426, 0.490] |
| coverage · differing, both defect-free | 101 | 5 | 77 | 19 | 0.453 [0.421, 0.485] |
| language · all | 120 | 1 | 117 | 2 | 0.496 [0.481, 0.508] |
| language · differing | 106 | 1 | 103 | 2 | 0.495 [0.478, 0.510] |
| language · differing, both defect-free | 101 | 1 | 98 | 2 | 0.495 [0.477, 0.510] |
| faithful · all | 120 | 3 | 116 | 1 | 0.508 [0.498, 0.522] |
| faithful · differing | 106 | 3 | 102 | 1 | 0.509 [0.497, 0.526] |
| faithful · differing, both defect-free | 101 | 2 | 98 | 1 | 0.507 [0.495, 0.524] |

### Coverage and overall by length (DAPO visible words / rival visible words), differing pairs

| Length ratio | Pairs | Coverage win rate | Overall win rate | Aesthetic win rate |
|---|---|---|---|---|
| < 0.70 | 20 | 0.338 | 0.475 | 0.600 |
| 0.70–0.85 | 27 | 0.472 | 0.472 | 0.509 |
| 0.85–1.00 | 33 | 0.485 | 0.523 | 0.515 |
| ≥ 1.00 | 26 | 0.500 | 0.442 | 0.481 |

Coverage win rate, ratio < 0.85 minus ≥ 0.85: -0.077 [-0.133, -0.011]

### What decides the overall verdict (pair verdicts; rows = criterion, cols = overall)

| Criterion verdict | Overall DAPO wins | Overall tie | Overall DAPO loses |
|---|---|---|---|
| aesthetic: DAPO wins | 9 | 1 | 0 |
| aesthetic: DAPO loses | 0 | 0 | 3 |
| coverage: DAPO wins | 5 | 1 | 0 |
| coverage: DAPO loses | 1 | 1 | 17 |
| layout: DAPO wins | 4 | 0 | 0 |
| layout: DAPO loses | 0 | 1 | 4 |
| faithful: DAPO wins | 2 | 1 | 0 |
| faithful: DAPO loses | 0 | 0 | 1 |

### By slide type (differing pairs)

| Slide type | Pairs | Overall | Aesthetic | Coverage |
|---|---|---|---|---|
| CHART_TOOLS | 3 | 0.500 | 0.500 | 0.500 |
| CONTENT_TOOLS | 77 | 0.477 | 0.516 | 0.451 |
| INTRO_TOOLS | 15 | 0.417 | 0.500 | 0.450 |
| TEAM_TOOLS | 1 | 0.500 | 0.500 | 0.500 |
| THANK_YOU_TOOLS | 9 | 0.611 | 0.611 | 0.500 |
| TRANSITION_TOOLS | 1 | 0.500 | 0.500 | 0.500 |

### What DAPO leaves out, by coverage verdict (differing pairs)

Source numbers / proper names that the rival shows and DAPO does not (mean per pair), and automatic metric differences DAPO minus rival.

| Coverage verdict | Pairs | Words DAPO/rival | Numbers dropped | Names dropped | Δ keypoint | Δ numeric_fact | Δ ViT |
|---|---|---|---|---|---|---|---|
| DAPO loses | 19 | 0.75 | 0.95 | 0.32 | -0.056 | -0.204 | -0.033 |
| tie | 81 | 0.88 | 0.32 | 0.22 | -0.032 | -0.043 | -0.118 |
| DAPO wins | 6 | 0.94 | 0.17 | 0.00 | +0.121 | +0.062 | -0.122 |

Examples (dapo_vs_best4): {"coverage_loss": ["2050_00", "2043_05", "2047_02", "2022_04", "2037_02", "2021_04", "2019_03", "2033_06", "2035_03", "2006_03", "2015_04", "2012_04", "2021_05", "2018_04", "2000_06", "2002_06", "2017_00", "2047_04", "2032_02"], "aesthetic_win_clean": ["2047_07", "2006_01", "2036_07", "2021_04", "2035_05", "2048_07", "2008_05"], "overall_loss": ["2050_00", "2043_05", "2039_00", "2022_04", "2037_02", "2019_01", "2019_03", "2033_06", "2035_03", "2022_06", "2006_03", "2015_04", "2044_07", "2036_00", "2018_00", "2012_04", "2021_05", "2018_04", "2002_00", "2000_06", "2002_06", "2017_00", "2035_04", "2047_04", "2032_02"]}

## dapo_vs_gemini (145 pairs, 135 with different visible text)

### Win rate of DAPO by criterion: all pairs vs differing pairs vs differing and defect-free

| Criterion / subset | Pairs | Win | Tie | Loss | Win rate [95% CI] |
|---|---|---|---|---|---|
| overall · all | 145 | 33 | 77 | 35 | 0.505 [0.458, 0.549] |
| overall · differing | 135 | 31 | 70 | 34 | 0.502 [0.453, 0.552] |
| overall · differing, both defect-free | 119 | 24 | 65 | 30 | 0.489 [0.436, 0.545] |
| aesthetic · all | 145 | 20 | 110 | 15 | 0.517 [0.477, 0.553] |
| aesthetic · differing | 135 | 19 | 102 | 14 | 0.519 [0.477, 0.559] |
| aesthetic · differing, both defect-free | 119 | 13 | 94 | 12 | 0.506 [0.467, 0.547] |
| layout · all | 145 | 13 | 128 | 4 | 0.526 [0.502, 0.550] |
| layout · differing | 135 | 12 | 119 | 4 | 0.524 [0.498, 0.550] |
| layout · differing, both defect-free | 119 | 8 | 109 | 2 | 0.519 [0.493, 0.542] |
| coverage · all | 145 | 20 | 98 | 27 | 0.490 [0.455, 0.521] |
| coverage · differing | 135 | 20 | 88 | 27 | 0.489 [0.453, 0.526] |
| coverage · differing, both defect-free | 119 | 16 | 79 | 24 | 0.487 [0.448, 0.528] |
| language · all | 145 | 6 | 136 | 3 | 0.510 [0.495, 0.526] |
| language · differing | 135 | 6 | 126 | 3 | 0.511 [0.495, 0.529] |
| language · differing, both defect-free | 119 | 6 | 110 | 3 | 0.513 [0.493, 0.532] |
| faithful · all | 145 | 8 | 136 | 1 | 0.522 [0.504, 0.541] |
| faithful · differing | 135 | 8 | 126 | 1 | 0.524 [0.504, 0.544] |
| faithful · differing, both defect-free | 119 | 8 | 110 | 1 | 0.527 [0.506, 0.550] |

### Coverage and overall by length (DAPO visible words / rival visible words), differing pairs

| Length ratio | Pairs | Coverage win rate | Overall win rate | Aesthetic win rate |
|---|---|---|---|---|
| < 0.70 | 36 | 0.396 | 0.500 | 0.583 |
| 0.70–0.85 | 27 | 0.398 | 0.407 | 0.491 |
| 0.85–1.00 | 32 | 0.492 | 0.461 | 0.461 |
| ≥ 1.00 | 40 | 0.631 | 0.600 | 0.525 |

Coverage win rate, ratio < 0.85 minus ≥ 0.85: -0.173 [-0.263, -0.085]

### What decides the overall verdict (pair verdicts; rows = criterion, cols = overall)

| Criterion verdict | Overall DAPO wins | Overall tie | Overall DAPO loses |
|---|---|---|---|
| aesthetic: DAPO wins | 19 | 1 | 0 |
| aesthetic: DAPO loses | 0 | 2 | 13 |
| coverage: DAPO wins | 17 | 3 | 0 |
| coverage: DAPO loses | 0 | 2 | 25 |
| layout: DAPO wins | 12 | 1 | 0 |
| layout: DAPO loses | 0 | 0 | 4 |
| faithful: DAPO wins | 8 | 0 | 0 |
| faithful: DAPO loses | 0 | 0 | 1 |

### By slide type (differing pairs)

| Slide type | Pairs | Overall | Aesthetic | Coverage |
|---|---|---|---|---|
| CHART_TOOLS | 3 | 0.167 | 0.500 | 0.333 |
| CONTENT_TOOLS | 94 | 0.489 | 0.500 | 0.503 |
| INTRO_TOOLS | 20 | 0.537 | 0.525 | 0.475 |
| TEAM_TOOLS | 2 | 0.250 | 0.500 | 0.250 |
| THANK_YOU_TOOLS | 15 | 0.600 | 0.633 | 0.483 |
| TRANSITION_TOOLS | 1 | 1.000 | 0.500 | 0.500 |

### What DAPO leaves out, by coverage verdict (differing pairs)

Source numbers / proper names that the rival shows and DAPO does not (mean per pair), and automatic metric differences DAPO minus rival.

| Coverage verdict | Pairs | Words DAPO/rival | Numbers dropped | Names dropped | Δ keypoint | Δ numeric_fact | Δ ViT |
|---|---|---|---|---|---|---|---|
| DAPO loses | 27 | 0.77 | 0.48 | 0.63 | -0.119 | -0.077 | -0.041 |
| tie | 88 | 0.89 | 0.33 | 0.24 | -0.017 | -0.064 | -0.044 |
| DAPO wins | 20 | 1.58 | 0.00 | 0.00 | +0.333 | +0.335 | +0.380 |

Examples (dapo_vs_gemini): {"coverage_loss": ["2017_03", "2049_00", "2012_02", "2012_05", "2031_02", "2040_04", "2015_05", "2036_05", "2027_04", "2049_03", "2013_04", "2021_02", "2011_01", "2050_04", "2002_05", "2047_04", "2004_05", "2012_04", "2002_00", "2013_00", "2025_06", "2032_06", "2014_04", "2050_01", "2016_04", "2027_06", "2037_01"], "aesthetic_win_clean": ["2040_07", "2002_07", "2001_05", "2031_02", "2014_03", "2011_06", "2047_07", "2028_04", "2039_03", "2036_07", "2021_07", "2032_03", "2011_03"], "overall_loss": ["2017_03", "2048_06", "2044_07", "2049_00", "2012_02", "2035_04", "2012_05", "2040_04", "2008_02", "2015_05", "2036_05", "2027_04", "2049_03", "2013_04", "2021_02", "2028_00", "2011_01", "2050_04", "2030_02", "2006_04", "2006_07", "2047_04", "2004_05", "2012_04", "2004_01", "2002_00", "2013_00", "2025_06", "2032_06", "2014_04", "2050_01", "2016_04", "2027_06", "2037_01"]}

