import unittest
from hk_financial_evidence import parse_values

class HKFinancialTests(unittest.TestCase):
    def setUp(self):
        self.watch=dict(cik='1081316',ticker='01211.HK',entity='BHE',member='BydCompanyLimitedCommonStockMember')
        self.source=dict(url='https://www.sec.gov/Archives/edgar/data/75594/example/report.htm',reportDate='2025-03-31',filingDate='2025-05-02',accession='example')
        self.doc='''<xbrli:context id="c1"><xbrli:entity><xbrli:identifier>0001081316</xbrli:identifier><xbrli:segment><xbrldi:explicitMember dimension="us-gaap:InvestmentTypeAxis">bhe:BydCompanyLimitedCommonStockMember</xbrldi:explicitMember></xbrli:segment></xbrli:entity><xbrli:period><xbrli:instant>2025-03-31</xbrli:instant></xbrli:period></xbrli:context><xbrli:unit id="usd"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit><ix:nonFraction name="us-gaap:OtherInvestments" contextRef="c1" unitRef="usd" decimals="-6" scale="6" format="ixt:fixed-zero">—</ix:nonFraction>'''
    def test_rounded_zero_is_value_not_zero_shares(self):
        result=parse_values(self.doc,self.watch,self.source)[0]
        self.assertEqual(result['reported_value_usd'],0)
        self.assertEqual(result['precision_usd'],1000000)
        self.assertIsNone(result['shares'])
        self.assertNotIn('event_date',result)
    def test_wrong_entity_date_member_unit_and_concept_are_rejected(self):
        for original,replacement in [('0001081316','0000000001'),('2025-03-31','2024-12-31'),('BydCompanyLimitedCommonStockMember','OtherMember'),('iso4217:USD','iso4217:HKD'),('us-gaap:OtherInvestments','us-gaap:InvestmentIncome')]:
            with self.subTest(original=original):self.assertEqual(parse_values(self.doc.replace(original,replacement),self.watch,self.source),[])
    def test_value_scale_and_untrusted_sources(self):
        doc=self.doc.replace(' format="ixt:fixed-zero"','').replace('>—<','>415<')
        self.assertEqual(parse_values(doc,self.watch,self.source)[0]['reported_value_usd'],415000000)
        with self.assertRaises(ValueError):parse_values(doc,self.watch,{**self.source,'url':'https://example.com/report'})
