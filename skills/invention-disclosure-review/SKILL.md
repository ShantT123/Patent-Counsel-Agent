---
name: invention-disclosure-review
description: Review invention disclosures, patents, published applications, and patent portfolios for technical counsel. Explain terminology, map technologies and reviewed claims, research related fields and organizations, and deliver a searchable offline HTML dashboard.
---

# Invention Disclosure Review

Help a technical patent attorney learn an unfamiliar technology without losing the inventors' actual meaning. Produce five connected, source-linked reports: glossary, thesaurus, technology categorization, related fields, and competitors/innovators/leaders. Support both individual documents and consolidated patent portfolios. The default output is a polished, searchable offline HTML dashboard with matching JSON. This skill is independently usable; intake and portfolio strategy are optional consumers.

## Start and inputs

Read [workflow and research rules](references/workflow.md) and [report contract](references/report-contract.md). Read [patent and portfolio review](references/patent-portfolio.md) for patents, applications, or multiple records, and [HTML dashboard](references/html-dashboard.md) for the default deliverable. The [report template](references/report-template.md) is an optional prose fallback when explicitly requested.

Accept a description and documents, including issued patents, published applications, portfolio inventories, claim versions, PDF, DOCX, slides, diagrams, technical notes, and transcripts when host tools can read them. Inventory every file and record unreadable pages, missing attachments, OCR limitations, and uninspected figures. Analyze accessible portions without implying complete coverage. Ask for indispensable missing material only when it blocks interpretation.

Check the user's supplied files and authorized connected portfolio context for an existing technology bucket list. Preserve bucket IDs, definitions, hierarchy, source, and version. If none is available, ask whether the user has a list; continue independent analysis with a provisional taxonomy for review. Never silently replace an existing taxonomy. If a list arrives later, retain the technical categories and revise their bucket mappings. An unavailable list is not evidence that no list exists.

Public research using generalized queries is the default and is authorized by invoking this skill unless the user restricts research. Do not repeatedly request permission for that default. Inspect available research capabilities first; if absent or blocked, complete document-grounded analysis and label external verification incomplete. Do not invent research or citations.

## Workflow

1. Inventory sources with stable locators. Extract terms, acronyms, internal names, and unnamed concepts across prose, figures, captions, and tables. Perform a second pass for omissions, compound concepts, ambiguous acronyms, and conflicting meanings. Separate distinct senses instead of merging them because wording matches.
2. Explain each entry in plain English, then explain its role in the disclosed mechanism. Preserve internal names; assign explicitly provisional descriptive labels to unnamed concepts. Distinguish disclosure statements, outside background, interpretation, and unknowns. A familiar-looking phrase is insufficient evidence that it is a term of art.
3. Research public vocabulary using the generalized-query rules. Build a thesaurus for every entry, labeling exact alias, broader, narrower, related mechanism, functional substitute, cross-field terminology, or commonly confused term. If no defensible relationship is found, say so. Do not force a synonym or assert technical equivalence from similar outcomes.
4. Classify by overarching field (if supported), specific mechanism, application domain, and supporting technology. Permit multiple primary fields and explicit alternatives. Explain confidence and contrary evidence. Map to supplied buckets or proposed buckets; flag gaps rather than forcing a fit. Treat optional CPC/IPC mappings as candidates and verify definitions in an official current source before calling them verified.
5. For every identified technology category, identify related fields using shared problems, mechanisms, constraints, substitutes, or transferable techniques. Provide a concrete research bridge and search vocabulary. Keep relationship confidence separate from search usefulness; do not infer legal analogous-art status.
6. Research organizations for every initial and related category, including alternative categories with their uncertainty preserved. Distinguish commercial competitor, research innovator, patent-active organization, open-source contributor, standards body, and evidenced leader. Record category coverage, including searches with no supported candidates. Avoid branding-only lists and unsupported leadership rankings.
7. For patents and applications, identify the exact document and claim version, summarize independent claims and dependent additions, and distinguish claim-mapped technologies from description-only, potential, and unreviewed mappings. For portfolios, consolidate terms and taxonomy while retaining document-specific evidence and different family-member claims. Follow the patent/portfolio reference; never infer legal scope from topic matches.
8. Reconcile all five reports, source links, IDs, ambiguities, and coverage. End with prioritized inventor questions and limitations. Revisit dependent definitions, classifications, relationships, and organization matches after attorney corrections, preserving a revision note.

## Confidence and boundaries

Use high / medium / low / unresolved with an evidence-based explanation. High requires direct or corroborated support and no material unresolved conflict; medium has plausible support with gaps; low relies on indirect evidence or competing interpretations; unresolved lacks adequate evidence. Assess term meaning, relationship, category fit, portfolio mapping, and organization relevance separately. These are qualitative assessments, not calibrated probabilities; overlapping categories do not sum to 100%.

Never characterize an internal term as publicly established without supporting public usage. Never infer ordinary skill, conventionality, novelty, inventiveness, infringement, claim coverage, or patentability from a glossary or category. Search leads and representative patent publications are not an exhaustive prior-art search. A publication's relevance does not establish its legal prior-art status. Publication and priority dates must remain distinct.

## Deliverables and handoff

Return `review.html` and `review.json`, plus a short chat summary with artifact links, unless the user explicitly requests another format. Use `scripts/render_dashboard.py` and follow the HTML dashboard reference. Include all five reports, orientation, source/research log, coverage statement, proposed taxonomy or existing-bucket mapping, and unresolved questions. For patents/applications add document and claim-version summaries; for portfolios add the claim-aware document-to-technology map. Follow the contract without adding unverified facts to satisfy fields. The dashboard presents technical coverage and source-supported claim mappings; it does not automatically establish enforceable legal coverage.

For invention intake, supply terminology IDs, mechanisms, source locators, and unresolved inventor questions. For portfolio strategy, supply category IDs and proposed/confirmed bucket mappings with provenance. These are handoff records, not a promise that existing scripts accept this JSON directly. Do not modify corporate taxonomy or portfolio records automatically.

Keep real matter materials and generated matter reports outside the reusable public skill repository. Repository examples must be fictional or explicitly authorized for publication. The host provides document extraction and research; this package bundles no external service, API credential, telemetry, or document parser.
