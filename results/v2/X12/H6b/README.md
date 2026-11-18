# H6b (L2-X12, registered 5cc73094)

Verdict: **NOT HELD**

## math_q15_7
- threshold 0.1897 (cheapest eval cost with eval acc >= fixed - 0.01); eval: router 0.78 vs fixed 0.79, cost ratio 0.9313, upgrades 0.8775
- held-out X2: router acc 0.7983 vs fixed 0.8025 (acc_ok True); cost ratio 0.9242 (<= 0.70: False); upgrade share 0.8623
- X12 final answer matches stored all_small: eval 0.615, X2 0.6579; all_small acc X12 vs stored: eval [0.5075, 0.49], X2 [0.5146, 0.5035]

## math_granite
- threshold 0.4113 (cheapest eval cost with eval acc >= fixed - 0.01); eval: router 0.65 vs fixed 0.66, cost ratio 0.776, upgrades 0.6625
- held-out X2: router acc 0.6773 vs fixed 0.6912 (acc_ok False); cost ratio 0.7864 (<= 0.70: False); upgrade share 0.6732
- X12 final answer matches stored all_small: eval 0.7, X2 0.6912; all_small acc X12 vs stored: eval [0.4625, 0.4725], X2 [0.5313, 0.5229]

Context: identical prompts (planner prompt tokens equal on 400/400 eval problems); X4 vs P2 all_small on the same 400
problems also matched only 67.75% of final answers (49/400 correctness flips) - run-to-run nondeterminism of greedy
decoding, amplified over the 6-agent chain.
