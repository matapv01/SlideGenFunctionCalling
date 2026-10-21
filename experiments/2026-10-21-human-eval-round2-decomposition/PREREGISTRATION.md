# Pre-registration: decomposing the round-2 human judgements (DAPO vs base, best-of-4, Gemini 3.6 Flash)

Written 2026-10-21 before the confirmation data exists. Commit time of this file is the cutoff.

## Data split
- **Exploration (already seen):** every rating in the export of 2026-10-21 02:51 UTC (A1: 480 pairs, A2: 199 pairs).
  The hypotheses below were formed after looking at aggregate numbers from this export.
- **Confirmation (not yet seen):** all A3 ratings, and A2 ratings with `updated_at` after this file's commit time.
  Only these ratings test the hypotheses. Exploration ratings are reported separately and never pooled into the test.

## Unit of analysis
Pair-level vote from DAPO's side (+1 DAPO better, 0 tie, -1 worse), averaged over the confirmation raters of the pair;
sign of the mean is the pair verdict. Win rate = mean of (vote + 1) / 2; 95% CI by deck-level bootstrap (2,000 rounds).
"Differing pair" = the two slides' rendered visible text is not identical (fixed before looking at confirmation data).

## Hypotheses (DAPO vs base unless stated)
- **H1 (aesthetic beyond defects).** On differing pairs where neither slide has a measured visible defect and both are
  valid, DAPO's aesthetic win rate is above 0.5 (CI lower bound > 0.5).
- **H2 (coverage loss comes from shortening).** Among differing pairs, the coverage verdict is negatively associated with
  how much shorter DAPO is: pairs where DAPO has < 0.85x the base's visible words have a lower DAPO coverage win rate than
  pairs with >= 0.85x (difference of win rates < 0, bootstrap CI excludes 0).
- **H3 (overall follows coverage).** Among pairs where DAPO loses coverage, DAPO loses overall in more than half.
- **H4 (differing pairs).** On differing pairs, |overall win rate - 0.5| is larger than on all pairs (reported, no threshold).
- **H5 (Gemini).** DAPO vs Gemini 3.6 Flash: layout win rate > 0.5 (CI lower bound > 0.5).

## Fixed analysis choices
- Visible defect = any of low_contrast, text_cutoff, slide_boundary, bbox_collision, markup_leak, tiny_text, plate_spill,
  panel_spill (scripts/dev_eval_table.py VISIBLE); scores from slidegen_data/testset_v2/scored_5880.
- Word count = whitespace tokens of `visible_text`.
- Script: scripts/decompose_round2.py (exploration and confirmation run the same code with `--split`).
- No other subsets will be reported as confirmatory. Anything else is labelled exploratory.
