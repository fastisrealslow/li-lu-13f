"""Lossless, content-addressed price-ledger storage below static-host limits."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

LIMIT = 20 * 1024 * 1024
CHUNK = 4 * 1024 * 1024

def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()

def parsed(raw):
    def invalid(value):
        raise ValueError('Non-finite JSON number: '+value)
    value=json.loads(raw, parse_constant=invalid)
    if not isinstance(value,dict):raise ValueError('Price JSON must be an object')
    return value

def sequence_hash(files):
    return hashlib.sha256(''.join(f"{r['file']}\t{r['sha256']}\t{r['bytes']}\n" for r in files).encode()).hexdigest()

def manifest_files(manifest):
    if not isinstance(manifest,dict) or manifest.get('version')!=1 or manifest.get('field')!='tradePrices':raise ValueError('Invalid price shard manifest')
    files=manifest.get('files')
    if not isinstance(files,list) or not files or len(files)>256:raise ValueError('Missing or excessive price shards')
    seen=set()
    for record in files:
        if not isinstance(record,dict):raise ValueError('Invalid price shard descriptor')
        name,digest,size=record.get('file',''),record.get('sha256',''),record.get('bytes')
        if (not isinstance(name,str) or not isinstance(digest,str)
                or not re.fullmatch(r'price_shards/[a-zA-Z0-9_-]+-[a-f0-9]{64}\.json',name)
                or not re.fullmatch(r'[a-f0-9]{64}',digest) or not name.endswith('-'+digest+'.json')
                or type(size) is not int or not 0<size<=25*1024*1024 or name in seen):
            raise ValueError('Invalid price shard descriptor')
        seen.add(name)
    if 'sequenceSha256' in manifest and sequence_hash(files)!=manifest['sequenceSha256']:raise ValueError('Price shard sequence mismatch')
    return files


def referenced_shards(path):
    path=Path(path);manifest=parsed(path.read_bytes()).get('_priceShards')
    return [path.parent/record['file'] for record in manifest_files(manifest)] if manifest is not None else []

def load_prices(path):
    path=Path(path); value=parsed(path.read_bytes());manifest=value.pop('_priceShards',None)
    if manifest is None:return value
    if 'tradePrices' in value:raise ValueError('Invalid price shard manifest')
    combined={}
    files=manifest_files(manifest)
    for record in files:
        name=record.get('file','');digest=record.get('sha256','')
        raw=(path.parent/name).read_bytes()
        if len(raw)!=record.get('bytes') or hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('Price shard integrity mismatch')
        for key,item in parsed(raw).items():
            if key not in combined:combined[key]=item
            elif isinstance(item,dict) and isinstance(combined[key],dict) and not combined[key].keys() & item.keys():combined[key].update(item)
            else:raise ValueError('Duplicate price shard member')
    if hashlib.sha256(encoded(combined)).hexdigest()!=manifest.get('sha256'):raise ValueError('Reassembled price ledger mismatch')
    value['tradePrices']=combined
    return value

def atomic(path,raw):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as f:
        temporary=f.name
        try:f.write(raw);f.flush();os.fsync(f.fileno())
        except BaseException:
            os.unlink(temporary);raise
    try:os.replace(temporary,path)
    finally:
        if os.path.exists(temporary):os.unlink(temporary)

def write_prices(path,value,limit=LIMIT,chunk_size=CHUNK):
    path=Path(path);value=copy.deepcopy(value)
    if '_priceShards' in value:raise ValueError('Write hydrated prices, not a manifest')
    raw=encoded(value)
    if len(raw)<=limit:atomic(path,raw+b'\n');return
    ledger=value.pop('tradePrices',None)
    if not isinstance(ledger,dict):raise ValueError('Oversized prices have no splittable ledger')
    parts=[]
    for key,item in ledger.items():
        if not isinstance(item,dict):parts.append({key:item});continue
        batch={};size=len(encoded({key:{}}))
        for member,entry in item.items():
            entry_size=len(encoded({member:entry}))
            if entry_size>limit:raise ValueError('Single ledger record exceeds asset limit')
            if batch and size+entry_size>chunk_size:
                parts.append({key:batch});batch={};size=len(encoded({key:{}}))
            batch[member]=entry;size+=entry_size
        parts.append({key:batch})
    records=[];prepared=[]
    for part in parts:
        body=encoded(part);digest=hashlib.sha256(body).hexdigest();name=f'price_shards/{path.stem}-{digest}.json'
        if len(body)>limit:raise ValueError('Single price shard exceeds asset limit')
        prepared.append((name,body));records.append(dict(file=name,sha256=digest,bytes=len(body)))
    value['_priceShards']=dict(version=1,field='tradePrices',sha256=hashlib.sha256(encoded(ledger)).hexdigest(),files=records,sequenceSha256=sequence_hash(records))
    manifest_files(value['_priceShards'])
    raw=encoded(value)
    if len(raw)>limit:raise ValueError('Price metadata still exceeds asset limit')
    # Verify the complete write plan before publishing any new files.
    for name,body in prepared:atomic(path.parent/name,body)
    atomic(path,raw+b'\n')

def prepare(root):
    root=Path(root)
    for person in parsed((root/'investors.json').read_bytes())['investors']:
        p=root/person['pricesFile'];before=load_prices(p)
        if p.stat().st_size>LIMIT:write_prices(p,before)
        metadata=parsed(p.read_bytes());manifest=metadata.get('_priceShards')
        if manifest is not None and 'sequenceSha256' not in manifest:
            manifest['sequenceSha256']=sequence_hash(manifest_files(manifest))
            atomic(p,encoded(metadata)+b'\n')
        if load_prices(p)!=before:raise ValueError('Price round-trip changed financial data')
    oversized=[str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and not {'.git','.cache','.archive-work'} & set(p.relative_to(root).parts) and p.stat().st_size>25*1024*1024]
    if oversized:raise ValueError('Oversized publication assets: '+', '.join(oversized))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',default=Path(__file__).parent);args=parser.parse_args();prepare(args.root)
