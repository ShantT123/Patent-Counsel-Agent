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
