# Presentation script and timed storyboard

Estimate: 145 spoken words per minute plus two seconds per slide transition. Actual rehearsal determines duration.
Target 10-11 minutes; recorded maximum 12 minutes. Stage headings and sources are not narration.

## 1. Naive substring search and KMP (0:00-0:34)

This project compares two ways to find a pattern inside a text. The problem sounds simple, but the algorithms treat repeated partial matches differently. Naive search starts again at each candidate. KMP keeps information about the pattern so it can reuse part of a failed match. The question is when that extra preparation pays for itself. I will show the important invariants, then the measured results, and finally a controlled example where counting comparisons gave an incomplete prediction.

Sources: Report sections 1-5; results/facts.json

## 2. The search contract (0:34-1:14)

Both algorithms receive exactly the same byte sequences and must return the smallest matching index. An empty pattern returns zero, and an absent pattern returns npos. These are byte positions, so Unicode character boundaries do not enter the definition. Embedded zero bytes also count as ordinary data. The example used throughout the explanation is text ABABABAC and pattern ABABAC. Its first match begins at index two. This contract matters because finding any occurrence, or finding every occurrence, would change when an algorithm can stop and how much work belongs in the comparison.

Sources: src/search.hpp; tests/search_tests.cpp

## 3. Naive search: every valid start (1:14-2:28)

Naive search considers every valid start from zero through n minus m. At each start it compares pattern bytes from the beginning. In this example, start zero matches ABABA, then the final C meets a B and fails. Start one fails immediately because A meets B. Start two matches all six bytes and returns two. The search makes thirteen equality tests in total. The correctness argument follows that order: every rejected start has an actual mismatch, and no earlier valid start remains when a full match returns. The important boundary is that m must not exceed n before subtracting unsigned sizes. Otherwise the candidate range can underflow. The empty pattern is also deliberate: its zero required comparisons succeed at start zero. For a worst case, take a text of only a bytes and a pattern of many a bytes followed by b. Every candidate repeats almost the whole pattern. That gives exactly n minus m plus one, multiplied by m, comparisons. The short code and the worst-case bound describe different strengths of this baseline.

Sources: src/naive.cpp; report section 1.2

## 4. KMP: the LPS table (2:28-3:38)

KMP first describes the pattern's own repetition. LPS means longest proper prefix that is also a suffix. For ABABAC, the table is zero, zero, one, two, three, zero. A proper prefix must be shorter than the whole prefix being considered. Look at ABABA, ending at pattern index four. Its first three bytes are ABA, and its last three bytes are also ABA, so the entry is three. Construction extends a known border when the next bytes agree. On a mismatch, it tries the border of that border. At the final C, a border length of three would require B. That fails. Falling back gives length one, which also requires B. That fails too. At length zero, C differs from A, so the final entry is zero. The key is to follow already established borders. A random shorter length is not necessarily a suffix and cannot safely describe a retained partial match. The table takes linear time and one size_t entry for each pattern byte.

Sources: Knuth, Morris and Pratt (1977), https://doi.org/10.1137/0206024; src/kmp.cpp

## 5. KMP fallback preserves a valid match (3:38-4:57)

During the search, matched tells us how many pattern-prefix bytes equal the text suffix immediately before i. That is the invariant. Here the first five bytes match. At text index five, B differs from pattern index five, C. The matched text ends in ABA, which is also a pattern prefix, so the table changes matched from five to three. The text index stays five. B now matches pattern index three, and the final A and C complete the occurrence at index two. The search uses nine equality tests, plus seven earlier tests to construct this pattern's table. This tiny example therefore does not promise a faster complete call. What matters is that fallback keeps a valid border and rules out starts that cannot succeed. Resetting matched to zero at the same text index can miss this occurrence. Moving the text index backward would lose the property that avoids repeated scans. For the linear bound, text position only advances, and each fallback reduces a prefix length built by earlier successful comparisons. That limits the total repeated comparisons even though one text byte can be compared more than once.

Sources: src/kmp.cpp; report sections 1.3-1.4

## 6. Predictions saved before timing (4:57-5:38)

The predictions were committed before the first performance pilot and remain unchanged. Naive might compete on random inputs because most candidates fail quickly. KMP should benefit when many candidates repeat a long partial match. A match at the beginning should make preprocessing relatively important because little text needs searching. There was no numerical crossover prediction and no confident winner for prose. These are hypotheses about the complete calls in this implementation. They do not assume that a linear worst-case bound wins every small example, or that every periodic text is difficult for naive search.

