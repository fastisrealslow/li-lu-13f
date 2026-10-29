import copy
import json
from pathlib import Path
import unittest
from security_identity import project, project_prices
from holdings_diff import same_security, consolidate_holdings

ROOT=Path(__file__).resolve().parents[1]
class IdentityTests(unittest.TestCase):
    def test_all_investors_preserve_source_totals_rows_and_missing_reports(self):
        affected=[]
        for person in json.loads((ROOT/'investors.json').read_text())['investors']:
            source=json.loads((ROOT/person['dataFile']).read_text());before=copy.deepcopy(source);result=project(source)
            self.assertEqual(source,before)
            old=source.get('history',{}).get('holdings',{});new=result.get('history',{}).get('holdings',{})
            self.assertEqual(set(old),set(new))
            changed=False
            for q,rows in old.items():
                self.assertEqual(len(rows),len(new[q]))
                for a,b in zip(rows,new[q]):
                    self.assertEqual(a['shares'],b['shares']);self.assertEqual(a['value'],b['value'])
                    if a.get('cusip') and a['cusip']!=b['cusip']:
                        self.assertEqual((person['id'],q,a['cusip'],a['shares'],b['cusip']),('pabrai','2016 Q3','84670702',47400,'084670702'))
                        self.assertEqual(b['reportedIdentity']['cusip'],a['cusip'])
                        self.assertEqual(b['identityEvidence']['method'],'source_scoped_missing_leading_zero')
                    changed |= 'reportedIdentity' in b
                for key in ('shares','value'):
                    self.assertEqual(sum(h[key] for h in rows),sum(h[key] for h in consolidate_holdings(new[q])))
            self.assertEqual(project(result),result)
            if changed:affected.append(person['id'])
        self.assertEqual(affected,['lilu','pabrai','akre'])

    def test_known_bridges_and_real_gap(self):
        data=project(json.loads((ROOT/'data.json').read_text()))
        rows=data['history']['holdings']
        for q in ('2016 Q4','2017 Q1','2018 Q1','2018 Q2','2018 Q3'):
            self.assertEqual(len([h for h in rows[q] if h.get('cusip')=='056752108']),1)
        self.assertTrue(any(h['ticker']=='MU' and h['cusip']=='595112103' for h in rows['2019 Q4']))
        for q in ('2018 Q4','2019 Q1','2019 Q2','2019 Q3'):self.assertNotIn(q,rows)
        for file,q,ticker,cusip in [('pabrai_data.json','2015 Q2','PKX','693483109'),('akre.json','2003 Q1','KMX','143130102')]:
            rows=project(json.loads((ROOT/file).read_text()))['history']['holdings'][q]
            self.assertTrue(any(h['ticker']==ticker and h.get('cusip')==cusip for h in rows))

    def test_ambiguity_class_instrument_and_real_cusip_changes_stay_separate(self):
        row=dict(ticker='X',name='Issuer',cls='COM',shares=1,value=10)
        a={**row,'cusip':'123456789'};b={**row,'cusip':'987654321'}
        def result(known,old):
            return project({'history':{'holdings':{'2020 Q1':[old],'2020 Q2':known}}})['history']['holdings']['2020 Q1'][0]
        self.assertNotIn('cusip',result([a,b],row))
        for extra in ({'cls':'CL A'},{'cls':'ADR'},{'cls':'WARRANT'},{'putCall':'Put'},{'putCall':'Call'},{'shareType':'PRN'}):
            other={**row,**extra};self.assertNotIn('cusip',result([a],other));self.assertFalse(same_security(a,other))
        self.assertEqual(result([a],b)['cusip'],b['cusip'])

    def test_old_estimates_are_invalidated_only_for_bridged_histories(self):
        data=json.loads((ROOT/'data.json').read_text())
        prices={'exitPerf':{'MU':{'entryQuarter':'2022 Q1'},'META':{'entryQuarter':'2020 Q2'}},'costBasis':{'MU':{'avg':1},'META':{'avg':2}}}
        result=project_prices(data,prices)
        self.assertNotIn('MU',result['exitPerf']);self.assertNotIn('MU',result['costBasis'])
        self.assertIn('META',result['exitPerf']);self.assertIn('MU',prices['exitPerf'])
        prices['securityIdentityVersion']=1
        self.assertEqual(project_prices(data,prices),prices)
