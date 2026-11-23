# Patent Counsel Workflows

**Open-source AI skills for understanding inventions, reviewing patents and applications, and planning patent portfolios.**

Created by **Shant Tchakerian**. Version **0.3.0 — preview**.

**New: Invention Disclosure Review** turns an invention description, patent, published application, or portfolio into a searchable HTML dashboard. Learn unfamiliar terminology, explore related technologies and organizations, and see which technology mappings are supported by the reviewed claims.

| Skill | Use it to… |
| --- | --- |
| [Invention Disclosure Review](skills/invention-disclosure-review/SKILL.md) | Understand technical terms and concepts, classify patents and applications, and map portfolio technologies in an HTML dashboard |
| [Invention Intake](skills/invention-intake/SKILL.md) | Develop incomplete inventor materials into a source-linked disclosure, technical questions, and a filing-review packet |
| [Filing Review](skills/filing-review/SKILL.md) | Apply supplied business criteria and compare deterministic budget scenarios |
| [Portfolio Strategy](skills/portfolio-strategy/SKILL.md) | Map technology ownership, products, roadmap targets, and portfolio inventory |

Each skill is self-contained and can be installed separately.

## Try invention disclosure review

Built for technical patent counsel learning unfamiliar technologies. Give it an invention description and supporting materials, a single issued patent or published application, or a collection of portfolio documents.

### Five connected reports

| Report | What you get |
| --- | --- |
| **Glossary** | Plain-English explanations of technical terms, acronyms, internal names, and concepts described without a name, with their role in the invention |
| **Thesaurus** | Synonyms, broader and narrower concepts, related mechanisms, substitutes, and commonly confused terms, with differences made explicit |
| **Technology categorization** | Overarching and specific technology areas, alternatives, source-backed confidence assessments, and mappings to existing or proposed portfolio buckets |
| **Related fields** | Neighboring technologies that share problems, mechanisms, or constraints, with useful research directions |
| **Competitors, innovators, and organizations** | Relevant companies, research groups, and projects for the initial and related categories, with dated evidence and qualified roles |

The skill checks for your technology bucket list. If none is available, it asks for the list and continues with a proposed taxonomy for review. Public terminology and organization research runs automatically using generalized queries, subject to your restrictions and available host tools.

### HTML dashboard by default

The default deliverables are **`review.html` and `review.json`**. The dashboard opens with a short **plain-English executive summary** covering the idea, technology/portfolio fit, key findings, uncertainties, and next steps. Clickable citations appear beside summary statements and report findings, with links to the source register and public sources when available. A clickable glossary word cloud helps readers explore terms. The thesaurus labels each invention **Term** and its **Related terms**; related fields group each **Technology** with its **Related technologies**, explaining connections and differences. Word-cloud sizes use documented occurrence counts when complete and comparable, or equal weights otherwise. The dashboard also includes sidebar navigation, search, technology/confidence filters, glossary type filters, expandable evidence, source links, JSON download, and print/save-PDF support. The HTML embeds its styles and scripts, so it needs no web server or external assets.

Try the [fictional portfolio dashboard](examples/invention-disclosure-review/dashboard.html): download the HTML using GitHub's **Download raw file** control and open it in your browser. GitHub's file viewer displays the HTML source. The [editable example JSON](examples/invention-disclosure-review/dashboard-input.json) and [example guide](examples/invention-disclosure-review/README.md) explain the fictional records.

### Patents, applications, and portfolio mapping

For each document, the skill identifies the reviewed publication and claim version, summarizes independent claims and dependent additions, and maps technology categories using **claim-mapped**, **description-only**, **potential**, or **unreviewed** labels. Portfolio mode consolidates terminology and taxonomy while preserving document-specific evidence and differences between family-member claims.

Issued claims remain distinct from published or pending application claims. A technology topic or proposed claim mapping does not establish enforceable legal scope, infringement, or freedom to operate. Unknown prosecution status and missing claim versions remain explicit.

### Install and run

Install the **entire** [skills/invention-disclosure-review](skills/invention-disclosure-review) folder, including its `references/` and `scripts/` files, in your assistant's configured skills directory. In Codex, invoke `$invention-disclosure-review`. In another assistant, provide [SKILL.md](skills/invention-disclosure-review/SKILL.md), its referenced files, and your source materials.

For one invention or publication:

> Use $invention-disclosure-review on this invention disclosure, patent, or published application. Explain its terms and concepts, build the thesaurus, categorize its technologies, research related fields and organizations, and produce review.html and review.json with sources and confidence. Check for my technology buckets and propose a taxonomy if unavailable. For a patent or application, include the reviewed-claim technology map.

For a portfolio:

> Use $invention-disclosure-review on these portfolio documents. Produce a consolidated HTML dashboard with shared terminology, technology buckets, and a document-to-technology map. Separate issued and application claims, distinguish claim-mapped topics from description-only topics, and flag missing claim versions and uncertain status.

To render the supplied fictional example without an AI assistant, run from the repository root:

