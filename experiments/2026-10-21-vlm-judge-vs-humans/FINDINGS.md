# Can a VLM judge stand in for the human annotators? (Qwen2.5-VL-32B-Instruct-AWQ, zero-shot)

Setup: the VLM sees what annotators saw (source text, two blind slide images) and answers the same six questions in
Vietnamese (`scripts/vlm_pairwise_judge.py`); each pair is judged in both A/B orders and the votes averaged.
Served with vLLM 0.15.0 on one RTX 5880 (GPU1). Human ratings: round 1 final export, round 2 export of 2026-10-21
04:46 UTC (A1 480, A2 278, A3 101). Analysis: `scripts/analyze_vlm_judge.py` (RESULTS_round1.md, RESULTS_round2.md).
Exploratory; nothing here was pre-registered.

## Agreement with the human pair verdict (same side, pairs where both took a side)

| Criterion | VLM r1 | VLM r2 | Automatic metric Δ r1 / r2 | Human vs human r1 / r2 |
|---|---|---|---|---|
| aesthetic | 0.44 (37/84) | 0.60 (30/50) | ViT 0.64 / 0.53 | 0.91 / 0.82 |
| overall | 0.67 (130/193) | 0.55 (62/112) | reward 0.70 / 0.64 | 0.81 / 0.73 |
| coverage | 0.79 | 0.72 | keypoint n/a / 0.79 | 0.86 / 0.92 |
| layout | 0.84 | 0.67 | dom 0.85 / 0.90 | 0.96 / 1.00 (n=7) |
| language | 0.98 | 1.00 | 1.00 / 1.00 | 0.97 / 1.00 |

The VLM is no better than the cheap metrics on any criterion, and on aesthetic it is at or below chance while two
humans agree 82-91% of the time.

## Why: the VLM uses two shortcuts that run against human taste
1. **Longer = more faithful and complete.** Picks the slide with more words on faithful 84% / 92% and coverage
   85% / 93% (humans: faithful 48% / 78%, coverage 65% / 78%).
2. **Darker, denser palettes = prettier.** On aesthetic it picks the shorter slide (VLM 25% / 18% pick the longer;
   humans 39% / 46%) and the darker one: humans pick the brighter slide 70% / 84%, the VLM 43% / 34%.
   Images (slidegen_data/annotation/vlm_judge/aesthetic_disagreements_r2.png, kept out of the public repo while round 2 is still being rated): humans prefer a white thank-you slide over dark red, light panels over dark
   navy panels; the VLM prefers the opposite.
3. **Position bias.** Same verdict in both orders only 48-57% on layout, aesthetic, overall; it favours the first image
   on layout/overall and the second on aesthetic. Single-order judging would be worse (forward-only overall 0.54-0.60).

Consequences for DAPO win rates: the VLM says DAPO loses to the base model overall (round 2: 0.42 [0.40, 0.45]) and on
faithful (0.37) where humans see parity (0.50, 0.50); it would have told us the opposite story from the annotators.

## For the paper
- Supports the benchmark framing: off-the-shelf VLM judges do not reproduce human slide preferences, and their errors
  are systematic (length, palette), so they would be exploitable as RL rewards.
- Human brightness preference shows up in both rounds and both judges disagree with it: neither the ViT reward nor the
  VLM captures what DAPO picked up.
- Not yet checked: larger or newer VLMs, prompting with a rubric/examples, or a VLM fine-tuned on the 1,929 pairs.
