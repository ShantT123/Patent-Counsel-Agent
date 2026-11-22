# Report contract (version 1)

Use the same IDs across readable reports and JSON. Null means unknown; an empty array means none recorded, with a coverage explanation where relevant. Never put a fabricated source or value into a required field. This is an interchange contract, not input for existing portfolio calculators.

## JSON envelope

Required keys: `schema_version` ("1"), `review_id`, `as_of`, `scope`, `sources`, `research_log`, `glossary`, `thesaurus`, `technology_categories`, `taxonomy`, `related_fields`, `organizations`, `organization_coverage`, `questions`, `limitations`, `handoff`.

- `scope`: supplied materials, inspected materials, exclusions, extraction limits, research status, geography, and time scope.
- `sources`: ID, title, kind (disclosure/public), locator or URL, publication/update date if available, actual accessed date for inspected public sources, and inspection status.
- `research_log`: query, purpose, date, tool, inspected source IDs, status, and gaps. Do not include confidential original wording in query logs intended for sharing.
- Every evidence reference: source ID, locator, short supporting excerpt, and what it supports. Every confidence object: level (high/medium/low/unresolved), rationale, and missing or contrary evidence.

## Executive summary (required for newly authored reports)

Add `executive_summary` with five nonempty arrays: `overview`, `technology_fit`, `key_findings`, `uncertainties`, and `next_steps`. Each array contains objects with `text` (plain text) and `evidence` (an array of `{source_id, locator}` references to the source register). Example:

```json
{"text": "The disclosed tube routes incoming air through a treatment region; its effectiveness is unknown.", "evidence": [{"source_id": "S-001", "locator": "Description, paragraph 1"}]}
```

Aim for 150–250 words total, readable by a smart 12th grader. Explain essential jargon. Summarize the idea, main category and confidence with its reason, proposed/existing portfolio mapping, representative findings or research leads, major uncertainties, and one to three prioritized next steps. Use fewer findings rather than a dense list. A confidence label without the reason is insufficient. For patents/portfolios, preserve claim-versus-description distinctions, claim-version limitations, and source-supported status or unknowns. Do not imply efficacy, novelty, leadership, or legal coverage from a topic match. Label recommendations as recommendations; they may have empty evidence arrays. Unknowns and factual findings should cite the material or scope record establishing the limitation. Do not fabricate sources to populate a field.

Each factual statement needs nearby supporting references. Split statements with different evidence into separate items. Full evidence records in the detailed reports retain supporting excerpts and confidence rationales. The renderer accepts older version-1 files without this optional extension, but clearly labels its orientation-only fallback as lacking an authored executive summary; it does not generate or infer a substantive summary.

## Five reports

### Glossary (`G-001`…)

Each entry: ID, original wording, occurrences/evidence, sense, type (term_of_art/internal_name/acronym/unnamed_concept/uncertain), provisional descriptive label if needed, plain-English definition, role in this invention, example/analogy and limits where useful, evidence status (disclosed/externally_supported/inferred/unknown), meaning confidence, and inventor question if unresolved. Include a public citation for a verified term-of-art designation. Do not conflate general definition with the invention-specific meaning.

### Thesaurus

One record per glossary ID, including entries where no supported match was found. Each relation: target wording or glossary ID, relation type (exact_alias/broader/narrower/related_mechanism/functional_substitute/cross_field/confused_with), explanation of similarities AND material differences, applicable context, evidence, confidence, suggested generalized search phrase. Identify unverified search candidates as such. Label an empty relations list with the reason.

### Technology categories (`T-001`…)

Each: ID, name, role (overarching/primary_mechanism/application/supporting/alternative), parent IDs, description, glossary IDs, supporting evidence, fit confidence, contrary evidence, alternative category IDs, and missing facts. Explicitly state whether an overarching field is justified. Do not force all mechanisms under a broad label such as AI. Candidate CPC/IPC fields: scheme, code, official definition URL, version/date where available, verification status, and mapping rationale; omit unsupported codes.

