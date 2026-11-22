# Patents, applications, and portfolio review

## Explicit modes

Support a disclosure, a published patent application, an issued patent, or a portfolio containing any combination. Infer the mode from the supplied documents; ask only if document identity or the requested scope is unclear. The task may be understanding a single patent or mapping an entire portfolio; do not require an inventor interview before reviewing available publications.

For a single document, produce the five reports plus a claim-aware document summary. For multiple documents, produce a consolidated dashboard with shared technology buckets, a document register, document-to-technology mapping, and links back to each document's terms and evidence. Reuse a term ID only when meanings agree; retain distinct senses and document-specific uses. Use stable, globally unique IDs across the batch. Do not merge unrelated documents just because the title is similar.

## Identify the exact document and version

Record document ID, publication/application/grant identifiers, document type, jurisdiction, title, applicant/assignee as sourced, filing/publication/grant dates, supplied version and retrieval date. Keep each date distinct. Record family/priority relationships only with evidence. Family members can have different claims: do not substitute a parent's claims or treat a family as a single scope of protection.

Distinguish issued claims, published application claims, pending amended claims supplied from the record, and canceled or superseded versions. State when only the publication was reviewed and current prosecution or legal status was not checked. Do not label an application granted or a patent live based only on publication kind or an old source. Provide source dates for status; unknown status stays unknown.

## Understand the technology, then inspect the claims

Read abstract, specification, available figures, and claims. Identify central mechanisms versus illustrative hardware, broad optional embodiments, and background. Record figure and extraction gaps. A catalog description is useful for triage but cannot support claim mappings by itself.

For each independent claim, summarize the actual required combination with claim number and exact document/version. Track dependent-claim additions separately. Compare the claims against the specification: distinguish subject matter described but not identified in reviewed claims, features expressly recited, and uncertain mappings. Do not silently repair omissions or insert a generative-AI, server, algorithm, or other step because the specification describes it. Record ambiguous language as a review issue.

Map each document/category pair using one of:

- `claim_mapped`: identified language in reviewed claims supports the proposed technology mapping; include claim locators, relevant limitations, confidence, and version. This is a technical mapping, not a conclusion about legal scope.
- `description_only`: category appears in the specification but has not been identified in the reviewed claims; state what claims were checked.
- `potential`: plausible relationship needing claim text or interpretation.
- `unreviewed`: insufficient material to assess it.

Application claim mappings describe proposed claim subject matter, not issued rights. Even issued-claim mappings do not establish enforceability, literal infringement, equivalents, or freedom to operate. Record any counsel-confirmed legal assessment separately with its author/date/scope; do not generate it from keywords, classification codes, title similarity, or counts.

## Portfolio outputs

Provide a shared taxonomy and document-by-technology map. Show mapping basis and document type together. Add claim summaries, source locators, and uncertainty on drill-down. Separate counts of documents and families if family evidence is available; do not equate either count with protection strength. Flag technology topics with only descriptive support, application-only mappings, missing claims, uncertain status, conflicting terminology, and possible overlap for attorney review. Absence in the supplied inventory means no mapping found in that inventory, not an established protection gap.

Preserve all five reports in portfolio mode: glossary and thesaurus can be consolidated, categories can overlap, related-field and organization evidence can be reused with explicit category links. Portfolio analysis does not require repeating identical public research per document. Keep real portfolio inventories, claim analyses, and generated dashboards outside the public skill repository unless publication is explicitly authorized.
