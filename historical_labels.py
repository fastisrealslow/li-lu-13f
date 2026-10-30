"""Reviewed bilingual historical issuer labels, independent of live ticker coverage.
Labels never change security IDs, quantities, values, or infer listing status.
"""
import json
import re
from functools import lru_cache
from pathlib import Path


def normalized(value):
    return re.sub(r'\s+', ' ', str(value or '').strip()).upper()


@lru_cache(maxsize=1)
def indexes():
    entries=json.loads(Path(__file__).with_name('historical_labels.json').read_text())['entries']
    by_id,by_name={},{}
    for e in entries:
        for code in e.get('cusips',[]):
            if code in by_id: raise ValueError('Conflicting historical CUSIP label: '+code)
            by_id[code]=e
        for name in e.get('names',[]):
            key=normalized(name)
            if key in by_name: raise ValueError('Conflicting historical name label: '+name)
            by_name[key]=e
    return by_id,by_name


def apply_row(row):
    ids,names=indexes()
    entry=ids.get(row.get('cusip')) or names.get(normalized(row.get('name')))
    if not entry:return False
    fields={k:entry[k] for k in ('cnName','displayName','sector','sectorEn')}
    changed=any(row.get(k)!=v for k,v in fields.items())
    row.update(fields)
    return changed


def apply(data):
    count=0
    groups=list(data.get('history',{}).get('holdings',{}).values())
    groups += [data.get('current',{}).get(k,[]) for k in ('holdings','previousHoldings')]
    for rows in groups:
        for row in rows:count+=apply_row(row)
    return count
