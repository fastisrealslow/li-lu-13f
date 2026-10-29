import copy,json,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
import fetch_13f_all as sec
import batch_market_data as market
from legacy_13f import parse_legacy


def legacy(rows,total,count):
    return (f'<SEC-DOCUMENT>\n<SEC-HEADER>\nCONFORMED SUBMISSION TYPE: 13F-HR\n</SEC-HEADER>\n<TEXT>Form 13F Information Table Entry Total: {count}\nForm 13F Information Table Value Total ($ in thousands): {total}\n<TABLE>\n'+rows+'\n</TABLE></TEXT>').encode()

class LegacyAndBatchTests(unittest.TestCase):
    def test_price_distribution_adjustments_are_not_share_splits(self):
        self.assertFalse(market.is_share_split({'date':'2026-06-01','factor':1.241},{'ticker':'FDX','cusip':'31428X106'}))
        self.assertFalse(market.is_share_split({'date':'2026-04-20','factor':1.5},{'ticker':'ANAB','cusip':'032724106'}))
        self.assertTrue(market.is_share_split({'date':'2026-06-12','factor':10},{'ticker':'KLAC'}))
        self.assertTrue(market.is_share_split({'date':'2026-05-13','factor':1.01},{'ticker':'SCCO','cusip':'84265V105'}))

    def test_only_explicit_validated_split_events_are_used(self):
        result={'events':{'splits':{'one':{'date':1598832000,'numerator':4,'denominator':1}}}}
        self.assertEqual(market.split_events(result),[{'date':'2020-08-31','factor':4}])
        with self.assertRaises(ValueError):market.split_events({'events':{'splits':{'bad':{'date':1598832000,'numerator':4,'denominator':0}}}})
        self.assertEqual(market.split_events({'timestamp':[1,2],'prices':[100,25]}),[])
        old={'shareActions':[{'date':'2020-08-31','factor':4}],'shareActionsSince':'1998-01-01'}
        merged=market.merge_actions(old,{'c':10,'shareActions':[],'shareActionsSince':'2024-01-01'})
        self.assertEqual(merged['shareActions'],old['shareActions']);self.assertEqual(merged['shareActionsSince'],'1998-01-01')

    def test_legacy_amounts_and_option_right_are_not_confused_with_contract_counts(self):
        raw=legacy('APPLE INC          COM       037833100  100  2000 SH\nAPPLE INC          COM       037833100  50  1000 SH PUT',150,2)
        rows=sec.parse_holdings(raw,filing_date='2012-02-14')
        self.assertEqual(sum(h['value'] for h in rows),150000)
        self.assertEqual({h['putCall']:h['shares'] for h in rows},{'':2000,'Put':1000})

    def test_incomplete_legacy_tables_and_wrong_totals_are_rejected(self):
        for total,count in [(100,2),(1000,1)]:
            with self.assertRaises(ValueError):parse_legacy(legacy('APPLE INC          COM       037833100  100  2000 SH',total,count))
        with self.assertRaises(ValueError):parse_legacy(legacy('',0,0).replace(b'13F-HR',b'13F-HR/A'))

    def test_cover_rounding_never_changes_the_reported_line_amounts(self):
        rows=parse_legacy(legacy('APPLE INC          COM       037833100  100  2000 SH\nMICROSOFT CORP     COM       594918104  50  1000 SH',151,2))
        self.assertEqual(sum(h['value'] for h in rows),150000)

    def test_html_legacy_table_reconciles_like_the_fixed_width_format(self):
        raw=legacy('<tr><td>Apple Inc</td><td>COM</td><td>037833100</td><td>100</td><td>2000</td><td>SH</td></tr>',100,1)
        self.assertEqual(parse_legacy(raw)[0]['cusip'],'037833100')

    def test_a_leading_missing_quarter_is_discovered_and_sourced(self):
        data={'history':{'quarters':['2026 Q2'],'values':[.2],'holdings':{'2026 Q2':[]}}}
        filing=dict(reportDate='2026-03-31',filingDate='2026-05-15',accession='a',accessionDashed='a')
        xml=f'<informationTable xmlns="{sec.NS["ns"]}"><infoTable><nameOfIssuer>APPLE INC</nameOfIssuer><value>100</value><shrsOrPrnAmt><sshPrnamt>1</sshPrnamt></shrsOrPrnAmt></infoTable></informationTable>'.encode()
        with patch.object(sec,'find_info_table_xml',return_value='/Archives/test.xml'),patch.object(sec,'sec_fetch',return_value=xml):sec.backfill_history_gaps('1',data,[filing])
        self.assertIn('2026 Q1',data['history']['holdings']);self.assertEqual(data['history']['coverage']['missingQuarters'],[])

    def test_batch_history_checks_identity_and_slices_actual_candles_only(self):
        result={'meta':{'symbol':'BRK-B','currency':'USD','regularMarketPrice':100,'regularMarketTime':int(time.time())},'timestamp':[10,20,30],'indicators':{'quote':[{'close':[1,None,3],'high':[2,None,4],'low':[.5,None,2]}]}}
        series,quote=market.checked_series(result,'BRK/B');self.assertEqual(quote['c'],100)
        with patch.dict(market.SERIES,{'BRK/B':series},clear=True):
            hit,candles=market.window('BRK/B',10,30);self.assertTrue(hit);self.assertEqual(candles['closes'],[1]);self.assertEqual(candles['lows'],[.5])
            self.assertEqual(market.window('BRK/B',20,30),(True,None))
        for field,value in [('symbol','BRK-A'),('currency','HKD')]:
            other=copy.deepcopy(result);other['meta'][field]=value
            with self.assertRaises(ValueError):market.checked_series(other,'BRK/B')

