import copy
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import ai_supplement as ai
import build_browser_assets as browser


def fixture():
    row = dict(ticker='TEST', cusip='123456789', name='Test Inc', cnName='测试公司',
        cls='COM', shares=10, value=1234567, shareType='SH', putCall='',
        managerAllocations=[dict(managerIds=['1'], shares=10, value=1234567)])
    return {'meta': {'instrumentHistoryTickers': ['TEST'], 'instrumentHistoryFrom':'2026 Q1'},
        'current': {'quarter':'2026 Q2','prevQuarter':'2026 Q1','periodEnd':'2026-06-30',
            'totalValue':1234567,'holdings':[row],'previousHoldings':[{**row,'shares':8}]},
        'history': {'quarters':['2026 Q1','2026 Q2'],'values':[1,1],
            'holdings':{'2026 Q1':[{**row,'shares':8}],'2026 Q2':[row]},
            'filing_sources':{'2026 Q1':{'cik':'1'}},'valueAudit':{'large':'backend evidence'}}}


class BrowserAssetsTests(unittest.TestCase):
    def test_overview_retains_precise_numbers_and_cost_class_proofs_without_the_archive(self):
        source=fixture();before=copy.deepcopy(source)
        prices={'quotes':{'TEST':{'c':100}},'costBasis':{'TEST':{'recent':{'quarter':'2026 Q1'},'allTime':{'first':'2026 Q1'}}}}
        result=browser.current_data(source,prices)
        self.assertEqual(source,before)
        self.assertEqual(result['history']['holdings'],{})
        self.assertNotIn('valueAudit',result['history'])
        self.assertEqual(result['history']['values'],[1.234567,1.234567])
        self.assertEqual(result['history']['costReferenceProofs']['2026 Q1'],[['TEST','123456789']])
        self.assertEqual(result['current']['holdings'][0]['value'],1234567)
        self.assertEqual(result['current']['previousHoldings'][0]['shares'],8)

    def test_scope_manager_evidence_and_historical_instruments_are_preserved(self):
        source=fixture();source['meta']['reportingTransition']={'fromQuarter':'2026 Q1'}
        result=browser.current_data(source,{})
        self.assertEqual(result['current']['holdings'][0]['managerAllocations'],source['current']['holdings'][0]['managerAllocations'])
        self.assertEqual(result['history']['holdings']['2026 Q1'],source['history']['holdings']['2026 Q1'])
        source['history']['holdings']['2026 Q1'][0]['putCall']='Put'
        history=browser.history_data(source,{'exitPerf':{'OLD':{'entryPrice':1,'exitPrice':2}}})
        self.assertEqual(history['history']['holdings']['2026 Q1'][0]['putCall'],'Put')
        self.assertEqual(history['exitPerf']['OLD']['exitPrice'],2)

    def test_changed_source_cannot_ship_a_stale_summary_and_assets_are_immutable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=fixture()
            config={'id':'test','name':'测试','nameEn':'Test','source13F':True,'dataFile':'data.json','pricesFile':'prices.json'}
            (root/'investors.json').write_text(json.dumps({'investors':[config]}))
            (root/'data.json').write_text(json.dumps(source))
            (root/'prices.json').write_text(json.dumps({'quotes':{'TEST':{'c':100,'t':1}},'costBasis':{}}))
            tasks=ai.tasks(root);cache={'entries':{t['id']:ai.make_entry(t,ai.fallback_selection(t['facts'])) for t in tasks}}
            cache['entries']['investor:test']['summary']='Incorrect old numbers'
            (root/'ai_supplement.json').write_text(json.dumps(cache))
            first=browser.build(root);entry=first['investors']['test'];snapshot=browser.read(root/entry['snapshot']['file'])
            self.assertNotEqual(snapshot['insights']['entries']['investor:test']['summary'],'Incorrect old numbers')
            for kind in ('snapshot','history'):
                raw=(root/entry[kind]['file']).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),entry[kind]['sha256'])
                compressed=(root/entry[kind]['gzipFile']).read_bytes()
                self.assertEqual(gzip.decompress(compressed),raw)
                self.assertEqual(len(compressed),entry[kind]['gzipBytes'])
            self.assertEqual(browser.build(root),first)
            source['current']['holdings'][0]['value']+=10;source['current']['totalValue']+=10
            (root/'data.json').write_text(json.dumps(source))
            updated=browser.build(root)['investors']['test']['snapshot']['file']
            self.assertNotEqual(updated,entry['snapshot']['file'])
            self.assertTrue((root/entry['snapshot']['file']).exists())


if __name__=='__main__':unittest.main()
