import json
import unittest
from unittest.mock import patch
import fetch_spinoff_us as sec


class PrimaryDocumentTests(unittest.TestCase):
    def company(self):
        return {'ticker':'CTVA','cik':'1755672','announcements':[{'adsh':'0001193125-26-391369','date':'2026-09-15'}]}

    def test_metadata_is_resolved_before_body_without_unnecessary_index(self):
        c=self.company()
        meta={'filings':{'recent':{'accessionNumber':['0001193125-26-391369'],
            'primaryDocument':['d71834d8k.htm'],'form':['8-K']}}}
        with patch.object(sec,'sec_get',side_effect=[json.dumps(meta).encode(),b'<p>The spin-off has been completed.</p>']) as get:
            sec.resolve_primary_documents(c,None)
            text=sec.fetch_8k_text(c['cik'],c['announcements'][0]['adsh'],None,c['announcements'][0])
        self.assertIn('completed',text)
        self.assertTrue(get.call_args_list[0].args[0].endswith('CIK0001755672.json'))
        self.assertTrue(get.call_args_list[1].args[0].endswith('/d71834d8k.htm'))
        self.assertFalse(any('-index.html' in call.args[0] for call in get.call_args_list))

    def test_known_document_reused_only_for_exact_accession(self):
        c=self.company();prior=self.company();prior['announcements'][0]['primaryDocument']='d71834d8k.htm'
        with patch.object(sec,'sec_get') as get:
            sec.resolve_primary_documents(c,None,prior)
        get.assert_not_called()
        self.assertEqual(c['announcements'][0]['primaryDocument'],'d71834d8k.htm')
        c=self.company();c['announcements'][0]['adsh']='0001193125-26-000002'
        with patch.object(sec,'sec_get',return_value=b'{"filings":{"recent":{}}}'):
            sec.resolve_primary_documents(c,None,prior)
        self.assertNotIn('primaryDocument',c['announcements'][0])

    def test_missing_metadata_cannot_erase_known_document_or_select_wrong_form(self):
        c=self.company();c['announcements'][0]['primaryDocument']='known.htm'
        c['announcements'].append({'adsh':'0001193125-26-000002'})
        meta={'filings':{'recent':{'accessionNumber':['0001193125-26-000002'],
            'primaryDocument':['exhibit.htm'],'form':['SC 13G']}}}
        with patch.object(sec,'sec_get',return_value=json.dumps(meta).encode()):
            sec.resolve_primary_documents(c,None)
        self.assertEqual(c['announcements'][0]['primaryDocument'],'known.htm')
        self.assertNotIn('primaryDocument',c['announcements'][1])

    def test_metadata_unavailable_keeps_index_fallback_and_reports_missing_document(self):
        c=self.company()
        with patch.object(sec,'sec_get',side_effect=[OSError('temporary outage'),b'<html>No document table</html>']), \
             patch.object(sec,'record_source_warning') as warn, patch('builtins.print') as log:
            sec.resolve_primary_documents(c,None)
            text=sec.fetch_8k_text(c['cik'],c['announcements'][0]['adsh'],None,c['announcements'][0])
        self.assertEqual(text,'')
        warn.assert_called_once()
        self.assertTrue(any('0001193125-26-391369-index.html' in str(c) for c in log.call_args_list))

if __name__=='__main__':unittest.main()
