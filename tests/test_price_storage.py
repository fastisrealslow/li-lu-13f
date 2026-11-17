import copy,json,tempfile,unittest
from pathlib import Path
from price_storage import load_prices,write_prices,referenced_shards

class PriceStorage(unittest.TestCase):
    def sample(self):return {'quotes':{'T':{'c':1.0}},'tradePrices':{'version':1,'entries':{str(i):{'price':i,'proof':'事实'*50} for i in range(20)},'quoteRefresh':{'T':{'day':'2026-09-30'}}}}
    def test_lossless_shards_and_rewrite_retains_rollback(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'prices.json';value=self.sample();write_prices(p,value,limit=6000,chunk_size=1000)
            old=p.read_bytes();paths=referenced_shards(p);self.assertGreater(len(paths),2);self.assertEqual(load_prices(p),value)
            new=copy.deepcopy(value);new['tradePrices']['entries']['0']['price']=999
            write_prices(p,new,limit=6000,chunk_size=1000);self.assertEqual(load_prices(p),new)
            p.write_bytes(old);self.assertEqual(load_prices(p),value);self.assertTrue(all(x.exists() for x in paths))
    def test_missing_corrupt_and_unsafe_shards_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'prices.json';write_prices(p,self.sample(),limit=6000,chunk_size=1000);chunk=referenced_shards(p)[0];chunk.write_text('{}')
            with self.assertRaises(ValueError):load_prices(p)
            manifest=json.loads(p.read_text());manifest['_priceShards']['files'][0]['file']='../secret.json';p.write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):load_prices(p)
    def test_small_legacy_and_nonfinite(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'prices.json';write_prices(p,{'quotes':{}});self.assertEqual(load_prices(p),{'quotes':{}});self.assertNotIn('_priceShards',p.read_text())
            p.write_text('{"x":NaN}')
            with self.assertRaises(ValueError):load_prices(p)
