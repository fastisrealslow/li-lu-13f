"""Seed issuer labels and ETF types from Nasdaq's published listing directories.

Keep reviewed translations; an official English proper name is preferable to
an invented Chinese name or thousands of slow per-symbol metadata lookups.
"""
import csv,io,json,re
from datetime import datetime,timezone
from pathlib import Path

URLS=['https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt','https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt']

def parse_directory(text,url):
    if 'Security Name|' not in text or 'File Creation Time:' not in text:raise ValueError('Incomplete Nasdaq directory')
    result={}
    for row in csv.DictReader(io.StringIO(text),delimiter='|'):
        ticker=row.get('Symbol') or row.get('ACT Symbol');name=row.get('Security Name')
        if not ticker or not name or row.get('Test Issue')!='N' or row.get('ETF') not in ('Y','N'):continue
        if not re.fullmatch(r'[A-Za-z0-9.$/-]+',ticker):continue
        result[ticker]={'cnName':re.sub(r' - (?:Common Stock|Common Shares|Ordinary Shares)$','',name),'sector':'ETF' if row['ETF']=='Y' else '其他','metadataSource':url,'metadataCheckedAt':datetime.now(timezone.utc).isoformat(),'etf':row['ETF']=='Y'}
    if len(result)<100:raise ValueError('Directory unexpectedly short')
    return result

def seed(cache,get=None,tickers=None):
    if get is None:
        import requests
        def get(url):
            r=requests.get(url,timeout=25);r.raise_for_status();return r.text
    for url in URLS:
        try:
            for ticker,entry in parse_directory(get(url),url).items():
                if tickers is not None and ticker not in tickers:continue
                old=cache.get(ticker,{})
                cache[ticker]={**entry,**old}
                if entry['etf']:cache[ticker]['sector']='ETF'
        except Exception as exc:print('Listing metadata retained:',type(exc).__name__)
    return cache
