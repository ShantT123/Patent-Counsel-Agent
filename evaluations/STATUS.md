# Evaluation status — 0.3.0 preview

- The worked example was manually authored for this package; it is not an independent model execution.
- Five behavioral challenge cases are supplied. They have not yet been run as a recorded benchmark.
- No independent attorney review, cross-model comparison, time-saving study, or legal validation is claimed.
- `scripts/check_package.py` verifies expected files, local Markdown links, case IDs, and source references in the worked example. It does not assess model behavior or legal correctness.
- Skill metadata can also be checked using the Codex skill-creator validator when available. That validator is not bundled or required for ordinary use.

The next meaningful validation step is a fresh-session model run followed by a patent practitioner's recorded review using the rubric. Add actual results here only after execution.

## Earlier package preparation checks (0.1.0)

The offline package checker passed during preparation, including source-locator and local-link checks. Skill metadata was inspected for required fields, naming, description length, unfinished scaffolding, and the invocation prompt. The bundled skill-creator Python validator could not run because its PyYAML dependency was unavailable in this environment; no successful run of that validator is claimed.

## Filing-review release (0.2.0)

- Fifteen automated calculator tests passed on Python 3.14 during package preparation, including a table of 20 invalid-input mutations. Python 3.10+ is the supported syntax target; other interpreters were not exercised in this preparation.
- Tests cover formula results, threshold boundary handling, unknown ratings, weight scaling, family counts, candidate limits, period boundaries, reserve rounding, over-budget detection, baseline-only scenarios, rejection of invalid/duplicate input, CLI output, and reproducibility.
- `examples/filing-review/expected-output.json` is actual calculator output. Its human-readable review packet was authored for the repository and is not a model benchmark result.
- `filing-review-cases.json` adds three proposed human/model evaluations. These have not been executed as recorded behavioral runs. The earlier five intake cases also remain unexecuted.
- The expanded offline checker verifies required files, local links, metadata shape, source locators, and saved calculation reproducibility. It does not verify the truth of cited sources or replace a general YAML validator.
- No attorney validation, legal correctness, model accuracy percentage, or time-saving claim is made.

## Portfolio-strategy release (0.3.0)

- Twenty additional automated tests passed on Python 3.14 during preparation (35 total across the repository). Tests include 20 invalid-input mutations for the strategy analyzer in addition to the existing filing-review mutations.
- Tested organization preservation/cycle rejection, family and jurisdiction counts, proposed mappings, disclosure stages, inventory signals, assessment/status refresh boundaries, unknowns, duplicate identifiers, JSON/CSV equivalence, accidental-replacement prevention, and the filing-review handoff.
- `examples/portfolio-strategy/expected-output.json` is generated analyzer output. The accompanying strategy review is manually authored. The fictional counsel assessments are illustrative input records, not independent legal validation.
- Three proposed strategy behavioral cases bring the total to eleven. No recorded model evaluation run or independent attorney validation is claimed.
- The expanded package checker checks equivalent JSON/CSV reports and source-locator existence in the strategy example; source existence does not prove that the source supports an assertion.

## Invention disclosure review

Five proposed challenge cases are in `disclosure-review-cases.json`. The Lantern worked example is manually authored and document-only; it does not demonstrate live public research. Independent model runs, attorney scoring, extraction recall, confidence calibration, research coverage, and cross-host installation remain unmeasured. Package checks validate required files, case structure, metadata, links, and example source locators only.

## HTML dashboard and patent/portfolio extension

Seven disclosure-review behavioral cases are now defined, including two new patent/portfolio challenges. The dashboard fixture is manually authored and entirely fictional. Eight renderer tests check data preservation, links, unsafe content handling, offline assets, claim-locator requirements, input preservation, and empty reports. Browser interaction smoke checks are performed separately on the fictional dashboard and the local published-application review; they test presentation, not substantive claim interpretation. Independent blinded evaluation of patent analysis, current legal status, and portfolio mapping remains outstanding.