```sh
python3 skills/invention-disclosure-review/scripts/render_dashboard.py examples/invention-disclosure-review/dashboard-input.json review.html
```

The renderer requires Python 3.10+ and no third-party libraries or API keys. It presents the supplied JSON; it does not extract patent text, conduct research, or infer claim mappings. Live analysis requires host document-reading and research tools. Keep real matter documents and generated reports outside this public repository. See the [report contract](skills/invention-disclosure-review/references/report-contract.md), [HTML guidance](skills/invention-disclosure-review/references/html-dashboard.md), and [patent/portfolio workflow](skills/invention-disclosure-review/references/patent-portfolio.md). Host installation and independent substantive model performance remain unvalidated.

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

- Four independently usable skills with evidence and uncertainty rules.
- A five-report invention/patent review skill with an offline HTML dashboard, JSON output, and explicit patent/application/portfolio modes.
- Templates for disclosures and filing-review packets.
- A complete fictional input/output example with a review commentary.
- Eighteen proposed behavioral challenge cases across the four skills and a human evaluation rubric; recorded model runs remain outstanding.
- A configurable filing-review skill and documented JSON input format.
- A standard-library calculator using decimal arithmetic, with quarterly cost breakouts and explicit scenarios.
- Forty-three executable tests covering renderer safety, evidence preservation, budgets, scoring, organization/portfolio integrity, import, refresh behavior, and module compatibility.
- A portfolio-strategy skill, JSON/CSV examples, and a source-linked strategy-review template.
- A standard-library package checker; no API key or paid service is required to inspect the project.

## Scope

This release supports **invention disclosure review, patent and application technology review, portfolio mapping and strategy, pre-filing invention development, and counsel review**. The intake skill can use optional strategy and glossary context. The filing-review skill applies supplied company criteria and assumptions; its calculator requires explicit policy, budget, and scenario inputs. Missing ratings remain unknown, and missing corporate evidence limits the corresponding review.

It does not conduct an exhaustive prior-art search, determine inventorship, give a legal clearance opinion, manage deadlines, draft a complete patent application, or file anything. It does not supply a confidentiality or privilege guarantee. Outputs need review by appropriately qualified counsel before professional reliance.

## Core design choices

**Evidence stays visible.** Technical assertions use stable source locators. Facts, inventor statements, inferences, proposed alternatives, and unknowns remain distinguishable.

**Technical depth precedes scoring.** The workflow asks what changes in the system, how the mechanism works, which steps are essential, and what supports the claimed advantage.

**Business assessment stays separate from legal judgment.** A strategic score is not a patentability determination. An unknown is not a zero. Similar abstracts identify review candidates, not established claim coverage.

**No hidden integrations.** The skill has no bundled external connectors, telemetry, or network code. The AI assistant hosting it may process data remotely; its privacy, retention, tools, and sharing settings still matter.

## Repository map

| Path | Purpose |
| --- | --- |
| `skills/invention-disclosure-review/` | Five-report invention, patent, application, and portfolio review skill with HTML renderer and claim-aware mapping guidance |
| `examples/invention-disclosure-review/` | Fictional sources, worked report, editable portfolio JSON, and self-contained HTML dashboard |
| `skills/invention-intake/` | Installable intake skill, supporting references, and Codex UI metadata |
| `skills/filing-review/` | Installable filing-review skill, guidance, and standalone calculator |
| `skills/portfolio-strategy/` | Installable strategy skill, organization/portfolio analyzer, CSV import, and handoff context |
| `templates/` | Optional editable Markdown output forms |
| `examples/synthetic-invention/` | Fictional source materials, worked output, and reviewer commentary |
| `examples/filing-review/` | Editable fictional JSON, source notes, actual calculator output, and review packet |
| `examples/portfolio-strategy/` | Equivalent JSON/CSV examples, generated output, sources, and strategy review |
| `tests/` | Executable renderer, calculator, inventory, import, and handoff tests |
| `evaluations/` | Challenge cases, scoring rubric, and evaluation status |
| `scripts/check_package.py` | Checks package integrity and worked-example source references |

Each installable skill is self-contained. Repository-level templates and evaluations are optional companions.

## Validation

Run `python3 scripts/check_package.py` from the repository root. This checks packaging, example references, metadata shape, and reproducible example calculations, **not legal correctness or model performance**. Run the test command above for the financial, inventory, import, and input-validation checks. See [evaluation status](evaluations/STATUS.md) for what has and has not been measured.

## Contributing and roadmap

See [publishing instructions](PUBLISHING.md) to upload this package. See [CONTRIBUTING.md](CONTRIBUTING.md) for useful contributions and [ROADMAP.md](ROADMAP.md) for proposed next steps. Synthetic edge cases, documented model failures, and improvements grounded in patent practice are particularly welcome.

## License and attribution

MIT licensed; see [LICENSE](LICENSE). Attribution does not imply endorsement. The fictional examples are intentionally created for this project and do not represent an actual company, invention, patentability conclusion, or client matter.
