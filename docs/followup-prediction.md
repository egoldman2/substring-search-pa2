# Controlled follow-up, recorded after the main study

27 October 2026. The main results have been seen. They show that byte-comparison
ratios can be much larger than runtime ratios, and that binary random inputs give
KMP a modest runtime benefit despite a larger reduction in comparisons.
This is a new prediction, not part of the preserved original record.

Question: when both algorithms perform almost the same number of comparisons on
a controlled repetitive input, will they run at similar speeds?

Fix n=65,536, m=512, text=a^n, and put the sole b in an otherwise all-a pattern at
positions 0, 1, 7, 31, 127 and 511 (zero-based). Every pattern is absent.
Naive should use (n-m+1)*(position+1) comparisons. When position=1, both methods
should make approximately 2n comparisons, including KMP preprocessing.
The working prediction is similar runtimes in that equal-work case. A consistent
separation beyond the observed spreads would challenge comparison count as a
sufficient runtime explanation, even though it remains a useful work measure.

Use the existing driver, nine repetitions and three byte-label variants per
position. Preserve the same complete-search timing boundary. No hardware cause
will be claimed from these timings alone.

Measurement note: the main run below was superseded after a stale executable was discovered. Use the verified replacement data for final analysis.
