# Correctness and reproducibility review

The valid input contract is two byte sequences, including embedded zero and high
bytes. Both searches return the first matching byte offset, `npos` if absent, and
zero for an empty pattern. No mutation is allowed. The test suite uses hand-set
answers, 16,129 exhaustive pairs over {a,b} through length six, and 10,000 seeded
cases checked against the standard library. Both counted and ordinary functions
run every case. These tests supply evidence, not a proof for arbitrary inputs.

Adversarial checks considered: unsigned subtraction when m>n, an empty-pattern
access in KMP, a mismatch after a long border chain, matches at the final valid
start, overlapping occurrences, high bytes under signed `char`, and disabled
assertions. The m>n and empty guards protect indexing. Equality works on identical
byte representations regardless of `char` signedness. Explicit test failures
remain active under `NDEBUG`. The loops inspect only valid candidate starts.

For independent human review, use this handoff: read `src/naive.cpp`, `src/kmp.cpp`
and their contract above; find a valid byte input yielding an incorrect first
index, out-of-bounds access or nontermination. Supply exact bytes, expected index
and a failing trace. Also inspect the timed loop for removed/hoisted calls and
the generator for incorrectly labelled first occurrences. A fresh independent
reviewer has not yet checked this project; the existing oracle and sanitizer
checks are documented rather than represented as that review.

## Controlled follow-up audit

All 18 mismatch-position instances are absent and have recorded hashes. At
position 1, naive performs 2*(65,536-512+1)=130,050 comparisons. KMP performs
131,071 search comparisons and 1,020 preprocessing comparisons, totalling 132,091.
The table agrees with these independently derived values. The naive search needs
only two comparisons per candidate before advancing. KMP repeatedly mismatches
at pattern index 1, falls back to index 0, and compares the same text byte again.
The state updates and data accesses differ despite similar equality-test counts.
These facts explain why equality-test counts are an incomplete cost model. They
do not identify a processor-level cause for the measured time difference.

The follow-up's `source_dirty: true` records untracked generated main-study
summaries and figures at launch. Its algorithm, driver and follow-up source are
unchanged from recorded revision `170e0cf`. This is an honest repository-state
qualification, not evidence of an uncommitted algorithm variant.
