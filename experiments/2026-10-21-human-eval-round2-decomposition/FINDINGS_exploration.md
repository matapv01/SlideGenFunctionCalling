# Exploration findings (A1 + A2 before the cutoff; NOT confirmatory)

Numbers from `scripts/decompose_round2.py --split exploration` (RESULTS_exploration.md) plus the checks below.
Everything here generates hypotheses; only the pre-registered tests on the confirmation split count.

## DAPO vs base (268 pairs, 176 with different visible text)
1. **Overall is decided by two separate effects that cancel.** Every pair DAPO wins on aesthetic it also wins (16) or
   ties (1) overall; 24 of 28 pairs it loses on coverage it loses overall. Aesthetic wins and coverage losses fall on
   different slides (only 1 pair has both), so this is not "summarising makes the same slide prettier but thinner".
2. **Aesthetic wins come from palette choice, on content that is otherwise the same.** In 13/17 aesthetic wins DAPO's
   slide is brighter (mean luminance +0.087; ties +0.006; all 3 losses darker, −0.049). Over all 318 test slides DAPO is
   brighter in 36 and darker in 15. Images: teal-on-white tiles instead of dark tiles (2036_04, 2047_02), light card instead of
   dark red (2014_06, 2016_05). The ViT reward does not see this: it agrees with the human aesthetic verdict in 6/17 wins.
   9 of the wins are on pairs where neither slide has a measured defect (aesthetic win rate on those 0.518 [0.500, 0.536]).
3. **Coverage losses are real content loss, mostly from compressing card text into labels.** Losing pairs: DAPO has 0.78x
   the base's words, keypoint −0.172, numeric_fact −0.049, more proper names dropped (0.50 vs 0.12 per pair on ties).
   Images: 2050_04, 2012_04, 2027_04, 2006_03 (details cut to short labels). Some verdicts look wrong: in 2039_02 and 2043_02
   DAPO shows more source facts than the base and still loses (A2 only; A1 tie).
4. **Short is not automatically worse.** Pairs DAPO wins on coverage are also shorter (0.84x). Coverage win rate by length:
   < 0.70x 0.433, 0.70–0.85 0.450, 0.85–1.00 0.481, ≥ 1.00 0.508 (difference short − long −0.046 [−0.117, +0.022]).
5. **Raters differ in how often they tie.** A1 ties 87% on overall and 95% on coverage; A2 62% and 50%. On the 118 pairs
   both rated, whenever both took a side they agreed (coverage 8/8, overall 18/25).

## DAPO vs base best-of-4 and vs Gemini 3.6 Flash
- Same structure: overall follows aesthetic wins and coverage losses. Shortening costs more against these rivals
  (coverage short − long: best-of-4 −0.077 [−0.133, −0.011]; Gemini −0.173 [−0.263, −0.085]).
- Gemini: DAPO wins faithful (8 vs 1) and layout (13 vs 4); when DAPO is at least as long as Gemini it wins overall 0.600.

## Implications (to be confirmed)
- The paper-worthy positive result is narrower than "DAPO is prettier": DAPO learned lighter, higher-contrast palettes that
  people prefer, which the ViT reward does not measure (likely driven by the contrast/layout terms; untested).
- Reframing the coverage criterion is not supported: the question already asks for key ideas, not completeness, and the
  coverage losses coincide with lost facts and names. The fix is a reward that keeps the most important ideas.