if __name__=='__main__':unittest.main()

class RetirementEvidenceTests(unittest.TestCase):
    def test_form25_retirement_requires_same_issuer_class_date_and_retirement_rule(self):
        from security_lifecycle import retirement_from_form25
        xml=b'<notificationOfRemoval><issuer><cik>1</cik><entityName>Test Inc.</entityName></issuer><descriptionClassSecurity>Common Stock</descriptionClassSecurity><ruleProvision>17 CFR 240.12d2-2(a)(3)</ruleProvision><signatureData><signatureDate>2026-01-02</signatureDate></signatureData></notificationOfRemoval>'
        h={'ticker':'TEST','name':'TEST INC','cusip':'123456789','cls':'COM'};f={'cik':'1','filingDate':'2026-01-02','url':'https://www.sec.gov/Archives/test.xml'}
        self.assertEqual(retirement_from_form25(xml,h,f)['status'],'ceased_trading')
        for old,new in [(b'Test Inc.',b'Other Inc.'),(b'Common Stock',b'Preferred Stock'),(b'12d2-2(a)(3)',b'12d2-2(c)'),(b'2026-01-02',b'2099-01-02')]:
            with self.assertRaises(ValueError):retirement_from_form25(xml.replace(old,new),h,f)
        with self.assertRaises(ValueError):retirement_from_form25(xml,{**h,'cls':'CL A'},f)

class IdentifierTypeTests(unittest.TestCase):
    def test_funds_with_same_issuer_remain_separate_share_classes(self):
        self.assertTrue(sec.resolve_ticker('ISHARES INC','MSCI UNKNOWN','000000000').startswith('?'))
        data=json.loads(Path('greenblatt.json').read_text())
        expected={'46434G764':'EMXC','464286681':'EUSA','46434G822':'EWJ','464286400':'EWZ','464286871':'EWH','46434G103':'IEMG'}
        actual={h['cusip']:h['ticker'] for h in data['current']['holdings']}
        for cusip,ticker in expected.items():self.assertEqual(actual[cusip],ticker)
        self.assertEqual(len(actual),len(data['current']['holdings']))

    def test_cins_and_cusip_keep_their_official_identifier_types(self):
        import io,resolve_unmapped_tickers as resolver
        requests=[]
        def response(req,**kw):
            requests.extend(json.loads(req.data));return io.BytesIO(json.dumps([{'data':[{'exchCode':'US','securityType':'Common Stock','ticker':'FTI'}]},{'data':[{'exchCode':'US','securityType':'Common Stock','ticker':'AAPL'}]}]).encode())
        with patch.object(resolver.urllib.request,'urlopen',side_effect=response),patch.object(resolver.time,'sleep'):
            result=resolver.resolve_via_openfigi(['G87110105','037833100'])
        self.assertEqual(result,{'G87110105':'FTI','037833100':'AAPL'})
        self.assertEqual([x['idType'] for x in requests],['ID_CINS','ID_CUSIP'])
        self.assertTrue(all(x['exchCode']=='US' and x['includeUnlistedEquities'] for x in requests))

class DecimalSourceTests(unittest.TestCase):
    def test_legacy_xml_decimal_notation_preserves_exact_unit_conversion(self):
        xml=f'<informationTable xmlns="{sec.NS["ns"]}"><infoTable><nameOfIssuer>TEST INC</nameOfIssuer><titleOfClass>COM</titleOfClass><cusip>123456789</cusip><value>123.456</value><shrsOrPrnAmt><sshPrnamt>86148865.00</sshPrnamt></shrsOrPrnAmt></infoTable></informationTable>'.encode()
        h=sec.parse_holdings(xml,filing_date='2013-08-14')[0]
        self.assertEqual(h['value'],123456);self.assertEqual(h['shares'],86148865)
        with self.assertRaises(ValueError):sec.parse_holdings(xml,filing_date='2026-08-14')

    def test_fractional_legacy_shares_require_a_primary_legacy_source(self):
        from validate_data import validate_history
        h=dict(cusip='123456789',ticker='TEST',shares=1234.125,value=1000,managerAllocations=[dict(managerIds=[],shares=1234.125,value=1000)])
        history={'quarters':['2006 Q4'],'values':[.001],'holdings':{'2006 Q4':[h]},'filing_sources':{'2006 Q4':{'format':'legacy_13f','url':'https://www.sec.gov/Archives/old.txt'}}}
        validate_history(history)
        history['filing_sources']={}
        with self.assertRaises(ValueError):validate_history(history)

