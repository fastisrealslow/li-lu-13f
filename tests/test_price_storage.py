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

    def test_manifest_sequence_rejects_omitted_or_reordered_shards(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'prices.json';write_prices(p,self.sample(),limit=6000,chunk_size=1000)
            original=json.loads(p.read_text())
            for mutation in ('omit','reorder'):
                value=copy.deepcopy(original)
                if mutation=='omit':value['_priceShards']['files'].pop()
                else:value['_priceShards']['files'].reverse()
                p.write_text(json.dumps(value))
                with self.assertRaisesRegex(ValueError,'sequence mismatch'):load_prices(p)
                with self.assertRaisesRegex(ValueError,'sequence mismatch'):referenced_shards(p)
            # Existing manifests remain readable during rolling deployment.
            original['_priceShards'].pop('sequenceSha256');p.write_text(json.dumps(original))
            self.assertEqual(load_prices(p),self.sample())

    def test_oversized_write_retains_previous_manifest_and_creates_no_partial_shards(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'prices.json';write_prices(p,{'quotes':{}});before=p.read_bytes()
            with self.assertRaisesRegex(ValueError,'exceeds asset limit'):
                write_prices(p,{'quotes':{},'tradePrices':{'version':1,'entries':{'X':'x'*1000}}},limit=1000)
            self.assertEqual(p.read_bytes(),before)
            self.assertFalse(list(Path(d).glob('price_shards/*')))

    def test_private_cache_does_not_block_public_asset_checks(self):
        from price_storage import prepare
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'investors.json').write_text('{"investors":[{"pricesFile":"prices.json"}]}')
            write_prices(root/'prices.json',{'quotes':{}})
            for name in ('.cache','.archive-work'):
                p=root/name/'large.tmp';p.parent.mkdir()
                with p.open('wb') as f:f.truncate(26*1024*1024)
            prepare(root)
            with (root/'oversized-public.json').open('wb') as f:f.truncate(26*1024*1024)
            with self.assertRaisesRegex(ValueError,'Oversized publication assets'):prepare(root)

    def test_prepare_upgrades_legacy_manifest_without_rewriting_ledger(self):
        from price_storage import prepare
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'investors.json').write_text('{"investors":[{"pricesFile":"prices.json"}]}')
            p=root/'prices.json';write_prices(p,self.sample(),limit=6000,chunk_size=1000)
            original=json.loads(p.read_text());original['_priceShards'].pop('sequenceSha256')
            p.write_text(json.dumps(original));parts={x:x.read_bytes() for x in referenced_shards(p)}
            prepare(root)
            self.assertIn('sequenceSha256',json.loads(p.read_text())['_priceShards'])
            self.assertEqual(load_prices(p),self.sample())
            self.assertEqual({x:x.read_bytes() for x in referenced_shards(p)},parts)
            after=p.read_bytes();prepare(root);self.assertEqual(p.read_bytes(),after)
