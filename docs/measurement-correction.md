# Executable freshness correction

27 October 2026, during final artifact verification. Inspecting the benchmark
executable with `strings` found no `batch checksum differs from oracle` message,
although the committed driver source contained that post-timing check. Source and
executable timestamps were both 20:45:32, so Make had accepted the stale binary.
The timed search loop was unchanged; results were still consumed and individual
calls checked before and after timing. Nevertheless, the executable did not
correspond exactly to the recorded source revision.

The original pilot, main and mismatch runs were superseded. The replacement runs were collected after a forced rebuild. The runner now
forces compilation, records source and executable SHA-256 hashes, and records the
working-tree status. The follow-up requires the exact same executable hash.
The figures use the verified replacement runs. Original predictions and the post-main follow-up
prediction remain unchanged; the earlier observations were already known before
replacement collection, which is verification rather than a new blind study.