`taxonomy`: status (existing/proposed/awaiting_list), source/version, buckets (ID, name, definition, parent ID), mappings (category ID, bucket ID, proposed/confirmed, evidence, confidence), gaps, and review questions. Distinguish technical category confidence from mapping confidence.

### Related fields (`R-001`…)

Each: ID, parent category ID, name, relationship type (shared_problem/shared_mechanism/shared_constraint/substitute/transferable_technique), explanation, source and glossary links, differences, relationship confidence, search usefulness with reason, generalized search phrases. Every category must have related fields or an explicit no-supported-fields coverage note. Do not recursively expand without a bound; default one hop from initial categories.

### Organizations (`O-001`…)

Each entity: ID, name, entity type, and category matches. Each match identifies T- or R-ID, role (commercial_competitor/research_innovator/patent_active/open_source/standards/evidenced_leader/technology_relevant), concrete activity, dated supporting sources, relevance confidence, and limitations. Representative products, papers, projects, and patent publications must have inspected supporting references. Leadership claims need a stated criterion and comparative evidence. Label market overlap unknown when client context is missing.

`organization_coverage`: one record for every T- and R-ID, researched status, matched organization IDs, query references, and remaining gaps, including zero-result categories. Weak/alternative categories retain that qualification in the organization report.

## Closing records

`questions`: prioritized question, affected IDs, missing fact, and why an answer matters.
`limitations`: unresolved interpretations, missing extraction/research, conflicts, and scope limits.
`handoff`: terminology/mechanism IDs and questions for intake; category-to-bucket mappings for portfolio strategy, each with provenance and proposed/confirmed status. Add revision notes when correcting a prior review.

Verify all references resolve, every glossary entry has a thesaurus record, every category has related-field coverage, and every initial/related category has organization coverage. Completeness is relative to inspected materials; do not claim all possible concepts or competitors have been discovered.


## HTML presentation (default)

Render the version-1 JSON as `review.html` using `scripts/render_dashboard.py`, following [HTML dashboard guidance](html-dashboard.md). The complete structured records remain in expandable details and the JSON download. Use `executive_summary` for the top quick-read section and visible citations for detailed entries and relations. Public citations offer both an internal source-register link and a direct safe HTTP(S) link when recorded. Private/disclosure sources retain locators and internal links without exposing local paths as public links. Optional `orientation` is additional plain-English mechanism context; optional `document` includes title and document metadata; optional `claim_observation` highlights a source-supported issue. These optional fields preserve compatibility with existing disclosure reports.

## Patent/application and portfolio extension (version-1 optional fields)

Set optional `review_mode` to `disclosure`, `patent`, `application`, or `portfolio`. For patents/applications, `document` records document type, identifiers, jurisdiction, supplied version, relevant dates, and source-backed identity. Include a `portfolio` object for a claim-aware single-document or multi-document map:

- `records` (array): each has unique `document_id`, document type (`issued_patent`, `published_application`, `pending_claim_version`, or `disclosure`), identifiers, title, jurisdiction, family ID/relationship if supported, sourced status/as-of date or unknown, reviewed claim version, claim summaries (independent combinations and dependent additions with source locators), extraction limitations, and source IDs.
- `category_mappings` (array): document ID, category ID, `basis` (`claim_mapped`, `description_only`, `potential`, `unreviewed`), `claim_locators` (required and nonempty for claim-mapped entries), relevant claim limitations, supporting source references, assessment confidence, review date/version, and scope limitations. Include proposed versus counsel-confirmed assessment status when relevant; never infer confirmation.
- `gaps` (array): missing documents, missing claim versions, application-only or description-only topic mappings, unknown/stale status, tentative overlap, and unanswered questions. An inventory absence does not establish a legal protection gap.

Document identifiers and source locators must resolve to the supplied record/version. Do not create portfolio mappings from keywords alone. Keep issued and application claims explicit, and family claims separate. Follow [patent/portfolio guidance](patent-portfolio.md). Unknowns stay unknown; no numeric legal-coverage score is generated.
