#!/usr/bin/env python3
"""Render an existing review as a standalone offline dashboard. No analysis or network calls."""
import argparse
import hashlib
import html
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
ARRAYS = ('sources', 'research_log', 'glossary', 'thesaurus', 'technology_categories',
          'related_fields', 'organizations', 'organization_coverage', 'questions', 'limitations')
REQUIRED = ('schema_version', 'review_id', 'as_of', 'scope', 'taxonomy', 'handoff') + ARRAYS
SUMMARY_FIELDS = (('overview', 'The idea'), ('technology_fit', 'Technology & portfolio fit'),
                  ('key_findings', 'Key findings'), ('uncertainties', 'What remains uncertain'),
                  ('next_steps', 'Next steps'))
LEVELS = {'high', 'medium', 'low', 'unresolved'}


def escape(value):
    return html.escape(str(value), quote=True)


def label(value):
    return str(value).replace('_', ' ').strip().capitalize()


def safe_url(value):
    """Source text cannot introduce executable or local file URLs."""
    try:
        url = urlsplit(str(value))
        if url.scheme.lower() in ('https', 'http') and url.netloc and not url.username:
            return str(value)
    except ValueError:
        pass
    return None


def validate(data):
    if not isinstance(data, dict):
        raise ValueError('Review must be a JSON object')
    missing = [k for k in REQUIRED if k not in data]
    if missing:
        raise ValueError('Missing review fields: ' + ', '.join(missing))
    if data['schema_version'] != '1':
        raise ValueError('Unsupported schema_version; expected "1"')
    for key in ARRAYS:
        if not isinstance(data[key], list):
            raise ValueError(key + ' must be an array')
    for key in ('scope', 'taxonomy', 'handoff'):
        if not isinstance(data[key], dict):
            raise ValueError(key + ' must be an object')
    for key in ('sources', 'glossary', 'technology_categories', 'related_fields', 'organizations'):
        ids = [x.get('id') if isinstance(x, dict) else None for x in data[key]]
        if not all(isinstance(x, str) and x for x in ids) or len(set(ids)) != len(ids):
            raise ValueError(key + ' requires nonempty, unique string IDs')
    if 'executive_summary' in data:
        summary = data['executive_summary']
        if not isinstance(summary, dict):
            raise ValueError('executive_summary must be an object')
        source_ids = {s['id'] for s in data['sources']}
        for field, _ in SUMMARY_FIELDS:
            items = summary.get(field)
            if not isinstance(items, list) or not items:
                raise ValueError('executive_summary.' + field + ' requires a nonempty array')
            for item in items:
                if not isinstance(item, dict) or not isinstance(item.get('text'), str) or not item['text'].strip():
                    raise ValueError('Summary items require nonempty text')
                if not isinstance(item.get('evidence'), list):
                    raise ValueError('Summary items require an evidence array; use [] for an unsupported recommendation')
                for ref in item['evidence']:
                    if not isinstance(ref, dict) or ref.get('source_id') not in source_ids or not ref.get('locator'):
                        raise ValueError('Summary evidence requires a known source ID and locator')
    if 'portfolio' in data:
        portfolio = data['portfolio']
        if not isinstance(portfolio, dict):
            raise ValueError('portfolio must be an object')
        for key in ('records', 'category_mappings', 'gaps'):
            if key not in portfolio or not isinstance(portfolio[key], list):
                raise ValueError('portfolio.' + key + ' must be an array')
        docs = {r['document_id'] for r in portfolio['records']}
        if len(docs) != len(portfolio['records']):
            raise ValueError('Portfolio document IDs must be unique')
        categories = {c['id'] for c in data['technology_categories']}
        for mapping in portfolio['category_mappings']:
            if mapping.get('document_id') not in docs or mapping.get('category_id') not in categories:
                raise ValueError('Portfolio mapping has an unknown document or category ID')
            if mapping.get('basis') not in ('claim_mapped', 'description_only', 'potential', 'unreviewed'):
                raise ValueError('Portfolio mapping requires an explicit basis')
            if mapping['basis'] == 'claim_mapped' and not mapping.get('claim_locators'):
                raise ValueError('Claim-mapped categories require claim locators')
    return data


