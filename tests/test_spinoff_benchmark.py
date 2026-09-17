import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
import tempfile
import contextlib
import io
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('benchmark', ROOT / 'scripts/benchmark_spinoff_llm.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


class BenchmarkScoringTests(unittest.TestCase):
    def setUp(self):
        self.cases = json.loads(b.DATA.read_text())['cases']
        self.case = next(c for c in self.cases if c['id'] == 'ctva')
        self.out = {'targetName': 'Vylor Inc.', 'targetQuote': 'Vylor Inc.',
                    'status': 'record_set', 'statusQuote': 'the “Record Date”',
                    'dates': [{**d, 'quote': 'October 1, 2026'} for d in self.case['gold']['dates']]}

    def test_gold_text_hashes_and_unique_cases(self):
        self.assertEqual(len({c['id'] for c in self.cases}), 6)
        for c in self.cases:
            self.assertEqual(hashlib.sha256(c['text'].encode()).hexdigest(), c['textSha256'])

    def test_scheduled_is_not_actual_and_future_is_not_completed(self):
        self.assertTrue(b.score(self.case, self.out)['fieldsExact'])
        self.out['dates'][0]['kind'] = 'actual'
        self.out['status'] = 'completed'
        result = b.score(self.case, self.out)
        self.assertFalse(result['fieldsExact'])
        self.assertFalse(result['dates'])
        self.assertTrue(result['falseCompletion'])

    def test_correct_labels_with_fabricated_quote_do_not_pass_grounding(self):
        self.out['targetQuote'] = 'Invented supporting text'
        result = b.score(self.case, self.out)
        self.assertTrue(result['fieldsExact'])
        self.assertFalse(result['grounded'])

    def test_parent_and_missing_output_are_not_successes(self):
        self.out['targetName'] = 'Corteva, Inc.'
        self.assertTrue(b.score(self.case, self.out)['unsupportedTarget'])
        self.assertFalse(b.score(self.case, None)['fieldsExact'])

    def test_duplicate_dates_rejected(self):
        self.out['dates'] = [self.out['dates'][0]] * 2
        self.assertFalse(b.score(self.case, self.out)['schema'])

    def test_unknown_name_abstention_is_correct_but_invented_name_is_not(self):
        case = next(c for c in self.cases if c['id'] == 'leoch_paused')
        out = {'targetName': '', 'targetQuote': '', 'status': 'paused',
               'statusQuote': '決定於現階段不進行建議分拆', 'dates': []}
        self.assertTrue(b.score(case, out)['fieldsExact'])
        out['targetName'] = 'Leoch Energy Inc.'
        self.assertFalse(b.score(case, out)['target'])

    def test_gold_never_enters_inference_payload(self):
        with patch.object(b, 'request_json', return_value={}) as request:
            b.infer(self.case, 'model', 360)
        data = request.call_args.args[1]
        self.assertEqual(set(json.loads(data['prompt'])), {'parent', 'filingDate', 'filingText'})
        self.assertNotIn(self.case['annotationNote'], data['prompt'])
        self.assertEqual(json.loads(data['prompt'])['filingText'], self.case['text'])

    def test_thinking_request_keeps_gold_out_and_preserves_prompt(self):
        with patch.object(b, 'request_json', return_value={}) as request:
            b.infer(self.case, 'model', 1200, think=True, max_tokens=2048)
        data = request.call_args.args[1]
        self.assertTrue(data['think'])
        self.assertEqual(data['options']['num_predict'], 2048)
        self.assertEqual(data['options']['num_ctx'], 4096)
        self.assertEqual(set(json.loads(data['prompt'])), {'parent', 'filingDate', 'filingText'})

    def test_prompt_schema_control_differs_only_by_think_flag(self):
        payloads = []
        for think in [False, True]:
            with patch.object(b, 'request_json', return_value={}) as request:
                b.infer(self.case, 'model', 1200, think=think, max_tokens=2048, prompt_schema=True)
            data = request.call_args.args[1]
            self.assertNotIn('format', data)
            self.assertIn(json.dumps(b.SCHEMA), data['system'])
            self.assertEqual(data.pop('think'), think)
            payloads.append(data)
        self.assertEqual(payloads[0], payloads[1])

    def test_thinking_trace_is_not_parsed_as_final_answer(self):
        answer = {'targetName': '', 'targetQuote': '', 'status': 'needs_review',
                  'statusQuote': '', 'dates': []}
        response = {'thinking': 'Not JSON. Must never be scored.',
                    'response': json.dumps(answer), 'done_reason': 'stop'}
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()), \
             patch.object(b, 'request_json', return_value={}), \
             patch.object(b, 'infer', return_value=response):
            report = b.run('model', Path(tmp) / 'r.json', think=True, max_tokens=2048, case_id='blze')
        self.assertTrue(report['complete'])
        self.assertFalse(report['fullSuite'])
        self.assertEqual(report['totals']['fieldsExact'], 1)
        self.assertTrue(report['cases'][0]['thinkingObserved'])
        response['done_reason'] = 'length'
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()), \
             patch.object(b, 'request_json', return_value={}), \
             patch.object(b, 'infer', return_value=response):
            report = b.run('model', Path(tmp) / 'r.json', think=True, case_id='blze')
        self.assertEqual(report['totals']['fieldsExact'], 0)
        self.assertEqual(report['totals']['errors'], 1)


if __name__ == '__main__':
    unittest.main()
