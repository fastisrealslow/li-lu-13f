import gzip,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from security_lifecycle import discover_retirements
from historical_security_audit import refresh

class HistoricalSecurityAuditTests(unittest.TestCase):
    def test_form25_requires_unique_candidate_class_and_respects_bounded_quarter(self):
        h={'cusip':'123456789','ticker':'?TEST','name':'Test Inc','cls':'COM'}
        index=gzip.compress(b'CIK|Company Name|Form Type|Date Filed|Filename\n1|Test Inc|25-NSE|2020-05-01|edgar/data/1/0000000001-20-000001.txt')
        xml=b'<notificationOfRemoval><issuer><cik>1</cik><entityName>Test Inc</entityName></issuer><descriptionClassSecurity>Common Stock</descriptionClassSecurity><ruleProvision>12d2-2(a)(3)</ruleProvision><signatureData><signatureDate>2020-05-01</signatureDate></signatureData></notificationOfRemoval>'
        calls=[]
        def fetch(path):
            calls.append(path);return index if path.endswith('.gz') else xml
        result=discover_retirements([h], '2020-04-01', fetch, until='2020-06-30')
        self.assertEqual(result[h['cusip']]['status'],'ceased_trading')
        self.assertEqual(len(calls),2)
        calls.clear()
        self.assertEqual(discover_retirements([h,{**h,'cusip':'987654321'}], '2020-04-01', fetch, until='2020-06-30'),{})
        self.assertEqual(calls,[])

    def test_failed_index_does_not_advance_cursor_and_success_is_persisted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'investors.json').write_text(json.dumps({'investors':[{'id':'a','source13F':True,'dataFile':'a.json'}]}))
            (root/'a.json').write_text(json.dumps({'history':{'holdings':{'2020 Q1':[{'cusip':'123456789','ticker':'?TEST','name':'Test Inc','cls':'COM','shares':1}]}}}))
            (root/'security_lifecycle.json').write_text(json.dumps({'version':1,'events':{},'historyAudit':{'nextIndex':2020*4+1}}))
            before=(root/'security_lifecycle.json').read_text()
            with patch('security_lifecycle.discover_retirements',side_effect=OSError('offline')):
                with self.assertRaises(OSError):refresh(root,index_limit=1)
            self.assertEqual((root/'security_lifecycle.json').read_text(),before)
            with patch('security_lifecycle.discover_retirements',return_value={}):refresh(root,index_limit=1)
            self.assertEqual(json.loads((root/'security_lifecycle.json').read_text())['historyAudit']['nextIndex'],2020*4)
