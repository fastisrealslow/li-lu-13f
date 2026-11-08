import copy,json,tempfile,unittest
from datetime import datetime,timezone,timedelta
from pathlib import Path
from unittest.mock import patch
import historical_quote_refresh as job
from fetch_prices_all import write_prices_atomic

NOW=datetime(2026,11,8,12,tzinfo=timezone.utc)
def h(tk):return dict(ticker=tk,cusip=tk.ljust(9,'0'),cls='COM',shares=10,value=100)
def data(*tickers):return {'current':{'quarter':'2026 Q2','holdings':[]},'history':{'holdings':{'2025 Q1':[h(t) for t in tickers]}}}
def quote(tk='A'):return {'c':10,'t':datetime(2026,11,6,21,tzinfo=timezone.utc).timestamp(),'symbol':tk,'currency':'USD','shareActions':[]}

class HistoricalQuoteTests(unittest.TestCase):
    def setUp(self):job.SESSION_QUOTES.clear()
    def test_missing_historical_quote_is_discovered_without_existing_quote_entry(self):
        q={};calls=[]
        state=job.refresh(data('A'),q,now=NOW,loader=lambda ts:(calls.extend(ts) or {'A':quote()}))
        self.assertEqual(calls,['A']);self.assertEqual(q['A']['c'],10);self.assertEqual(state['A']['failures'],0)
    def test_failed_prefix_does_not_starve_later_symbols_and_old_price_survives(self):
        old={'c':5,'t':1};q={'A':old};calls=[]
        state=job.refresh(data('A','B'),q,now=NOW,limit=1,loader=lambda ts:(calls.extend(ts) or {'A':{'error':True}}))
        job.refresh(data('A','B'),q,state,now=NOW,limit=1,loader=lambda ts:(calls.extend(ts) or {'B':quote('B')}))
        self.assertEqual(calls,['A','B']);self.assertEqual(q['A'],old);self.assertIn('B',q)
        job.SESSION_QUOTES.clear()
        second=job.refresh(data('A'),q,state,now=NOW+timedelta(days=1),loader=lambda ts:{})
        self.assertEqual(second['A']['failures'],2)
        self.assertEqual(datetime.fromisoformat(second['A']['nextAttemptAt']),NOW+timedelta(days=3))
    def test_weekend_and_cross_investor_quotes_do_not_repeat_download(self):
        q={'A':quote()};calls=[]
        job.refresh(data('A'),q,now=NOW,loader=lambda ts:calls.extend(ts))
        other={};job.refresh(data('A'),other,now=NOW,loader=lambda ts:calls.extend(ts))
        self.assertEqual(calls,[]);self.assertEqual(other['A']['c'],10)
    def test_failure_or_action_conflict_is_isolated_to_one_security(self):
        q={'A':{'c':5,'t':1,'shareActions':[{'date':'2025-01-01','factor':2}]}}
        before=copy.deepcopy(q['A'])
        bad={**quote(),'shareActions':[{'date':'2025-01-01','factor':3}]}
        state=job.refresh(data('A','B'),q,now=NOW,loader=lambda ts:{'A':bad,'B':quote('B')})
        self.assertEqual(q['A'],before);self.assertEqual(q['B']['c'],10);self.assertEqual(state['A']['failures'],1)
        job.SESSION_QUOTES.clear()
        job.refresh(data('C'),q,now=NOW,loader=lambda ts:(_ for _ in ()).throw(TimeoutError()))
        self.assertNotIn('C',q)
    def test_fresh_shared_quote_bypasses_failure_backoff_without_network(self):
        state={'A':{'cusip':h('A')['cusip'],'nextAttemptAt':(NOW+timedelta(days=7)).isoformat(),'failures':3}}
        job.SESSION_QUOTES['A']=quote();q={};calls=[]
        job.refresh(data('A'),q,state,now=NOW,loader=lambda ts:calls.extend(ts))
        self.assertEqual(q['A']['c'],10);self.assertEqual(calls,[])

    def test_confirmed_retirement_is_not_queried(self):
        calls=[]
        with patch.object(job,'event_for',return_value={'status':'ceased_trading'}):job.refresh(data('A'),{},now=NOW,loader=lambda ts:calls.extend(ts))
        self.assertEqual(calls,[])
    def test_price_identity_mismatch_never_replaces_existing_quote(self):
        q={};job.refresh(data('A'),q,now=NOW,loader=lambda ts:{'A':quote('WRONG')})
        self.assertNotIn('A',q)
    def test_atomic_failure_preserves_previous_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'prices.json';p.write_text('{"old":true}')
            with self.assertRaises(ValueError):write_prices_atomic(p,{'bad':float('nan')})
            self.assertEqual(json.loads(p.read_text()),{'old':True});self.assertEqual(len(list(Path(tmp).iterdir())),1)
            write_prices_atomic(p,{'new':True});self.assertEqual(json.loads(p.read_text()),{'new':True})

    def test_interrupted_history_refresh_keeps_old_ledger_and_old_quotes(self):
        import fetch_prices_all as prices
        import contextlib,io
        snapshot={'current':{'quarter':'2026 Q2','prevQuarter':'2026 Q1','holdings':[h('A')]},'history':{'holdings':{'2026 Q1':[h('A')],'2026 Q2':[h('A')]}}}
        ledger={'version':1,'entries':{},'quoteRefresh':{'OLD':{'failures':2}}}
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);d=root/'data.json';p=root/'prices.json';d.write_text(json.dumps(snapshot));p.write_text(json.dumps({'quotes':{'OLD':quote('OLD')},'tradePrices':ledger}))
            with patch.object(prices,'finnhub',return_value={'c':100,'h':100,'l':100,'o':100,'pc':100,'t':1}),patch.object(prices,'yahoo_chart',return_value={'closes':[100],'lows':[100],'highs':[100]}),patch.object(prices.time,'sleep'),patch('trade_price_history.build',side_effect=TimeoutError('interrupted')),contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(TimeoutError):prices.fetch_us('test',{'data':str(d),'prices':str(p)})
            saved=json.loads(p.read_text());self.assertEqual(saved['tradePrices'],ledger);self.assertEqual(saved['quotes']['OLD'],quote('OLD'))

    def test_disk_quote_cache_is_shared_across_calls_and_checks_symbol(self):
        import batch_market_data as market,time
        from unittest.mock import Mock
        result={'meta':{'symbol':'TEST','currency':'USD','regularMarketPrice':10,'regularMarketTime':int(time.time())},'timestamp':[int(time.time())],'indicators':{'quote':[{'close':[10],'high':[11],'low':[9]}]}}
        response=Mock();response.json.return_value={'chart':{'result':[result]}}
        with tempfile.TemporaryDirectory() as tmp,patch('requests.get',return_value=response) as get:
            a=market.prefetch_quotes(['TEST'],root=Path(tmp));b=market.prefetch_quotes(['TEST'],root=Path(tmp))
            self.assertEqual(a['TEST']['c'],b['TEST']['c']);self.assertEqual(get.call_count,1)
            path=next((Path(tmp)/'.cache/live-quotes').glob('*.json'));bad=json.loads(path.read_text());bad['symbol']='WRONG';path.write_text(json.dumps(bad))
            market.prefetch_quotes(['TEST'],root=Path(tmp));self.assertEqual(get.call_count,2)
