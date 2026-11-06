import copy
from datetime import date
import json
from pathlib import Path
import time
import unittest
import security_symbol_recovery as recovery

FIX=Path(__file__).parent/'fixtures/symbol_recovery'
H={'ticker':'MSGS','cusip':'55825T103','cls':'CL A','name':'MADISON SQUARE GRDN SPRT COR','shareType':'SH','putCall':''}
class SymbolRecoveryTests(unittest.TestCase):
    def discover(self,mutate=lambda text:text,holding=H):
        recent={'form':['8-K','8-K'],'filingDate':['2026-10-27','2026-09-30'],'accessionNumber':['0001193125-26-434274','0001193125-26-409143'],'primaryDocument':['d178604d8k.htm','d126791d8k.htm']}
        def fetch(path):
            if path.startswith('submissions/'):return json.dumps({'cik':'0001636519','filings':{'recent':recent}}).encode()
            if path.endswith('d178604d8k.htm'):return (FIX/'new-cover.html').read_bytes()
            if path.endswith('d126791d8k.htm'):return (FIX/'old-cover.html').read_bytes()
            if path.endswith('d126791dex991.htm'):return mutate((FIX/'unchanged-cusip.html').read_text()).encode()
            return b'<html></html>'
        return recovery.discover([holding],[{'ticker':'MSGS','cik_str':1636519}],fetch,
            lambda ticker:{'c':317,'t':time.time(),'verifiedName':'MSG Knickerbockers Corp.'},now=date(2026,11,6))
    def test_changed_name_and_directory_lag_are_resolved_from_original_class_evidence(self):
        result=self.discover()['55825T103']
        self.assertEqual(result['ticker'],'MSGK');self.assertEqual(result['oldSymbols'],['MSGS'])
        self.assertEqual(result['effectiveDate'],'2026-10-27');self.assertFalse(result['preserveCost'])
        self.assertIn('d126791dex991.htm',result['identitySourceURL'])
    def test_another_cusip_or_class_is_never_mapped_by_a_similar_name(self):
        self.assertEqual(self.discover(lambda s:s.replace('55825T103','999999999')), {})
        self.assertEqual(self.discover(holding={**H,'cls':'CL B'}),{})
        self.assertIsNone(recovery.cover((FIX/'new-cover.html').read_bytes(),999,H))
    def test_planned_ticker_without_a_new_cover_cannot_pass(self):
        self.assertEqual(recovery.cover((FIX/'old-cover.html').read_bytes(),1636519,H)['ticker'],'MSGS')
        self.assertFalse(recovery.unchanged_cusip('CUSIP 55825T103. Another security will remain unchanged.','55825T103'))
if __name__=='__main__':unittest.main()
