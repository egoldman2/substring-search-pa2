# Substring search comparison

A C++17 comparison of naive substring search and Knuth–Morris–Pratt (KMP). Both return the first matching byte index, `std::string_view::npos` if absent, and zero for an empty pattern. Binary inputs are supported.

## Build and test

```sh
make all
make test
python3 tests/workflow_test.py
```

Run a search with `./build/search naive TEXT_FILE PATTERN_FILE` or replace `naive` with `kmp`.

## Experiments

```sh
python3 scripts/experiment.py --smoke --instances 1 --repetitions 3 --output build/smoke
```

The smoke-test output directory must be new. Raw measurements and environment details are in `results/`; predictions and measurement notes are in `docs/`. The verified main measurements are included; the verified follow-up is still pending. See `results/README.md`.

The analysis script requires the verified replacement measurements, which have not yet been published.
