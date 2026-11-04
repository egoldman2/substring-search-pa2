# Substring search comparison

A C++17 comparison of naive substring search and Knuth–Morris–Pratt (KMP). Both return the first matching byte index, `std::string_view::npos` if absent, and zero for an empty pattern. Binary inputs are supported.

## Deliverables

- [Final report](deliverables/Final%20report.pdf)
- [Individual reflection](deliverables/Reflection.pdf)
- [Results figures](deliverables/figures/)
- [Results tables](results/tables.md) and [raw measurements](results/)

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

The smoke-test output directory must be new. Raw measurements and environment details are in `results/`; predictions and measurement notes are in `docs/`. The verified main and follow-up measurements are included. See `results/README.md`.

Regenerate the figures and tables with `python3 -m pip install -r requirements.txt` followed by `python3 scripts/analyse.py`.
