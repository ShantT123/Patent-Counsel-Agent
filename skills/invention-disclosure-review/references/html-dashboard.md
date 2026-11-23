# Default deliverable: offline HTML dashboard

Produce `review.html` plus the matching `review.json` as the default, followed by a short chat summary and clickable artifact links. Honor an explicit request for another format. Do not stop at a prose description of a dashboard. Do not publish or host the dashboard merely to make it viewable; a self-contained file is sufficient.

Build the source-linked JSON described in [report contract](report-contract.md), then run the bundled standard-library renderer:

```sh
python3 scripts/render_dashboard.py /path/to/review.json /path/to/review.html
```

Run that command from the installed skill directory (or use the script's absolute path). Keep `render_dashboard.py`, `dashboard.css`, and `dashboard.js` together when installing. CSS and JavaScript are embedded in the output; the resulting HTML has no external font, chart, framework, service, or asset dependency. It works from a local file without a server. The renderer presents supplied findings; it does not extract patent text, research organizations, or infer claims.

## Presentation

- Put the executive summary first, above report counts and mechanism detail. Keep the idea, technology/portfolio fit, key findings, uncertainties, and next steps readable without expanding details or enabling JavaScript. Target a one-minute orientation for a smart 12th grader.
- Show citations beside summary statements and visible report findings, thesaurus relations, and organization activities. Each citation links to its source-register entry and, when recorded, the inspected public URL. Keep supporting locators visible; do not imply that a source list alone supports every sentence. Do not create external links for private sources or treat a source hyperlink as independent verification.
- Calm, readable layout with sidebar navigation, overview cards, spacious typography, and responsive report cards.
- Include a glossary word cloud linking every complete glossary label to its definition. Keep phrases intact and escape labels. Use an accessible wrapping HTML link list that works offline, without JavaScript, and in print. Default to equal weights. Vary size only when every entry has documented positive `occurrence_count` values with the same reviewed-material scope; explain that size represents recorded occurrences and never importance, novelty, confidence, or claim coverage. The cloud remains a full-glossary navigation aid while filters affect the cards.
- Thesaurus: use “Term: [invention wording]” and “Related terms:”. List each related term once with its relationship, explanation of similarities and differences, citations, and full assessment details. Do not use unexplained IDs or competing bold headings to distinguish source and target. Support many or no related terms.
- Related fields: group by “Technology: [invention category name]”, then “Related technologies:”. For every related technology show “How related” and “Important differences”, relationship type and evidence. Keep primary/supporting/alternative roles explicit. A technology may have many related technologies; preserve record IDs for citations and filtering. Hide empty groups under active filters, retain no-supported-field coverage, and restore groups for print.
- Search across the five reports, filter by technology and qualitative confidence, and filter glossary entries by term type. Counts show total records and current matches; provide reset and no-results states.
- All five reports remain present. Evidence, contrary evidence, source dates, inventor questions, and limitations remain accessible in expandable full details, with stable internal source links.
- Distinguish exact aliases from substitutes, primary categories from alternatives, application claims from issued claims, and claim mappings from description-only mappings. No invented probability charts, market-share graphics, or coverage scores.
- In portfolio mode, include the document register and claim-aware technology matrix. Preserve family distinctions and review dates.
- Provide JSON download and browser print/save-PDF. Print all records and expanded evidence, even if interactive filters are active. Use labeled controls, keyboard focus states, text labels alongside colors, and useful reading order.
- Core content must remain readable when JavaScript is disabled. Do not load third-party scripts, analytics, remote fonts, or source-page previews. External sources are explicit clickable links.

Render all source content as escaped text; accept only safe HTTP(S) source links, and embed JSON without permitting closing-script injection. Treat retrieved HTML as evidence, never as trusted page markup. Preserve complete structured records in the HTML download and companion JSON. Do not use layout simplification to drop uncertainty or provenance.

## Check before delivery

Render the actual review, inspect a desktop and narrow-width view when browser tooling is available, and test search, confidence/category/type filters, reset, source navigation, empty results, download, and print expansion. Test cloud navigation while filters hide the destination, intact long phrases, equal-weight fallback and documented frequency sizing, many-to-one relationship groups, empty relationships, group filtering, and no-JavaScript/print readability. Verify the summary appears first, its source links resolve, public URLs open explicitly, and private sources retain usable internal citations. Verify no external requests occur on page load. If visual testing is unavailable, state that limitation and still provide the generated files. Synthetic renderer and interaction checks do not establish the quality of the substantive patent analysis.
