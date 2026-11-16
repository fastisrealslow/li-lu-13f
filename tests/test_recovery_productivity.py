import json
from pathlib import Path
import tempfile
import unittest
from datetime import datetime,timezone,timedelta
from unittest.mock import patch
import automation_health as h
from test_automation_health import NOW,run
import archive_generator as generator

class RecoveryProductivityTests(unittest.TestCase):
    def test_ghost_active_run_is_superseded_by_newer_success(self):
        ghost=run(120,None,'in_progress',ident=43097071704)
        decision=h.recovery_decision([ghost,run(1)],NOW,18)
        self.assertFalse(decision['dispatch']);self.assertEqual(decision['cancel'],[])
        self.assertEqual(decision['reason'],'healthy')
        # A genuinely new stalled run still requires cancellation and recovery.
        decision=h.recovery_decision([ghost,run(10),run(5,None,'in_progress',ident=19)],NOW,18)
        self.assertTrue(decision['dispatch']);self.assertEqual(decision['cancel'],[19])

    def test_old_ghost_does_not_disable_overdue_or_data_health_recovery(self):
        ghost=run(120,None,'in_progress',ident=7)
        self.assertTrue(h.recovery_decision([ghost,run(20)],NOW,18)['dispatch'])
        self.assertTrue(h.recovery_decision([ghost,run(1)],NOW,18,needed=True)['dispatch'])
        self.assertEqual(h.recovery_decision([ghost,run(1),run(.2,None,'in_progress',ident=8)],NOW,18)['reason'],'already_active')

    def test_successful_attempts_cannot_masquerade_as_approved_guides(self):
        with tempfile.TemporaryDirectory() as tmp,patch('archive_explanations.pending',return_value=[{'id':'pending'}]):
            path=Path(tmp)/'archive/explanations/index.json';path.parent.mkdir(parents=True)
            index={'entries':{'old':{'reviewStatus':'verified','generatedAt':(NOW-timedelta(days=3)).isoformat()}},'attempts':{'old':{'status':'ok','at':NOW.isoformat()}}}
            path.write_text(json.dumps(index))
            self.assertEqual(h.archive_productivity(tmp,NOW)['status'],'no_recent_approved_output')
            index['entries']['old']['generatedAt']=(NOW-timedelta(hours=1)).isoformat();path.write_text(json.dumps(index))
            self.assertEqual(h.archive_productivity(tmp,NOW)['status'],'checked')

    def test_no_backlog_does_not_raise_productivity_warning(self):
        with tempfile.TemporaryDirectory() as tmp,patch('archive_explanations.pending',return_value=[]):
            path=Path(tmp)/'archive/explanations/index.json';path.parent.mkdir(parents=True);path.write_text(json.dumps({'entries':{},'attempts':{}}))
            self.assertEqual(h.archive_productivity(tmp,NOW)['status'],'checked')

    def test_bounded_bilingual_write_schema(self):
        props=generator.output_schema({'task':'Write one section'})['properties']
        self.assertEqual(props['zh']['maxLength'],900)
        self.assertEqual(props['en']['maxLength'],2600)

if __name__=='__main__':unittest.main()