class Dashboard:
    def __init__(self, data):
        self.data = validate(data)
        self.counter = 0
        self.anchors = {}
        for collection in ('sources', 'glossary', 'technology_categories', 'related_fields', 'organizations'):
            for item in data[collection]:
                self.counter += 1
                self.anchors[item['id']] = 'record-' + str(self.counter)

    def confidence(self, obj):
        level = obj.get('level', 'unresolved') if isinstance(obj, dict) else str(obj)
        css = level if level in LEVELS else 'unresolved'
        return '<span class="badge ' + css + '">' + escape(label(level)) + '</span>'

    def value(self, obj):
        """Retain all supplied fields, escaping text and generating only safe links."""
        if obj is None:
            return '<span class="muted">Not provided</span>'
        if isinstance(obj, dict):
            badge = self.confidence(obj) if 'level' in obj else ''
            return badge + '<dl>' + ''.join('<div><dt>' + escape(label(k)) + '</dt><dd>' + self.value(v) + '</dd></div>' for k, v in obj.items()) + '</dl>'
        if isinstance(obj, list):
            if not obj:
                return '<span class="muted">None recorded</span>'
            return '<ul>' + ''.join('<li>' + self.value(v) + '</li>' for v in obj) + '</ul>'
        text = str(obj)
        if text in self.anchors:
            return '<a href="#' + self.anchors[text] + '">' + escape(text) + '</a>'
        url = safe_url(text)
        if url:
            return '<a href="' + escape(url) + '" target="_blank" rel="noopener noreferrer">' + escape(urlsplit(url).netloc + urlsplit(url).path) + '</a>'
        return escape(text)

    def citations(self, record, caption='Sources cited here'):
        # Only explicit source-reference fields create citations; prose is never parsed as markup.
        refs = []
        def collect(value):
            if isinstance(value, dict):
                if isinstance(value.get('source_id'), str):
                    refs.append((value['source_id'], str(value.get('locator') or '')))
                for key, child in value.items():
                    if key in ('source_ids', 'supporting_source_ids') and isinstance(child, list):
                        refs.extend((sid, '') for sid in child if isinstance(sid, str))
                    else:
                        collect(child)
            elif isinstance(value, list):
                for child in value:
                    collect(child)
        collect(record)
        refs = list(dict.fromkeys(refs))
        if not refs:
            return ''
        sources = {s['id']: s for s in self.data['sources']}
        links = []
        for sid, locator in refs:
            source = sources.get(sid)
            if source is None:
                links.append(escape(sid) + ' (unresolved source)')
                continue
            title = source.get('title', sid)
            text = sid + (' · ' + locator if locator else '')
            link = '<a href="#' + self.anchors[sid] + '" title="' + escape(title) + '">' + escape(text) + '</a>'
            url = safe_url(source.get('url')) or safe_url(source.get('locator'))
            if url:
                link += ' <a href="' + escape(url) + '" target="_blank" rel="noopener noreferrer" aria-label="' + escape('Open source: ' + title) + '">Open source</a>'
            links.append('<span>' + link + '</span>')
        return '<div class="citations"><strong>' + escape(caption) + ':</strong> ' + ' · '.join(links) + '</div>'

    def executive_summary(self):
        summary = self.data.get('executive_summary')
        result = '<section id="executive-summary" class="executive-summary card"><span class="eyebrow">Start here · Quick read</span><h2>Executive summary</h2>'
        if summary is None:
            return result + '<p class="muted">This older report has no authored executive summary. Its supplied orientation follows; consult the detailed findings for evidence and uncertainties.</p>' + self.value(self.data.get('orientation', 'No orientation supplied.')) + '</section>'
        result += '<div class="summary-grid">'
        for field, title in SUMMARY_FIELDS:
            result += '<div class="summary-block"><h3>' + title + '</h3>'
            for item in summary[field]:
                result += '<p>' + escape(item['text']) + '</p>' + self.citations(item)
            result += '</div>'
        return result + '</div><p class="muted summary-note">A quick orientation to this review. Source links support the nearby statements; recommendations are identified in the text. Full evidence and qualifications remain below.</p><a href="#technology_categories">Explore technologies</a> · <a href="#questions">Review questions</a> · <a href="#evidence">Source register</a></section>'

    def details(self, record):
        return '<details><summary>Full details and evidence</summary>' + self.value(record) + '</details>'

    def cats(self, record, collection):
        if collection == 'technology_categories':
            return [record['id']]
        if collection == 'related_fields':
            return [record.get('parent_category_id')]
        if collection == 'organizations':
            matched = [m.get('category_id') for m in record.get('category_matches', [])]
            return matched + [r.get('parent_category_id') for r in self.data['related_fields'] if r['id'] in matched]
        gid = record.get('glossary_id', record.get('id'))
        return [c['id'] for c in self.data['technology_categories'] if gid in c.get('glossary_ids', [])]

    def card(self, record, collection):
        rid = record.get('id', record.get('glossary_id', ''))
        title = record.get('original_wording', record.get('name', rid))
        levels = []
        def collect(value):
            if isinstance(value, dict):
                if value.get('level') in LEVELS:
                    levels.append(value['level'])
                for child in value.values():
                    collect(child)
            elif isinstance(value, list):
                for child in value:
                    collect(child)
        # Confidence filtering uses this report's assessment, not confidence buried in cited records.
        if collection == 'glossary':
            collect(record.get('meaning_confidence', {}))
        elif collection == 'technology_categories':
            collect(record.get('fit_confidence', {}))
        elif collection == 'related_fields':
            collect(record.get('relationship_confidence', {}))
        elif collection == 'organizations':
            for match in record.get('category_matches', []):
                collect(match.get('relevance_confidence', {}))
        else:
            for relation in record.get('relations', []):
                collect(relation.get('confidence', {}))
        if not levels:
            levels = ['unresolved']
        anchor = self.anchors.get(rid) if collection != 'thesaurus' else None
        attr = (' id="' + anchor + '"') if anchor else ''
        text = json.dumps(record, ensure_ascii=False).lower()
        result = '<article class="entry card"' + attr + ' data-search="' + escape(text) + '" data-levels="' + escape(' '.join(set(levels))) + '" data-categories="' + escape(' '.join(str(c) for c in self.cats(record, collection) if c)) + '" data-type="' + escape(record.get('type', '')) + '">'
        result += '<div class="card-top"><span class="eyebrow">' + escape(rid) + '</span>' + ''.join(self.confidence(x) for x in sorted(set(levels))) + '</div><h3>' + escape(title) + '</h3>'
        if collection == 'glossary':
            result += '<span class="pill">' + escape(label(record.get('type', 'uncertain'))) + '</span><p>' + escape(record.get('plain_english_definition', 'Definition not supplied.')) + '</p><p class="muted">' + escape(record.get('role_in_invention', '')) + '</p>'
        elif collection == 'thesaurus':
            g = next((g for g in self.data['glossary'] if g['id'] == rid), {})
            result += '<p class="muted">' + escape(g.get('original_wording', '')) + '</p>'
            for relation in record.get('relations', []):
                result += '<div class="relation"><span class="pill">' + escape(label(relation.get('relation_type', 'related'))) + '</span><h4>' + escape(relation.get('target_wording', relation.get('target_glossary_id', 'Related concept'))) + '</h4><p>' + escape(relation.get('similarities_and_differences', relation.get('explanation', 'See full details.'))) + '</p>' + self.citations(relation) + '</div>'
        elif collection == 'technology_categories':
            result += '<span class="pill">' + escape(label(record.get('role', 'unspecified'))) + '</span><p>' + escape(record.get('description', '')) + '</p>'
        elif collection == 'related_fields':
            result += '<p class="muted">Connected to ' + self.value(record.get('parent_category_id')) + '</p><p>' + escape(record.get('explanation', '')) + '</p><p><b>Difference:</b> ' + escape(record.get('differences', 'Not supplied')) + '</p>'
        else:
            result += '<p class="muted">' + escape(record.get('entity_type', 'Organization')) + '</p>'
            for match in record.get('category_matches', []):
                result += '<div class="relation"><span class="pill">' + escape(label(match.get('role', 'technology_relevant'))) + '</span> ' + self.value(match.get('category_id')) + '<p>' + escape(match.get('concrete_activity', 'Activity not supplied')) + '</p><p class="muted">' + escape(match.get('limitations', '')) + '</p>' + self.citations(match) + '</div>'
        if collection not in ('thesaurus', 'organizations'):
            result += self.citations(record, 'Sources cited in this entry')
        return result + self.details(record) + '</article>'

    def section(self, key, title, subtitle):
        records = self.data[key]
        body = ''.join(self.card(record, key) for record in records)
        return '<section id="' + key + '" class="collection"><div class="section-heading"><div><span class="eyebrow">Review report</span><h2>' + title + '</h2><p class="muted">' + subtitle + '</p></div><span class="count" aria-live="polite">' + str(len(records)) + ' entries</span></div><p class="empty" hidden>No entries match the current filters.</p><div class="cards">' + body + '</div></section>'

    def portfolio(self):
        portfolio = self.data.get('portfolio')
        if portfolio is None:
            return ''
        result = '<section id="portfolio"><div class="section-heading"><div><span class="eyebrow">Claim-aware inventory</span><h2>Portfolio map</h2></div></div><p class="callout">A technology described in a document is different from a technology mapped to reviewed claims. Issued and application claims remain distinct. Neither a topic match nor a claim mapping establishes enforceable scope or infringement.</p>'
        result += '<div class="table-wrap"><table><caption>Document-to-technology mappings</caption><thead><tr><th>Document</th><th>Technology</th><th>Mapping basis</th><th>Claims and limits</th></tr></thead><tbody>'
        for mapping in portfolio['category_mappings']:
            record = next(r for r in portfolio['records'] if r['document_id'] == mapping['document_id'])
            result += '<tr><td>' + escape(mapping['document_id']) + '<br><span class="pill">' + escape(label(record.get('document_type', 'unknown document type'))) + '</span></td><td>' + self.value(mapping['category_id']) + '</td><td><span class="pill">' + escape(label(mapping['basis'])) + '</span></td><td>' + self.value(mapping.get('claim_locators')) + self.details(mapping) + '</td></tr>'
        result += '</tbody></table></div><h3>Document records</h3>'
        result += ''.join('<article class="card"><h3>' + escape(r['document_id']) + '</h3>' + self.value(r) + '</article>' for r in portfolio['records'])
        return result + '<h3>Gaps and review needs</h3>' + self.value(portfolio['gaps']) + self.details({k: v for k, v in portfolio.items() if k not in ('records', 'category_mappings', 'gaps')}) + '</section>'

    def render(self):
        d = self.data
        document = d.get('document') or {}
        title = document.get('title', d['review_id']) if isinstance(document, dict) else d['review_id']
        nav = [('executive-summary', 'Executive summary'), ('overview', 'Overview'), ('glossary', 'Glossary'), ('thesaurus', 'Thesaurus'), ('technology_categories', 'Technologies'), ('related_fields', 'Related fields'), ('organizations', 'Organizations')]
        if 'portfolio' in d:
            nav.append(('portfolio', 'Portfolio map'))
        nav += [('questions', 'Review questions'), ('evidence', 'Sources & scope')]
        css = (ROOT / 'dashboard.css').read_text(encoding='utf-8')
        js = (ROOT / 'dashboard.js').read_text(encoding='utf-8')
        # Data stays inert even if a source contains a closing script tag or HTML.
        payload = json.dumps(d, ensure_ascii=True).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
        js_hash = hashlib.sha256(js.encode()).digest()
        import base64
        policy = "default-src 'none'; style-src 'unsafe-inline'; script-src 'sha256-" + base64.b64encode(js_hash).decode() + "'; connect-src 'none'; base-uri 'none'; form-action 'none'"
        out = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="Content-Security-Policy" content="' + escape(policy) + '"><title>' + escape(title) + ' — Invention review</title><style>' + css + '</style></head><body>']
        out += ['<a class="skip" href="#main">Skip to report</a><aside><div class="brand"><span class="brand-mark">IR</span><div>Invention review<small>Technology intelligence</small></div></div><nav aria-label="Report sections">' + ''.join('<a href="#' + key + '">' + text + '</a>' for key, text in nav) + '</nav><p class="sidebar-note">Evidence stays visible.<br>Uncertainty stays explicit.</p></aside><main id="main"><header><div><span class="eyebrow">' + escape(d.get('review_mode', 'Invention disclosure review')) + '</span><h1>' + escape(title) + '</h1><p class="muted">' + escape(d['review_id']) + ' · As of ' + escape(d['as_of']) + '</p></div><div class="actions"><button id="download" type="button">Download JSON</button><button id="print" type="button">Print / save PDF</button></div></header>']
        out.append(self.executive_summary())
        out += ['<section id="overview"><h2 class="sr-only">Overview</h2><div class="metrics">']
        for key, name in [('glossary', 'Terms & concepts'), ('technology_categories', 'Technology categories'), ('related_fields', 'Related fields'), ('organizations', 'Organizations')]:
            out.append('<a class="metric" href="#' + key + '"><strong>' + str(len(d[key])) + '</strong><span>' + name + '</span><small>Total in this review</small></a>')
        out += ['</div><div class="overview-grid"><div class="card intro"><span class="eyebrow">The invention in plain English</span><h2>Understand the mechanism</h2>' + self.value(d.get('orientation', 'See the source-linked findings below.')) + '</div><div class="card"><span class="eyebrow">Scope & confidence</span><h3>Know what was reviewed</h3>' + self.value({k: v for k, v in d['scope'].items() if k in ('research_status', 'extraction_limits')}) + '<details><summary>Materials and review boundaries</summary>' + self.value(d['scope']) + '</details></div></div>']
        if document:
            out.append(self.details({'document_metadata': document}))
        if d.get('claim_observation'):
            out.append('<div class="callout"><b>Claim observation</b><p>' + escape(d['claim_observation']) + '</p></div>')
        out += ['</section><div class="filters" id="filters" hidden><label>Search the five reports<input id="search" type="search" placeholder="Term, concept, company, source…"></label><label>Confidence<select id="confidence"><option value="">All confidence levels</option>' + ''.join('<option value="' + x + '">' + label(x) + '</option>' for x in ('high', 'medium', 'low', 'unresolved')) + '</select></label><label>Technology<select id="category"><option value="">All technologies</option>' + ''.join('<option value="' + escape(c['id']) + '">' + escape(c['id'] + ' · ' + c['name']) + '</option>' for c in d['technology_categories']) + '</select></label><label>Term type (glossary)<select id="term-type"><option value="">All types</option>' + ''.join('<option value="' + escape(t) + '">' + escape(label(t)) + '</option>' for t in sorted({g.get('type', 'uncertain') for g in d['glossary']})) + '</select></label><button id="reset" type="button">Reset</button></div><noscript><p class="callout">Interactive filters require JavaScript. All findings and evidence remain readable below.</p></noscript>']
        for key, heading, sub in [('glossary', 'Glossary', 'Plain-English meanings, roles, examples, and meaning confidence.'), ('thesaurus', 'Thesaurus', 'Synonyms, broader concepts, substitutes, and terms that must not be confused.'), ('technology_categories', 'Technology categories', 'Primary mechanisms, supporting technologies, applications, and alternatives.'), ('related_fields', 'Related fields', 'Search bridges with explicit similarities and differences.'), ('organizations', 'Organizations', 'Relevant competitors, innovators, projects, and providers with dated evidence.')]:
            out.append(self.section(key, heading, sub))
            if key == 'technology_categories':
                out.append('<section><h3>Portfolio taxonomy and mappings</h3>' + self.value(d['taxonomy']) + self.value(d.get('publication_classifications', [])) + '</section>')
        out += [self.portfolio(), '<section id="questions"><div class="section-heading"><div><span class="eyebrow">Next decisions</span><h2>Questions for review</h2></div></div>' + self.value(d['questions']) + '</section><section id="evidence"><span class="eyebrow">Trace every finding</span><h2>Sources & scope</h2><h3>Limitations</h3>' + self.value(d['limitations']) + '<h3>Source register</h3>']
        for s in d['sources']:
            out.append('<article class="card source" id="' + self.anchors[s['id']] + '"><h3>' + escape(s['id'] + ' · ' + s.get('title', 'Source')) + '</h3>' + self.value(s) + '</article>')
        out += ['<h3>Research coverage</h3>' + self.value(d['organization_coverage']) + '<details><summary>Research log</summary>' + self.value(d['research_log']) + '</details><details><summary>Handoff records</summary>' + self.value(d['handoff']) + '</details>']
        extra = {k: v for k, v in d.items() if k not in set(REQUIRED) | {'document', 'orientation', 'claim_observation', 'publication_classifications', 'review_mode', 'portfolio', 'executive_summary'}}
        out += [self.details(extra) if extra else '', '<footer>Prepared for technical review. Topic classification and claim mapping do not establish patentability, enforceable scope, or infringement.</footer></section></main><script id="review-data" type="application/json">' + payload + '</script><script>' + js + '</script></body></html>']
        return ''.join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('review_json', type=Path)
    parser.add_argument('output_html', type=Path)
    args = parser.parse_args()
    try:
        if args.review_json.resolve() == args.output_html.resolve():
            raise ValueError('Input and output paths must differ')
        data = json.loads(args.review_json.read_text(encoding='utf-8'))
        output = Dashboard(data).render()
        args.output_html.write_text(output, encoding='utf-8')
    except (ValueError, TypeError, KeyError, OSError) as exc:
        parser.exit(2, 'Cannot render review: ' + str(exc) + '\n')
    print('Wrote ' + str(args.output_html))


if __name__ == '__main__':
    main()
