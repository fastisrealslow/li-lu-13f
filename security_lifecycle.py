"""Dated, source-verified security events, keyed by class-specific CUSIP."""
import json
from pathlib import Path
from datetime import date
from urllib.parse import urlsplit
import re
ROOT=Path(__file__).resolve().parent

def events(root=ROOT):
    path=Path(root)/'security_lifecycle.json'
    if not path.exists():return {}
    data=json.loads(path.read_text())['events']
    for cusip,event in data.items():
        url=urlsplit(event.get('sourceURL',''))
        if not re.fullmatch(r'[A-Z0-9]{9}',cusip) or event.get('status')!='ceased_trading' or not event.get('ticker') or url.scheme!='https' or not url.netloc or url.username or url.password:
            raise ValueError('Invalid verified security lifecycle evidence')
        date.fromisoformat(event['effectiveDate'])
        if not all(event.get(k) for k in ['reason','reasonEn','issuer']):raise ValueError('Missing lifecycle explanation')
    return data

def event_for(holding,root=ROOT):
    event=events(root).get(holding.get('cusip'))
    if event and event['ticker']==holding.get('ticker') and date.fromisoformat(event['effectiveDate'])<=date.today():return event
    return None
