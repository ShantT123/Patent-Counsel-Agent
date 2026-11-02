"""Inventory, provenance, refresh, import, and handoff invariants."""
import copy
from datetime import date, timedelta
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/portfolio-strategy/scripts/strategy.py'

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

strategy = module('strategy', SCRIPT)
filing = module('filing', ROOT / 'skills/filing-review/scripts/review.py')


class StrategyTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'examples/portfolio-strategy/input.json').read_text())

    def output(self):
        return strategy.run(self.data)

    def target(self, ident):
        return next(r for r in self.output()['target_reviews'] if r['target']['id'] == ident)

    def test_family_and_jurisdiction_counts(self):
        inv = self.output()['portfolio_inventory']
        self.assertEqual((inv['records'], inv['known_families'], inv['records_with_unknown_family']), (5, 3, 1))
        self.assertEqual(inv['by_jurisdiction']['US']['records'], 4)
        self.assertEqual(inv['by_jurisdiction']['EP']['by_status']['pending'], 1)
        self.assertEqual(inv['by_jurisdiction']['US']['published_application_records'], 0)
        self.data['records'][0]['publication_id'] = 'FICTIONAL-PUB-A'
        self.assertEqual(self.output()['portfolio_inventory']['by_jurisdiction']['US']['published_application_records'], 1)

    def test_mapped_ownership_and_org_preserved(self):
        out = self.output()
        edge = out['bucket_reviews'][0]
        self.assertEqual(edge['teams'][0]['name'], 'Embedded Systems')
        self.assertEqual(edge['people'][0]['id'], 'MIRA')
        self.assertEqual(out['organization']['teams'][1]['parent_id'], 'ENG')
        self.assertTrue(out['bucket_reviews'][2]['ownership_needs_assignment'])

    def test_proposed_mapping_excluded_from_confirmed_counts(self):
        sec = self.target('T-SEC')
        self.assertEqual(sec['candidate_records'], [])
        self.assertEqual(len(sec['proposed_mapping_candidates']), 1)
        self.assertEqual(sec['inventory_signal'], 'no_confirmed_mapped_records')
        self.assertIn('R31-US', self.output()['unmapped_or_proposed_only_record_ids'])
        self.assertEqual(self.output()['bucket_reviews'][2]['inventory']['records'], 0)

    def test_pending_and_issued_signals_not_coverage(self):
        self.assertEqual(self.target('T-ALERT')['inventory_signal'], 'pending_candidates_only_no_issued_records')
        self.assertEqual(self.target('T-DIAG')['inventory_signal'], 'issued_candidates_require_claim_review')
        self.assertTrue(all(not t['legal_gap_inferred_by_software'] for t in self.output()['target_reviews']))

    def test_jurisdiction_partition(self):
        self.assertEqual([r['record_id'] for r in self.target('T-ALERT')['candidate_records']], ['R17-US'])
        self.assertEqual([r['record_id'] for r in self.target('T-EU')['candidate_records']], ['R17-EP'])

    def test_stale_record_withholds_current_support_without_creating_gap(self):
        diag = self.target('T-DIAG')
        self.assertEqual(diag['reported_counsel_assessment']['result'], 'supports')
        self.assertEqual(diag['current_recorded_assessment'], 'not_currently_established')
        self.assertIn('record_status_needs_refresh:R25-US', diag['assessment_refresh_reasons'])
        self.assertEqual(diag['reported_counsel_assessment']['source_refs'], ['sources.md REVIEW-01 §1'])

    def test_review_window_boundary_and_undated(self):
        self.data['records'][2]['status_as_of'] = (date(2026, 11, 2) - timedelta(days=180)).isoformat()
        self.assertEqual(self.target('T-DIAG')['current_recorded_assessment'], 'supports')
        self.data['records'][2]['status_as_of'] = (date(2026, 11, 2) - timedelta(days=181)).isoformat()
        self.assertEqual(self.target('T-DIAG')['current_recorded_assessment'], 'not_currently_established')
        self.data['records'][2]['status_as_of'] = None
        self.assertEqual(self.target('T-DIAG')['candidate_records'][0]['status_freshness'], 'undated')

    def test_stale_assessment_withholds_even_with_fresh_status(self):
        self.data['records'][2]['status_as_of'] = '2026-10-24'
        self.data['assessments'][0]['reviewed_on'] = '2025-01-01'
        self.assertIn('assessment_outside_review_window', self.target('T-DIAG')['assessment_refresh_reasons'])

    def test_missing_records_do_not_generate_gap_assessment(self):
        self.data['records'] = []
        self.data['assessments'] = []
        t = self.target('T-DIAG')
        self.assertEqual(t['current_recorded_assessment'], 'not_currently_established')
        self.assertEqual(self.output()['filing_review_context']['strategy']['gaps'], [])

    def test_family_shortfall_not_pipeline_or_coverage(self):
        alert = self.target('T-ALERT')
        self.assertEqual(alert['planning_family_shortfall'], 1)
        self.assertEqual(alert['open_disclosure_count'], 1)
        self.assertEqual(self.target('T-DIAG')['open_disclosure_count'], 0)
        self.assertEqual(self.target('T-EU')['planning_family_shortfall'], 0)
        self.assertEqual(self.target('T-EU')['current_recorded_assessment'], 'not_currently_established')
        self.data['records'][0]['family_id'] = None
        self.assertEqual(self.target('T-ALERT')['active_records_with_unknown_family'], 1)
        self.assertEqual(self.target('T-ALERT')['planning_family_shortfall'], 2)

    def test_inactive_and_unknown_status_signals(self):
        self.data['records'][0]['status'] = 'expired'
        self.assertEqual(self.target('T-ALERT')['inventory_signal'], 'inactive_candidates_only')
        self.data['records'][0]['status'] = 'unknown'
        self.assertEqual(self.target('T-ALERT')['inventory_signal'], 'status_unknown_review_required')

    def test_multi_bucket_counts_are_not_global_sum(self):
        self.data['records'][0]['bucket_links'].append({'bucket_id':'DIAG','state':'confirmed','rationale':'Shared classification only','source_refs':['sources.md MAP-01 §1']})
        out = self.output()
        self.assertEqual(out['portfolio_inventory']['records'], 5)
        self.assertEqual(out['bucket_reviews'][1]['inventory']['records'], 3)

    def test_filing_review_context_is_compatible(self):
        context = self.output()['filing_review_context']
        self.assertEqual([g['id'] for g in context['strategy']['gaps']], ['T-SEC'])
        self.assertEqual(context['portfolio'][4]['bucket_ids'], [])
        filing_input = json.loads((ROOT / 'examples/filing-review/input.json').read_text())
        filing_input.update(context)
        for invention in filing_input['inventions']:
            invention['gap_ids'] = []
        result = filing.evaluate(filing_input)
        self.assertEqual(result['portfolio_summary']['known_family_count'], 3)

    def test_empty_dataset_is_useful_partial_not_error(self):
        for key in ('teams','people','products','buckets','targets','records','disclosures','assessments'):
            self.data[key] = []
        out = self.output()
        self.assertEqual(out['portfolio_inventory']['records'], 0)
        self.assertEqual(out['target_reviews'], [])

    def test_invalid_data_rejected(self):
        mutations = [
            lambda d: d['teams'][0].update(parent_id='EMB'),
            lambda d: d['teams'][0].update(parent_id='missing'),
            lambda d: d['people'][0].update(team_ids=['missing']),
            lambda d: d['buckets'][0].update(person_ids=['missing']),
            lambda d: d['targets'][0].update(jurisdiction=''),
            lambda d: d['targets'][0].update(desired_family_count=True),
            lambda d: d['records'][0].update(status_as_of='2027-01-01'),
            lambda d: d['records'][0].update(priority_date='2025-06-01'),
            lambda d: d['records'][0].update(filing_date='2025-02-30'),
            lambda d: d['records'][0]['bucket_links'].append(copy.deepcopy(d['records'][0]['bucket_links'][0])),
            lambda d: d['records'][0]['bucket_links'][0].update(state='automatic'),
            lambda d: d['assessments'][0].update(record_ids=[]),
            lambda d: d['assessments'][0].update(record_ids=['R17-EP']),
            lambda d: d['assessments'][0].update(record_ids=['R17-US']),
            lambda d: d['records'][2].update(claim_refs=[]),
            lambda d: d['assessments'][0].update(reviewed_on='2027-01-01'),
            lambda d: d['assessments'].append(copy.deepcopy(d['assessments'][0])),
            lambda d: d['disclosures'][0].update(target_ids=['T-DIAG']),
            lambda d: d['records'][0].update(source_refs=[]),
            lambda d: d.update(extra_field='typo'),
        ]
        for i, mutate in enumerate(mutations):
            with self.subTest(mutation=i):
                value = copy.deepcopy(self.data); mutate(value)
                with self.assertRaises(strategy.InputError):
                    strategy.run(value)

    def test_duplicate_public_identifiers_rejected(self):
        self.data['records'][0]['application_id'] = 'Example-ID'
        self.data['records'][2]['application_id'] = ' example-id '
        with self.assertRaises(strategy.InputError):
            self.output()

    def test_csv_roundtrip_equivalent_to_json(self):
        records = strategy.load_csv(ROOT / 'examples/portfolio-strategy/records.csv')
        self.assertEqual(records, self.data['records'])
        self.data['records'] = records
        expected = json.loads((ROOT / 'examples/portfolio-strategy/expected-output.json').read_text())
        self.assertEqual(self.output(), expected)

    def test_csv_cli_and_prevents_accidental_replacement(self):
        csv = ROOT / 'examples/portfolio-strategy/records.csv'
        command = [sys.executable, str(SCRIPT), str(ROOT / 'examples/portfolio-strategy/csv-input.json'), '--records-csv', str(csv)]
        p = subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout), self.output())
        command[2] = str(ROOT / 'examples/portfolio-strategy/input.json')
        p = subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(p.returncode, 2)
        self.assertIn('records: []', p.stderr)
        self.assertEqual(p.stdout, '')

    def test_cli_duplicate_keys_and_csv_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'bad.json'
            path.write_text('{"schema_version":"1.0","schema_version":"1.0"}')
            p = subprocess.run([sys.executable,str(SCRIPT),str(path)],capture_output=True,text=True)
            self.assertEqual(p.returncode,2)
            self.assertIn('Duplicate JSON key',p.stderr)
            csv = Path(tmp) / 'bad.csv'
            csv.write_text('id,id\na,b\n')
            with self.assertRaises(strategy.InputError):
                strategy.load_csv(csv)
            csv.write_text(','.join(strategy.CSV_FIELDS)+'\njust,three,cells\n')
            with self.assertRaises(strategy.InputError):
                strategy.load_csv(csv)

    def test_deterministic_no_mutation(self):
        before = copy.deepcopy(self.data)
        expected = json.loads((ROOT / 'examples/portfolio-strategy/expected-output.json').read_text())
        self.assertEqual(self.output(), expected)
        self.assertEqual(self.data,before)
        self.assertEqual(self.output(),self.output())


if __name__ == '__main__':
    unittest.main()
