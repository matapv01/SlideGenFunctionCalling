# Does the reward gain show up for people? (round 2, final DAPO vs base)

`scripts/reward_vs_human.py` recomputes the round-4 training reward from the scored components and splits the
DAPO - rival gap by component (RESULTS.md). Exploratory.

1. **The whole test-set reward gain over the base model is validity.** Mean training reward 4.889 vs 4.735 (+0.154);
   fewer invalid slides contributes +0.170 (110%): base 17 invalid of 337, DAPO 8. Pairs with an invalid side are not
   shown to people (decided automatically: DAPO valid / base broken 11, the reverse 2, both broken 6). On the slides
   people saw, the reward gap is slightly negative (sum -3.15 over 291 pairs): reward and humans both say "about equal".
   So "the reward says better, people say equal" is mostly a difference in what was measured, not a contradiction.
2. **Within shown pairs the reward gap tracks the human overall verdict, weakly and monotonically:** win rate 0.449
   (gap < -0.3), 0.479, 0.502 (|gap| < 0.05), 0.526, 0.585 (gap >= 0.3).
3. **Per component:** layout/defect terms register with people (dom favours DAPO: layout 0.587 vs 0.444 when it favours
   the base; a visible defect only on the base slide: layout 0.72, overall 0.84, n=8). Key-point coverage registers
   (coverage 0.539 vs 0.377). **The ViT aesthetic term does not** (human aesthetic win rate 0.544 whichever side the ViT
   favours), and over the test set it rates DAPO slightly worse (-0.021) while people rate DAPO prettier (0.525).
