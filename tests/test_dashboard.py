"""Renderer checks for evidence preservation, offline output, and unsafe input handling."""
import copy
import importlib.util
import json
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/invention-disclosure-review/scripts/render_dashboard.py'
spec = importlib.util.spec_from_file_location('dashboard', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = []
        self.links = []
        self.srcs = []
        self.payload = ''
        self.in_payload = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if 'id' in values:
            self.ids.append(values['id'])
        if 'href' in values:
            self.links.append(values['href'])
        if 'src' in values:
            self.srcs.append(values['src'])
        if tag == 'script' and values.get('id') == 'review-data':
            self.in_payload = True

    def handle_data(self, value):
        if self.in_payload:
            self.payload += value

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_payload = False


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'examples/invention-disclosure-review/dashboard-input.json').read_text())

    def test_complete_data_roundtrip_and_resolved_navigation(self):
        rendered = module.Dashboard(self.data).render()
        parsed = Document(rendered)
        self.assertEqual(json.loads(parsed.payload), self.data)
        self.assertEqual(len(parsed.ids), len(set(parsed.ids)))
        self.assertTrue(all(url[1:] in parsed.ids for url in parsed.links if url.startswith('#')))
        for section in ('glossary', 'thesaurus', 'technology_categories', 'related_fields', 'organizations', 'portfolio'):
            self.assertIn(section, parsed.ids)
        self.assertIn('description_only', parsed.payload)
        self.assertIn('FICT-APP-B', rendered)

    def test_untrusted_content_and_executable_links_are_inert(self):
        attack = '</script><script>alert("unsafe")</script><img src=x onerror=alert(1)>'
        self.data['glossary'][0]['plain_english_definition'] = attack
        self.data['sources'][0]['url'] = 'javascript:alert(2)'
        self.data['sources'][0]['local_file'] = 'file:///etc/passwd'
        text = module.Dashboard(self.data).render()
        parsed = Document(text)
        self.assertNotIn('<script>alert', text)
        self.assertNotIn('<img src=x', text)
        self.assertNotIn('javascript:alert(2)', parsed.links)
        self.assertNotIn('file:///etc/passwd', parsed.links)
        self.assertEqual(json.loads(parsed.payload), self.data)
        self.assertIn('Content-Security-Policy', text)
        self.assertIn("connect-src &#x27;none&#x27;", text)

    def test_standalone_contains_no_remote_assets(self):
        text = module.Dashboard(self.data).render()
        parsed = Document(text)
        self.assertEqual(parsed.srcs, [])
        self.assertNotIn('@import', text)
        self.assertNotIn('fetch(', text)
        self.assertIn('<noscript>', text)
        self.assertIn('@media print', text)
        self.assertIn('beforeprint', text)

    def test_claim_mapping_needs_claim_locators(self):
        self.data['portfolio']['category_mappings'][0]['claim_locators'] = []
        with self.assertRaisesRegex(ValueError, 'claim locators'):
            module.Dashboard(self.data)

    def test_unknown_document_mapping_is_rejected(self):
        self.data['portfolio']['category_mappings'][0]['document_id'] = 'missing'
        with self.assertRaisesRegex(ValueError, 'unknown document'):
            module.Dashboard(self.data)

    def test_empty_document_review_and_missing_confidence(self):
        for key in module.ARRAYS:
            self.data[key] = []
        self.data.pop('portfolio')
        self.data.pop('executive_summary', None)
        output = module.Dashboard(self.data).render()
        self.assertIn('No entries match', output)
        self.assertIn('None recorded', output)
        self.assertNotIn('id="portfolio"', output)

    def test_summary_precedes_metrics_and_retains_qualifications(self):
        text = module.Dashboard(self.data).render()
        self.assertLess(text.index('id="executive-summary"'), text.index('id="overview"'))
        self.assertIn('no legal patent coverage', text)
        self.assertIn('What remains uncertain', text)
        self.assertIn('Next steps', text)

    def test_summary_requires_resolved_evidence_and_locators(self):
        for ref in ({'source_id': 'missing', 'locator': 'p1'}, {'source_id': 'S-DEMO'}):
            data = copy.deepcopy(self.data)
            data['executive_summary']['overview'][0]['evidence'] = [ref]
            with self.assertRaisesRegex(ValueError, 'source ID and locator'):
                module.Dashboard(data)

    def test_legacy_summary_fallback_is_explicit(self):
        self.data.pop('executive_summary')
        text = module.Dashboard(self.data).render()
        self.assertIn('no authored executive summary', text)
        self.assertIn(self.data['orientation'], text)

    def test_visible_citations_have_safe_public_links_and_private_locators(self):
        self.data['sources'][0]['url'] = 'https://example.org/evidence'
        dashboard = module.Dashboard(self.data)
        citation = dashboard.citations(self.data['glossary'][0])
        self.assertIn('href="#' + dashboard.anchors['S-DEMO'] + '"', citation)
        self.assertIn('href="https://example.org/evidence"', citation)
        self.assertIn('A1', citation)
        self.assertIn('Sources cited in this entry', dashboard.card(self.data['glossary'][0], 'glossary'))
        self.data['sources'][0]['url'] = 'file:///private/disclosure'
        self.assertNotIn('Open source', module.Dashboard(self.data).citations(self.data['glossary'][0]))

    def test_summary_text_and_source_titles_are_escaped(self):
        attack = '<img src=x onerror=alert(1)>'
        self.data['executive_summary']['overview'][0]['text'] = attack
        self.data['sources'][0]['title'] = attack
        self.data['sources'][0]['url'] = 'javascript:alert(1)'
        text = module.Dashboard(self.data).render()
        self.assertNotIn(attack, text)
        self.assertNotIn('javascript:alert(1)', Document(text).links)

    def test_word_cloud_links_every_phrase_and_defaults_to_equal_weights(self):
        cloud = module.Dashboard(self.data).word_cloud()
        self.assertEqual(cloud.count('<li>'), len(self.data['glossary']))
        self.assertIn('All terms have equal weight', cloud)
        self.assertIn('Generation number</a>', cloud)
        self.assertEqual(cloud.count('font-size:20px'), len(self.data['glossary']))

    def test_frequency_cloud_requires_documented_comparable_counts(self):
        for n, g in enumerate(self.data['glossary']):
            g['occurrence_count'] = n + 1
            g['occurrence_count_basis'] = {'scope': 'Fictional A1', 'method': 'Manual', 'evidence': [{'source_id': 'S-DEMO', 'locator': 'A1'}]}
        cloud = module.Dashboard(self.data).word_cloud()
        self.assertIn('Size shows recorded occurrences', cloud)
        self.assertNotIn('font-size:20px', cloud)
        self.data['glossary'][0]['occurrence_count_basis']['scope'] = 'Different material'
        self.assertIn('All terms have equal weight', module.Dashboard(self.data).word_cloud())
        self.data['glossary'][0]['occurrence_count'] = 0
        with self.assertRaisesRegex(ValueError, 'positive integer'):
            module.Dashboard(self.data)

    def test_missing_count_provenance_is_rejected(self):
        self.data['glossary'][0]['occurrence_count'] = 7
        with self.assertRaisesRegex(ValueError, 'scope, method, and evidence'):
            module.Dashboard(self.data)

    def test_multiple_related_terms_are_labeled_under_original_wording(self):
        record = self.data['thesaurus'][0]
        record['relations'].append({'target_glossary_id': 'G-002', 'relation_type': 'confused_with', 'explanation': 'A team label differs from a version number.'})
        card = module.Dashboard(self.data).card(record, 'thesaurus')
        self.assertIn('Term: Generation number', card)
        self.assertIn('Related terms:', card)
        self.assertIn('version identifier', card)
        self.assertIn('Lantern', card)
        self.assertIn('How related / important differences:', card)

    def test_related_technologies_are_grouped_without_losing_records(self):
        record = copy.deepcopy(self.data['related_fields'][0])
        record['id'] = 'R-004'
        record['name'] = 'Another related technology'
        self.data['related_fields'].append(record)
        output = module.Dashboard(self.data).section('related_fields', 'Related fields', '')
        self.assertEqual(output.count('class="field-group"'), len(self.data['technology_categories']))
        self.assertEqual(output.count('class="entry card"'), len(self.data['related_fields']))
        self.assertIn('Technology: ' + self.data['technology_categories'][0]['name'], output)
        self.assertIn('Related technologies:', output)
        self.assertIn('Related technology: Another related technology', output)
        self.assertIn('How related:', output)
        self.assertIn('Important differences:', output)

    def test_empty_relations_and_hostile_cloud_labels_remain_readable(self):
        self.data['thesaurus'][0]['relations'] = []
        self.data['glossary'][0]['original_wording'] = '<img src=x>'
        dashboard = module.Dashboard(self.data)
        self.assertIn('No supported related terms', dashboard.card(self.data['thesaurus'][0], 'thesaurus'))
        self.assertNotIn('<img src=x>', dashboard.word_cloud())

    def test_cli_preserves_input_and_does_not_overwrite_it(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'input.json'
            target = Path(folder) / 'output.html'
            raw = json.dumps(self.data)
            source.write_text(raw)
            result = subprocess.run([sys.executable, str(SCRIPT), str(source), str(target)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(target.exists())
            self.assertEqual(source.read_text(), raw)
            rejected = subprocess.run([sys.executable, str(SCRIPT), str(source), str(source)], capture_output=True, text=True)
            self.assertEqual(rejected.returncode, 2)
            self.assertEqual(source.read_text(), raw)

    def test_does_not_mutate_assessment(self):
        original = copy.deepcopy(self.data)
        module.Dashboard(self.data).render()
        self.assertEqual(self.data, original)


if __name__ == '__main__':
    unittest.main()
