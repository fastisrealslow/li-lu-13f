import datetime as dt
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import archive_explanations as e
import archive_maintenance as maintenance
import market_schedule as schedule

class IncrementalTests(unittest.TestCase):
    def test_dst_slot_changes_automatically(self):
        self.assertEqual(schedule.opening_slot(dt.datetime(2026,7,1,14,15,tzinfo=dt.timezone.utc)),'15 14 * * *')
        self.assertEqual(schedule.opening_slot(dt.datetime(2026,11,15,15,15,tzinfo=dt.timezone.utc)),'15 15 * * *')

    def test_completed_material_is_reused_until_source_changes(self):
        work={'id':'cache-test','title':{'en':'Example'},'sources':[{'url':'https://example.com'}]}
        with tempfile.TemporaryDirectory() as tmp,patch.object(e,'obtain_material',return_value=('source text','official_text','https://example.com')) as get,patch.object(e.source,'source_chunks',return_value=[{},{}]):
            self.assertEqual(e.cached_material(work,tmp),e.cached_material(work,tmp));self.assertEqual(get.call_count,1)
            e.cached_material({**work,'sourceRevision':'changed'},tmp);self.assertEqual(get.call_count,2)

    def test_discovery_runs_once_per_day(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(maintenance.source,'discover') as discover:
            root=Path(tmp);e.write(root/'archive/catalog.json',{'works':[]})
            now=dt.datetime(2026,11,15,tzinfo=dt.timezone.utc)
            maintenance.discover(root,now);maintenance.discover(root,now)
            self.assertEqual(discover.call_count,1)
            maintenance.discover(root,now+dt.timedelta(days=1));self.assertEqual(discover.call_count,2)

    def test_holidays_and_half_days(self):
        # Thanksgiving closure and the following early closing session.
        self.assertNotIn('US',schedule.active_markets(dt.datetime(2026,11,26,20,tzinfo=dt.timezone.utc)))
        self.assertIn('US',schedule.active_markets(dt.datetime(2026,11,27,20,tzinfo=dt.timezone.utc)))
        self.assertNotIn('US',schedule.active_markets(dt.datetime(2026,11,29,12,tzinfo=dt.timezone.utc)))
        self.assertIn('HK',schedule.active_markets(dt.datetime(2026,11,16,8,35,tzinfo=dt.timezone.utc)))

if __name__=='__main__':unittest.main()
