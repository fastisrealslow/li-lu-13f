import unittest
from unittest.mock import patch
import archive_budget as budget
from archive_continuation import latest_run


class ArchiveContinuationTests(unittest.TestCase):
    def test_latest_failed_batch_is_eligible_and_expired_or_wrong_shards_are_skipped(self):
        def get(path):
            if '/workflows/' in path:return {'workflow_runs':[{'id':100},{'id':99},{'id':98},{'id':97}]}
            ident=path.split('/runs/')[1].split('/')[0]
            return {'artifacts':{'99':[{'name':'archive-drafts-2','expired':True}],
                                 '98':[{'name':'archive-drafts-1','expired':False}],
                                 '97':[{'name':'archive-drafts-2','expired':False}]}[ident]}
        self.assertEqual(latest_run('owner/repo',2,'100',get=get),'97')

    def test_explicit_resume_does_not_silently_pick_another_run(self):
        paths=[]
        def get(path):paths.append(path);return {'artifacts':[{'name':'archive-drafts-4','expired':False}]}
        self.assertEqual(latest_run('owner/repo',4,requested='123',get=get),'123')
        self.assertEqual(len(paths),1)

    def test_nested_budget_never_extends_deadline_and_resets_afterwards(self):
        with patch.object(budget.time,'monotonic',return_value=100):
            with budget.limit(100):
                self.assertEqual(budget.timeout(900),70)
                with budget.limit(1000):self.assertEqual(budget.timeout(900),70)
                with budget.limit(10):
                    with self.assertRaises(budget.BatchDeadline):budget.check()
                self.assertEqual(budget.remaining(),100)
            self.assertIsNone(budget.remaining())


if __name__=='__main__':unittest.main()
