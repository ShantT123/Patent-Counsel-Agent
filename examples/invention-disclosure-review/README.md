# Disclosure review example

Provide the installable skill and [fictional input](inputs.md), then request the five reports. Compare against the [illustrative document-only fallback](worked-example.md). That example deliberately has no live research and must not be presented as a completed competitor landscape.

For a connected run, allow automatic generalized public queries, record inspected sources and dates, and replace the unverified search hypotheses with supported relationships where possible. Do not use internal labels as queries.

The worked output was manually authored to demonstrate format and uncertainty handling. The five cases in `evaluations/disclosure-review-cases.json` are proposed behavioral challenges; independent model runs and attorney scoring have not been performed. Structural checks cannot establish extraction recall, explanation accuracy, or research quality.


## Default HTML dashboard and portfolio mode

Run from the repository root:

```sh
python3 skills/invention-disclosure-review/scripts/render_dashboard.py examples/invention-disclosure-review/dashboard-input.json examples/invention-disclosure-review/dashboard.html
```

Open [dashboard.html](dashboard.html) locally. It is a self-contained responsive report with search, confidence/category/type filters, source navigation, expandable evidence, JSON download, and print/save-PDF. The [editable JSON](dashboard-input.json) contains a fictional grant and a fictional published application, with claim-mapped, description-only, and unreviewed technology mappings. These identifiers and claims do not correspond to real patents or rights. Neither this fixture nor its styling establishes extraction quality, claim interpretation, or legal coverage.

Install the entire skill folder, including its `scripts/` files. The renderer uses Python 3.10+ standard library only and embeds its CSS/JS, so the generated file needs no server or external assets. In patent/portfolio mode, the assistant creates the source-backed claim summaries and mappings before rendering; the renderer does not perform analysis.
