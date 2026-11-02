"""Observable financial and review invariants; no model-performance claims."""
import copy
from decimal import Decimal
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/filing-review/scripts/review.py'
spec = importlib.util.spec_from_file_location('review', SCRIPT)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'examples/filing-review/input.json').read_text())

    def run_data(self):
        return review.evaluate(self.data)

    def test_example_budget_and_quarters(self):
        result = self.run_data()
        a, b = result['scenarios']
        self.assertEqual((a['new_cost'], a['contingency'], a['forecast_total'], a['headroom']), ('28000.00', '2800.00', '65800.00', '14200.00'))
        self.assertEqual(a['new_cost_by_quarter_excluding_contingency'], {'2027-Q1': '14000.00', '2027-Q2': '14000.00'})
        self.assertEqual((b['forecast_total'], b['headroom']), ('50400.00', '29600.00'))

    def test_missing_rating_does_not_become_zero_or_partial_score(self):
        result = self.run_data()['invention_reviews'][0]
        self.assertIsNone(result['business_score'])
        self.assertEqual(result['missing_criteria'], ['detectability'])
        del self.data['inventions'][0]['ratings']['detectability']
        self.assertIsNone(self.run_data()['invention_reviews'][0]['business_score'])

    def test_complete_draft_score_not_approved(self):
        r = self.run_data()['invention_reviews'][1]
        self.assertEqual(r['business_score'], '70.00')
        self.assertIsNone(r['meets_approved_business_threshold'])

    def test_approved_threshold_uses_unrounded_value(self):
        self.data['policy'].update(state='approved', approved_by='Fictional policy owner', approved_on='2026-11-02')
        self.assertTrue(self.run_data()['invention_reviews'][1]['meets_approved_business_threshold'])
        self.data['inventions'][1]['ratings']['product_relevance']['value'] = '7.99999'
        r = self.run_data()['invention_reviews'][1]
        self.assertEqual(r['business_score'], '70.00')
        self.assertFalse(r['meets_approved_business_threshold'])

    def test_weight_scaling_does_not_change_score(self):
        original = self.run_data()['invention_reviews'][1]['business_score']
        for criterion in self.data['policy']['criteria']:
            criterion['weight'] = str(Decimal(criterion['weight']) * 3)
        self.assertEqual(self.run_data()['invention_reviews'][1]['business_score'], original)

    def test_families_not_double_counted_unknowns_remain_unknown(self):
        self.assertEqual(self.run_data()['portfolio_summary']['known_family_count'], 1)
        for rec in self.data['portfolio']:
            rec['family_id'] = None
        result = self.run_data()['portfolio_summary']
        self.assertEqual(result['known_family_count'], 0)
        self.assertEqual(result['records_with_unknown_family'], 2)

    def test_candidates_do_not_establish_coverage_or_gap(self):
        r = self.run_data()['invention_reviews'][0]
        self.assertEqual(len(r['candidate_portfolio_records']), 2)
        self.assertTrue(all(x['coverage_conclusion'] == 'not_assessed' for x in r['candidate_portfolio_records']))
        self.data['portfolio'] = []
        r = self.run_data()['invention_reviews'][0]
        self.assertEqual(r['portfolio_conclusion'], 'no_candidates_in_supplied_records_gap_not_established')

    def test_casefold_term_match_without_shared_bucket(self):
        self.data['portfolio'][0]['bucket_ids'] = []
        self.data['portfolio'][0]['technical_terms'] = ['  GATEWAY SCHEDULING  ']
        r = self.run_data()['invention_reviews'][0]
        self.assertEqual(r['candidate_portfolio_records'][0]['shared_terms'], ['gateway scheduling'])

    def test_period_boundaries_and_outside_lines(self):
        self.data['plan'][0]['expected_date'] = '2027-01-01'
        self.data['plan'][1]['expected_date'] = '2027-12-31'
        self.data['plan'][2]['expected_date'] = '2028-01-01'
        self.data['plan'][3]['expected_date'] = '2026-12-31'
        s = self.run_data()['scenarios'][0]
        self.assertEqual(s['new_cost'], '14000.00')
        self.assertEqual(len(s['outside_period_lines']), 2)

    def test_exact_cents_and_half_up_reserve(self):
        self.data['cost_catalog']['items'][0]['unit_cost'] = '0.05'
        self.data['scenarios'][0]['plan_line_ids'] = ['L1']
        s = self.run_data()['scenarios'][0]
        self.assertEqual(s['new_cost'], '0.05')
        self.assertEqual(s['contingency'], '0.01')
        self.assertEqual(s['forecast_total'], '35000.06')

    def test_over_budget_and_exact_limit(self):
        self.data['budget']['limit'] = '65800.00'
        self.assertFalse(self.run_data()['scenarios'][0]['over_budget'])
        self.data['budget']['limit'] = '65799.99'
        s = self.run_data()['scenarios'][0]
        self.assertTrue(s['over_budget'])
        self.assertEqual(s['headroom'], '-0.01')

    def test_empty_scenario_still_includes_existing_commitments(self):
        self.data['scenarios'][0]['plan_line_ids'] = []
        s = self.run_data()['scenarios'][0]
        self.assertEqual(s['forecast_total'], '35000.00')
        self.assertEqual(s['contingency'], '0.00')

    def test_invalid_inputs_are_rejected(self):
        mutations = [
            lambda d: d['policy']['criteria'][0].update(weight='0'),
            lambda d: d['policy']['criteria'][0].update(max=1),
            lambda d: d['policy'].update(state='approved'),
            lambda d: d['policy'].update(business_threshold='101'),
            lambda d: d['inventions'][0]['ratings']['product_relevance'].update(value=11),
            lambda d: d['inventions'][0]['ratings']['product_relevance'].update(source_refs=[]),
            lambda d: d['inventions'][0]['ratings'].update(typo={'value':1}),
            lambda d: d['cost_catalog'].update(currency='EUR'),
            lambda d: d['cost_catalog']['items'][0].update(unit_cost='-1'),
            lambda d: d['cost_catalog']['items'][0].update(unit_cost='NaN'),
            lambda d: d['cost_catalog']['items'][0].update(unit_cost='1.001'),
            lambda d: d['budget'].update(end='2026-01-01'),
            lambda d: d['plan'][0].update(expected_date='2027-02-30'),
            lambda d: d['plan'][0].update(quantity=True),
            lambda d: d['plan'][0].update(quantity=0),
            lambda d: d['plan'][0].update(cost_id='missing'),
            lambda d: d['scenarios'][0].update(plan_line_ids=['L1', 'L1']),
            lambda d: d['scenarios'][0].update(plan_line_ids=['missing']),
            lambda d: d['portfolio'].append(copy.deepcopy(d['portfolio'][0])),
            lambda d: d['budget'].update(spnet='1'),
        ]
        for i, mutate in enumerate(mutations):
            with self.subTest(mutation=i):
                data = copy.deepcopy(self.data)
                mutate(data)
                with self.assertRaises(review.InputError):
                    review.evaluate(data)

    def test_reproducible_output_without_mutating_inputs(self):
        before = copy.deepcopy(self.data)
        result = self.run_data()
        self.assertEqual(self.data, before)
        self.assertEqual(result, self.run_data())
        expected = json.loads((ROOT / 'examples/filing-review/expected-output.json').read_text())
        self.assertEqual(result, expected)

    def test_cli_errors_and_decimal_json_tokens(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'input.json'
            path.write_text('{"schema_version":"1.0","schema_version":"1.0"}')
            p = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
            self.assertEqual(p.returncode, 2)
            self.assertIn('Duplicate JSON key', p.stderr)
            self.assertEqual(p.stdout, '')
            self.data['cost_catalog']['items'][0]['unit_cost'] = '0.05'
            raw = json.dumps(self.data).replace('"unit_cost": "0.05"', '"unit_cost": 0.05')
            path.write_text(raw)
            p = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(json.loads(p.stdout)['scenarios'][0]['included_lines'][0]['amount'], '0.05')


if __name__ == '__main__':
    unittest.main()
