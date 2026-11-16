"""CUSIP-bound quote-only routes for ticker reuse. Never rewrites filed history."""
from datetime import date, datetime, timezone

SOURCE='https://www.nasdaqtrader.com/TraderNews.aspx?id=ECA2026-742'
ACTION={
    'kind':'symbol_reuse_special_dividend', 'ticker':'INDV', 'quoteSymbol':'SUPN',
    'issuer':'Supernus, Inc.', 'cusip':'45579U109', 'effectiveDate':'2026-11-03',
    'preserveCost':False, 'sourceURL':SOURCE,
    'historySourceURL':'https://www.nasdaqtrader.com/TraderNews.aspx?id=DTN2026-25',
    'specialDividend':{'amount':8.13,'currency':'USD','exDate':'2026-11-03','paymentDate':'2026-11-06'},
    'note':'原 INDV 同一 CUSIP 现以 SUPN 交易；特别股息未计入收益，暂停跨事件成本比较。',
    'noteEn':'Former INDV, same CUSIP, now quoted as SUPN. Special dividend is not included in returns; cross-event cost comparisons are suspended.'
}

def transition_for(h, today=None):
    today=today or date.today()
    return ACTION if (h.get('cusip')==ACTION['cusip'] and h.get('ticker')==ACTION['ticker']
        and h.get('shareType','SH')=='SH' and not h.get('putCall')
        and today.isoformat()>=ACTION['effectiveDate']) else None

def apply(payload, holdings, fetch=None):
    """Keep quote dictionary keys/report identities unchanged. Fetch only current price.

    No history request, no share-ratio conversion, and no cash-dividend addition.
    This deliberately does not migrate any old SUPN cache or cost basis.
    """
    from quote_coverage import fresh_quote, issuer_key
    for h in holdings:
        action=transition_for(h)
        if not action:continue
        tk=h['ticker'];quotes=payload.setdefault('quotes',{});old=quotes.get(tk,{})
        payload.setdefault('corporateActions',{})[h['cusip']]=dict(action)
        # Keep raw historical trade records, but do not publish price-only returns
        # or costs spanning the special cash distribution.
        payload.get('costBasis',{}).pop(tk,None)
        payload.get('exitPerf',{}).pop(tk,None)
        if fetch is None:
            if old.get('quotedForCUSIP')!=h['cusip'] or old.get('reportedSymbol')!=tk or old.get('symbol')!=action['quoteSymbol']:
                quotes[tk]={**old,'stale':True}
            continue
        q=fetch(action['quoteSymbol'])
        boundary=datetime.fromisoformat(action['effectiveDate']).replace(tzinfo=timezone.utc).timestamp()
        if (fresh_quote(q) and q.get('symbol')==action['quoteSymbol'] and q.get('currency')=='USD'
                and q['t']>=boundary and issuer_key(q.get('verifiedName') or '')==issuer_key(action['issuer'])):
            # Do not merge provider split history from the reused symbol.
            current={k:v for k,v in q.items() if k not in ('shareActions','shareActionsSince')}
            for k in ('shareActions','shareActionsSince'):
                if k in old:current[k]=old[k]
            quotes[tk]={**current,'quotedForCUSIP':h['cusip'],'reportedSymbol':tk,'quoteTransition':dict(action)}
        else:
            # A failed refresh never makes a legacy quote fresh or changes its date.
            quotes[tk]={**old,'stale':True}
    return payload
