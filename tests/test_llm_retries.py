import io
import json
import os
import tempfile
from pathlib import Path
import update_status
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
from urllib.error import HTTPError

import enrich_metadata
import fetch_spinoff
import fetch_spinoff_us


CASES = [
    (enrich_metadata, '_sf_call_enrich', 'urllib.request.urlopen', None),
    (fetch_spinoff, '_sf_call_hk', 'urllib.request.urlopen', None),
    (fetch_spinoff_us, '_sf_call', 'fetch_spinoff_us.urlopen', (None, None)),
]


def response():
    return io.BytesIO(json.dumps({'choices': [{'message': {'content': '摘要'}}]}).encode())


class ModelRetryTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {"TRACK_RUN_STATUS": "0"})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        for module, _, _, _ in CASES:
            module._SF_UNAVAILABLE = False
            module._SF_REJECTED_MODELS.clear()

    def tearDown(self):
        for module, _, _, _ in CASES:
            module._SF_UNAVAILABLE = False
            module._SF_REJECTED_MODELS.clear()

    def test_auth_and_payment_errors_stop_later_batches_without_sleeping(self):
        for code in (401, 402):
            for module, name, target, empty in CASES:
                with self.subTest(module=module.__name__, code=code):
                    module._SF_UNAVAILABLE = False
                    error = HTTPError('https://example.test', code, 'Unavailable', {}, None)
                    with patch(target, side_effect=error) as request, \
                            patch.object(module.time, 'sleep') as sleep, redirect_stdout(io.StringIO()) as output:
                        self.assertEqual(getattr(module, name)('test-key', 'batch 1'), empty)
                        self.assertEqual(getattr(module, name)('test-key', 'batch 2'), empty)
                    self.assertEqual(request.call_count, 1)
                    sleep.assert_not_called()
                    self.assertIn('::warning::', output.getvalue())

    def test_unavailable_model_is_skipped_but_next_model_can_succeed(self):
        for module, name, target, _ in CASES:
            with self.subTest(module=module.__name__):
                error = HTTPError('https://example.test', 403, 'Model unavailable', {}, None)
                with patch(target, side_effect=[error, response(), response()]) as request, \
                        patch.object(module.time, 'sleep') as sleep, redirect_stdout(io.StringIO()):
                    first = getattr(module, name)('test-key', 'batch 1')
                    second = getattr(module, name)('test-key', 'batch 2')
                self.assertTrue(first)
                self.assertTrue(second)
                self.assertEqual(request.call_count, 3)
                sleep.assert_not_called()
                first_model = json.loads(request.call_args_list[0].args[0].data)['model']
                self.assertNotEqual(json.loads(request.call_args_list[2].args[0].data)['model'], first_model)

    def test_payment_failures_reach_published_status_for_each_client(self):
        for (module, name, target, _), step in zip(CASES, ['metadata', 'spinoff_hk', 'spinoff_us']):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as directory, \
                    patch.object(update_status, 'STATUS_FILE', str(Path(directory) / 'run_status.json')), \
                    patch.dict(os.environ, {'TRACK_RUN_STATUS': '1'}), redirect_stdout(io.StringIO()):
                update_status.init_run('test')
                error = HTTPError('https://example.test', 402, 'Payment required', {}, None)
                with patch(target, side_effect=error):
                    getattr(module, name)('test-key', 'batch')
                update_status.update_step(step, 'ok')
                saved = update_status.load()['runs'][0]['steps'][step]
                self.assertEqual(saved['status'], 'warn')
                self.assertIn('余额不足', saved['msg'])

    def test_transient_server_errors_still_retry(self):
        for module, name, target, _ in CASES:
            with self.subTest(module=module.__name__):
                error = HTTPError('https://example.test', 500, 'Temporary error', {}, None)
                with patch(target, side_effect=[error, response()]) as request, \
                        patch.object(module.time, 'sleep') as sleep, redirect_stdout(io.StringIO()):
                    result = getattr(module, name)('test-key', 'batch')
                self.assertTrue(result)
                self.assertEqual(request.call_count, 2)
                sleep.assert_called_once_with(1)


if __name__ == '__main__':
    unittest.main()