class LegacyLayoutRecoveryTests(unittest.TestCase):
    def fixed(self, lines, count, total, header=True):
        markers='<S>                           <C>            <C>       <C>      <C>       <C> <C>  <C>        <C>      <C>       <C>       <C>'
        body=('NAME CLASS CUSIP VALUE SHARES\n'+markers+'\n'+lines)
        raw=legacy(body,total,count)
        return raw if header else raw[0:raw.index(b'<TEXT>')+6]+b'<TABLE>\n'+body.encode()+b'\n</TABLE></TEXT>'
    def test_wrapped_values_and_fractional_shares_are_separate_fields(self):
        line=f"{'APPLE INC':30}{'COM':15}{'037833100':10}{'':9}{'2000':>9} SH\n"+' '*55+'100.00\n'
        rows=parse_legacy(self.fixed(line,1,100))
        self.assertEqual((rows[0]['shares'],rows[0]['value']),(2000,100000))
    def test_an_original_cover_error_is_recorded_without_changing_line_values(self):
        line=f"{'APPLE INC':30}{'COM':15}{'037833100':10}{100:9} {2000:8} SH"
        raw=self.fixed(line,1,200)
        with self.assertRaises(ValueError):parse_legacy(raw)
        rows=parse_legacy(raw,retain_source_discrepancies=True)
        self.assertEqual(rows[0]['value'],100000)
        self.assertEqual(rows.reconciliation['status'],'cover_total_mismatch')
        self.assertEqual(rows.reconciliation['reportedValue'],200000)
    def test_a_missing_cover_is_only_accepted_with_a_complete_fixed_width_table(self):
        line=f"{'APPLE INC':30}{'COM':15}{'037833100':10}{100:9} {2000:8} SH"
        rows=parse_legacy(self.fixed(line,1,100,header=False),retain_source_discrepancies=True)
        self.assertEqual(rows.reconciliation['status'],'missing_cover_totals')
        self.assertEqual(rows[0]['shares'],2000)
    def test_manager_reference_continuation_is_not_a_position(self):
        line=f"{'APPLE INC':30}{'COM':15}{'037833100':10}{100:9} {2000:8} SH\n"+' '*94+'4, 11, 14\n'
        rows=parse_legacy(self.fixed(line,1,100))
        self.assertEqual(len(rows),1)
    def test_source_missing_amounts_are_not_replaced_with_zero(self):
        line=f"{'APPLE INC':30}{'COM':15}{'037833100':10}{'?':>9} {2000:8} SH"
        with self.assertRaises(ValueError):parse_legacy(self.fixed(line,1,100),retain_source_discrepancies=True)
    def test_numeric_cusips_with_lost_leading_zeros_are_normalized(self):
        rows=parse_legacy(legacy('ABBOTT LAB   COM   2824100 100 2000 SH',100,1))
        self.assertEqual(rows[0]['cusip'],'002824100')

class ExplicitLegacyRestatementTests(unittest.TestCase):
    def test_only_the_checked_full_restatement_box_allows_an_amended_table(self):
        raw=legacy('APPLE INC  COM  037833100  100  2000 SH',100,1).replace(b'13F-HR',b'13F-HR/A')
        for flags in [b'[X] is a restatement [ ] adds new holding entries',b'|X| is a restatement |_| adds new holding entries']:
            accepted=raw.replace(b'<TEXT>',b'<TEXT>'+flags)
            self.assertEqual(parse_legacy(accepted)[0]['value'],100000)
        for flags in [b'[ ] is a restatement [X] adds new holding entries',b'[X] is a restatement [X] adds new holding entries',b'is a restatement']:
            with self.assertRaises(ValueError):parse_legacy(raw.replace(b'<TEXT>',b'<TEXT>'+flags))

    def test_mixed_tab_fallback_keeps_all_rows_and_audits_an_inconsistent_cover(self):
        body=f"{'APPLE INC':30}{'COM':15}{'037833100':10}100  2000 SH"
        body+='\nOTHER CORP\tCOM\t012345678  200  3000 SH'
        raw=LegacyLayoutRecoveryTests().fixed(body,2,900)
        result=parse_legacy(raw,retain_source_discrepancies=True)
        self.assertEqual(len(result),2)
        self.assertEqual(sum(h['value'] for h in result),300000)
        self.assertEqual(result.reconciliation['status'],'cover_total_mismatch')
