import json,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
import enrich_metadata as e

class ValueScreenSources(unittest.TestCase):
    def test_shared_quote_references_and_directions_stay_bound_to_their_holder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);people=[]
            for ident,buy,price,stamp,prev,shares in [('a',120,85,20,10,12),('b',100,80,10,20,10),('c',85,90,30,None,10)]:
                data=root/(ident+'.json');quotes=root/(ident+'-prices.json')
                data.write_text(json.dumps({'meta':{},'current':{'quarter':'2026 Q2','totalValue':1000,'holdings':[{'ticker':'TEST','name':'Test','cusip':'123456789','shares':shares,'prevShares':prev,'value':500,'shareType':'SH'}]}}))
                quotes.write_text(json.dumps({'quotes':{'TEST':{'c':price,'t':time.time()-100+stamp,'currency':'USD'}},'costBasis':{'TEST':{'recent':{'buy':buy,'quarter':'2025 Q4','source':'yahoo'},'allTime':{'avg':buy,'buy_quarters':2}}}}))
                people.append({'id':ident,'name':ident,'nameEn':ident,'dataFile':str(data),'pricesFile':str(quotes),'inValueScreen':True})
            with patch.object(e,'load_investors',return_value=people):
                screen=e._build_value_screen();prompt,notes,candidates,_=e._build_homework_prompt()
            c=screen['candidates'][0]
            self.assertEqual(c['price'],90);self.assertEqual(c['buy'],100);self.assertEqual(c['mos'],10)
            self.assertEqual(c['referenceInvestorId'],'b');self.assertEqual(c['referenceQuarter'],'2025 Q4')
            self.assertEqual([(h['id'],h['chg']) for h in c['investors']],[('a','added'),('b','trimmed')])
            self.assertEqual(c['otherHolders'][0]['chg'],'unknown');self.assertIsNone(c['otherHolders'][0]['previousShares'])
            self.assertEqual([n['ticker'] for n in notes],[x['ticker'] for x in screen['candidates']])
            self.assertEqual(candidates['TEST']['price'],90);self.assertEqual(notes[0]['buy'],100)

if __name__=='__main__':unittest.main()