Sources: docs/predictions.md, commit c06dfc8

## 7. A controlled measurement (5:38-6:23)

The main study has three hundred and sixty-three validated instances. It varies text length, pattern length, alphabet, structure and match position. Each instance has nine timed batches, after warm-up and calibration. Both algorithms receive the same inputs, and the standard library checks actual first positions outside timing. The monotonic clock surrounds algorithm calls only. It excludes file loading, generation and printing. KMP builds and destroys its table on every call. Results are consumed, and optimized assembly confirmed repeated calls inside the batching loop. The plots summarise instance medians and show their interquartile spread. This separates repeated timing noise from differences between the three input instances.

Sources: bench/driver.cpp; scripts/experiment.py; results/main-2026-10-27/environment.json

## 8. Long partial matches reward KMP (6:23-7:19)

This plot holds text length at sixty-five thousand five hundred and thirty-six and increases the length of an absent near-match pattern. The naive curve rises because each candidate repeats a longer prefix. KMP remains close to a linear scan of the text. At pattern length five hundred and twelve, naive takes about eleven point two milliseconds while KMP takes about one hundred and five microseconds. That is approximately one hundred and seven times faster. The spread is small relative to this gap. This is an intentionally difficult input for naive search. On random alphabet-twenty-six text, the algorithms are much closer, with naive slightly faster in the measured large absent case. The prose windows also give overlapping spreads. The result supports a conditional choice, rather than declaring a universal winner.

Sources: results/summary.csv; results/tables.md; report figures 1-2

## 9. Comparison counts test the explanation (7:19-8:08)

The counters test the explanation about repeated work. On that repeated absent input, naive makes roughly thirty-three million comparisons. The exact formula is n minus m plus one, multiplied by m. KMP makes about one hundred and thirty-two thousand, including preprocessing. The analysis script checks those counts against independently derived formulas. This confirms that KMP removes repeated equality tests. But the comparison ratio is about two hundred and fifty-three, while the runtime ratio is only about one hundred and seven. Equality tests are not equally expensive complete steps. The code also updates indices, follows fallbacks and accesses the table. This difference motivated a separate experiment, with its own prediction recorded after the main study.

Sources: results/facts.json; scripts/analyse.py; docs/followup-prediction.md

## 10. Almost equal counts, different runtimes (8:08-9:20)

The follow-up moves one mismatching b through an otherwise all-a pattern. At index one, naive and KMP make almost equal numbers of equality tests. The new prediction was that their runtimes would be similar. Instead, naive takes about sixty-one microseconds and KMP about one hundred and eight. KMP is one point seven seven times slower, and the observed spreads are well separated. The exact counts are one hundred and thirty thousand and fifty for naive, and one hundred and thirty-two thousand and ninety-one for KMP. The difference is only about one point six percent. Looking at the source explains the limitation of the count: naive rejects each candidate on its second comparison, while KMP repeatedly fails at pattern index one, falls back to zero and compares the same text byte again. Those paths perform different surrounding work. This does not identify a cache or branch-prediction cause. It establishes that comparison count alone is an insufficient timing model, while still being a useful measure of the repeated work removed.

Sources: results/mismatch-summary.csv; docs/review.md; report section 5

## 11. Limits of the evidence (9:20-9:52)

The large adversarial result is clear, but the scope stays narrow. Measurements came from one Apple M1 Pro and one optimized compiler build. Three instances do not describe a broad population, and the prose windows come from the same repeated excerpt. Very fast calls also include a visible batching-overhead floor. Small percentage differences should therefore be treated cautiously. The experiments establish mechanisms and examples, while the complexity arguments provide guarantees beyond those examples.

Sources: report sections 3.3 and 6

## 12. The choice depends on the workload (9:52-10:23)

KMP gives predictable worst-case behaviour by keeping valid prefix information. Naive remains a useful baseline when candidates fail quickly or a match arrives immediately. The next question is how the balance changes when many texts share one pattern and its table can be reused. That would be a separate workload with a separate timing boundary. The code, raw measurements and regeneration scripts are available in the repository for checking these conclusions.

Sources: https://github.com/egoldman2/substring-search; report section 6

Total spoken words: 1449.
Estimated duration at 145 words/minute with transitions: 10:23. Rehearse aloud and trim if necessary.
