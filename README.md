# Patent Counsel Workflows

**Open-source AI workflows for developing invention disclosures and preparing patent filing reviews.**

Created by **Shant Tchakerian**. Version **0.3.0 — preview**.

The **Invention Intake** skill helps patent counsel turn incomplete inventor materials into a source-linked disclosure, prioritized follow-up questions, technical diagrams, and a filing-review packet. It preserves unresolved questions instead of filling them with invented technical facts.

The **Filing Review** skill adds configurable business scoring, source-retaining portfolio candidates, and deterministic budget scenarios. All three skills are self-contained and can be installed separately.

The new **Portfolio Strategy** skill maps technology ownership, products, roadmap targets, portfolio records, and disclosure pipeline. Its offline analyzer preserves proposed mappings and source dates, summarizes inventory, and flags strategy-review needs without inferring legal coverage.

## Try portfolio strategy

Requires Python 3.10+; no third-party libraries or API keys.

```sh
python3 skills/portfolio-strategy/scripts/strategy.py examples/portfolio-strategy/input.json
python3 skills/portfolio-strategy/scripts/strategy.py examples/portfolio-strategy/csv-input.json --records-csv examples/portfolio-strategy/records.csv
```

Read the [fictional strategy review](examples/portfolio-strategy/strategy-review.md), [editable JSON](examples/portfolio-strategy/input.json), [CSV records](examples/portfolio-strategy/records.csv), and [input reference](skills/portfolio-strategy/references/input-format.md). The commands produce identical reports. Portfolio records may contain internal/public identifiers, family labels, jurisdictions, dated status, claim locators, and confirmed/proposed bucket mappings.

In an AI assistant, provide `skills/portfolio-strategy/SKILL.md`, its references, and the available organization/roadmap/portfolio sources. In Codex, install the entire `skills/portfolio-strategy` directory and invoke `$portfolio-strategy`; host installation has not been independently validated.

Example request:

> Follow Portfolio Strategy. Use the fictional source notes and input to map teams, people, products, and technology buckets. Run the analyzer. Explain inventory signals, missing ownership, stale status evidence, recorded counsel assessments, and the source scope. Prepare a strategy review and show the context available for filing review. Do not infer claim coverage from counts.

The output's `filing_review_context` supplies compatible strategy and portfolio sections for the filing-review module. Review IDs, dates, and scope before merging; it does not supply a complete input, business scores, costs, or filing decisions.

## Try the filing-review module

Requires Python 3.10+; no third-party libraries or API keys.

```sh
python3 skills/filing-review/scripts/review.py examples/filing-review/input.json
python3 -m unittest discover -s tests -v
python3 scripts/check_package.py
```

Read the [fictional review packet](examples/filing-review/review-packet.md), [editable input](examples/filing-review/input.json), and [input format](skills/filing-review/references/input-format.md). The calculator runs offline and prints JSON without modifying the input.

To use the workflow in an AI assistant, provide `skills/filing-review/SKILL.md`, its referenced guidance, and your source materials. In Codex, install the entire `skills/filing-review` directory in your configured skills directory and invoke `$filing-review`. It has no dependency on the intake skill. Host installation behavior has not been independently validated.

Example request:

> Follow Filing Review. Use the attached fictional input and source notes. Explain missing ratings, strategy mappings, and candidate portfolio overlaps. Run the calculator and compare the two supplied budget scenarios. Keep policy approval, legal review, and filing authorization explicit.

## Try invention intake in five minutes

1. Download and extract this repository.
2. Open an AI assistant that supports reading local Markdown files. Give it `skills/invention-intake/SKILL.md` and the referenced files in that skill's `references/` folder. Tool support and installation methods vary by assistant.
3. Attach `examples/synthetic-invention/inputs.md` and use this prompt:

> Follow the Invention Intake skill. Use only the attached fictional sources. Prepare a disclosure, prioritized follow-up questions, proposed diagrams, and a filing-review packet. Preserve source references, contradictions, and unknowns. Do not search externally. Produce Markdown in this chat.

4. Compare the response with `examples/synthetic-invention/worked-example.md` and score it using `evaluations/rubric.md`.

