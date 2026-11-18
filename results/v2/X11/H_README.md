# X11 confirmatory analyses (H1d, H5c, H5c-b2)

Offline, no model calls: tools_lease/x11_h_analysis.py, exactly as registered (H1d d488d333, H5c 7a67f064, H5c-b2 b9fe2c9e).
Selection data: X5 (math500_q15_7, 64 plans x 300 eval problems) and X7 (code_c15_7, 32 plans x 178 eval problems).
Scoring data: X11 held-out problems (200 each), sha256-checked against VM-A before the run. Run 2026-11-18 after X11
finished. Verdicts: H1d HELD; H5c NOT HELD ((a) halving meets both conditions in both settings; (b) racing meets the regret
condition but uses 41.1% / 51.2% of the exhaustive evaluations, above 40%); H5c-b2 HELD. "Within tau" is one-sided
(regret - exhaustive regret <= tau); every difference is also within tau in absolute value. H1d code_c15_7 k = 2 UV regret is
exactly 0.020 (4 of 200 problems), on the boundary of the <= 0.02 condition. Details: H1d/h1d.json, H5c/h5c.json.
