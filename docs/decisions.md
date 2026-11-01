# Decisions and checks

## 27 October 2026: implementation and timing

The original searches passed their existing tests before changes. The test harness
used `assert`, so `NDEBUG` could remove its checks. Tests now use explicit failures
and exercise both counted and uncounted entry points: 104,600 oracle/expected-answer
checks plus exact counter values, including a `-DNDEBUG` build and address/undefined
behaviour sanitizers. No incorrect search result was observed.

KMP now returns immediately when the pattern is longer than the text. This avoids
an unnecessary allocation; it is an implementation choice, not a claim that the
original answer was wrong. Counting is selected at compile time inside the same
algorithm bodies. Tests verify both instantiations against independent answers.

The generated corpus inputs passed checks for all 363 full-study instances before
any pilot. The binary CLI also passed zero-byte, high-byte, empty-pattern, absent,
invalid-algorithm and missing-file checks.

The pilot used six instances and three repetitions. Its batches ranged from 32 to
65,536 calls. Even the beginning-match case for m=32 reached approximately 1 ms
per batch, so the predeclared 1 ms target, 65,536 cap and nine main repetitions
were retained. Tiny m=1 workloads may reach the cap below the target; retain and
label those rows. No pilot result is pooled with the main study.

Optimized Apple Clang assembly of `batch_time` was inspected: an indirect call
(`blr x24`) remains inside its decrement-and-branch loop, between two clock reads.
The algorithm translation units are compiled separately, without LTO or pure
annotations. A consumed batch checksum is checked against the oracle after timing.
This supports repeated execution on this build. It does not prove every future
compiler/flag combination has identical behaviour.

Random m=1 searches only use a beginning match: a one-byte pattern drawn from the
same small alphabet cannot reliably be absent from a long random text. Repeated
and periodic seed variants change byte labels but retain structure. The prose
instances use related windows of one excerpt; they are not independent corpora.

Linux could not run locally: Docker is installed but its daemon is unavailable.
A portable CI build will supply Linux verification if the service can run it.