For Codex, copy the **entire** `skills/invention-intake` folder into your configured skills directory (commonly `~/.codex/skills/`), make it available in your session, and invoke `$invention-intake`. If it is not discovered, use the file-based prompt above. This preview has been structurally checked; cross-assistant installation and model behavior have not been independently validated.

## What you get

- A reusable skill with evidence and uncertainty rules.
- Templates for disclosures and filing-review packets.
- A complete fictional input/output example with a review commentary.
- Eleven proposed behavioral challenge cases across the three skills and a human evaluation rubric; recorded model runs remain outstanding.
- A configurable filing-review skill and documented JSON input format.
- A standard-library calculator using decimal arithmetic, with quarterly cost breakouts and explicit scenarios.
- Thirty-five executable tests covering budgets, scoring, organization/portfolio integrity, import, refresh behavior, and module compatibility.
- A portfolio-strategy skill, JSON/CSV examples, and a source-linked strategy-review template.
- A standard-library package checker; no API key or paid service is required to inspect the project.

## Scope

This release supports **portfolio strategy, pre-filing invention development, and counsel review**. The intake skill can use optional strategy and glossary context. The filing-review skill applies supplied company criteria and assumptions; its calculator requires explicit policy, budget, and scenario inputs. Missing ratings remain unknown, and missing corporate evidence limits the corresponding review.

It does not conduct an exhaustive prior-art search, determine inventorship, give a legal clearance opinion, manage deadlines, draft a complete patent application, or file anything. It does not supply a confidentiality or privilege guarantee. Outputs need review by appropriately qualified counsel before professional reliance.

## Core design choices

**Evidence stays visible.** Technical assertions use stable source locators. Facts, inventor statements, inferences, proposed alternatives, and unknowns remain distinguishable.

**Technical depth precedes scoring.** The workflow asks what changes in the system, how the mechanism works, which steps are essential, and what supports the claimed advantage.

**Business assessment stays separate from legal judgment.** A strategic score is not a patentability determination. An unknown is not a zero. Similar abstracts identify review candidates, not established claim coverage.

**No hidden integrations.** The skill has no bundled external connectors, telemetry, or network code. The AI assistant hosting it may process data remotely; its privacy, retention, tools, and sharing settings still matter.

## Repository map

| Path | Purpose |
| --- | --- |
| `skills/invention-intake/` | Installable intake skill, supporting references, and Codex UI metadata |
| `skills/filing-review/` | Installable filing-review skill, guidance, and standalone calculator |
| `skills/portfolio-strategy/` | Installable strategy skill, organization/portfolio analyzer, CSV import, and handoff context |
| `templates/` | Optional editable Markdown output forms |
| `examples/synthetic-invention/` | Fictional source materials, worked output, and reviewer commentary |
| `examples/filing-review/` | Editable fictional JSON, source notes, actual calculator output, and review packet |
| `examples/portfolio-strategy/` | Equivalent JSON/CSV examples, generated output, sources, and strategy review |
| `tests/` | Executable calculator, inventory, import, and handoff tests |
| `evaluations/` | Challenge cases, scoring rubric, and evaluation status |
| `scripts/check_package.py` | Checks package integrity and worked-example source references |

Each installable skill is self-contained. Repository-level templates and evaluations are optional companions.

## Validation

Run `python3 scripts/check_package.py` from the repository root. This checks packaging, example references, metadata shape, and reproducible example calculations, **not legal correctness or model performance**. Run the test command above for the financial, inventory, import, and input-validation checks. See [evaluation status](evaluations/STATUS.md) for what has and has not been measured.

## Contributing and roadmap

See [publishing instructions](PUBLISHING.md) to upload this package. See [CONTRIBUTING.md](CONTRIBUTING.md) for useful contributions and [ROADMAP.md](ROADMAP.md) for proposed next steps. Synthetic edge cases, documented model failures, and improvements grounded in patent practice are particularly welcome.

## License and attribution

MIT licensed; see [LICENSE](LICENSE). Attribution does not imply endorsement. The fictional examples are intentionally created for this project and do not represent an actual company, invention, patentability conclusion, or client matter.
