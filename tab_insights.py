"""Independent holdings/history facts; model output is limited to fact selection."""
from collections import Counter
import json
import math
import re

from holdings_diff import consolidate_holdings

CURRENT_FIELDS = ('ticker', 'cusip', 'shares', 'value', 'cnName', 'name', 'cls', 'putCall', 'shareType', 'sector')


def quarter_index(q):
    m = re.fullmatch(r'(\d{4}) ?Q([1-4])', q or '')
    return int(m[1])*4+int(m[2])-1 if m else None


def holdings_source(data):
    cur, meta = data.get('current', {}), data.get('meta', {})
    return dict(section='holdings', quarter=cur.get('quarter'), snapshotType=meta.get('snapshotType'),
                valueQuality=cur.get('valueQuality'), holdings=[[h.get(k) for k in CURRENT_FIELDS] for h in cur.get('holdings', [])])


def history_source(data):
    h, meta = data.get('history', {}), data.get('meta', {})
    return dict(section='history', current=holdings_source(data), transition=meta.get('reportingTransition'),
                instrumentHistoryFrom=meta.get('instrumentHistoryFrom'), instrumentHistoryTickers=meta.get('instrumentHistoryTickers'),
                quarters=h.get('quarters', []), values=h.get('values', []), verification=h.get('verification'),
                excludedValueQuarters=h.get('excludedValueQuarters', []),
                recentHoldings={q:[[r.get(k) for k in CURRENT_FIELDS] for r in rows] for q,rows in h.get('holdings',{}).items()
                    if quarter_index(q) is not None and quarter_index(data.get('current',{}).get('quarter')) is not None
                    and 0<=quarter_index(data['current']['quarter'])-quarter_index(q)<4},
                holdings={q:dict(totalValue=sum(r['value'] for r in rows) if rows and all(valid_number(r.get('value')) for r in rows) else None,
                    securities=sorted({json.dumps(identity(r),separators=(',',':'),ensure_ascii=False) for r in rows if valid_number(r.get('shares')) and r['shares']>0}))
                    for q, rows in h.get('holdings', {}).items()})


def valid_number(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) and value>=0


def money(value, currency='US$'):
    return currency + f'{value/1e6:,.2f}M'


def security_name(h, en=False):
    name = (h.get('name') if en else h.get('cnName')) or h.get('name') or h['ticker']
    suffix = (' '+h['putCall'].upper()) if h.get('putCall') else ''
    return f'{name}（{h["ticker"]}{suffix}）'


def identity(h):
    return (h.get('cusip') or h['ticker'], (h.get('putCall') or '').upper(), (h.get('shareType') or 'SH').upper())


def context(data, name, kind, texts):
    items=[dict(id=f'f{i}', text=text, change='结构事实' if kind=='holdings' else '历史事实') for i,text in enumerate(texts)]
    required=[f['id'] for f in items if any(k in f['text'][0] for k in ('期权共','历史权益披露快照','量级仍待核实','缺少或排除','申报范围在'))]
    return dict(kind=kind, investor=name, quarter=data['current']['quarter'],items=items,requiredIds=required)


def holdings_facts(data, name):
    rows = consolidate_holdings(data['current']['holdings'])
    counts = Counter((h.get('putCall') or ('PRN' if h.get('shareType', 'SH')!='SH' else 'SH')).upper() for h in rows)
    labels = [('SH','普通股','ordinary shares'), ('CALL','CALL','CALL'), ('PUT','PUT','PUT'), ('PRN','本金类证券','principal securities')]
    zh = '、'.join(f'{cn} {counts[k]} 项' for k,cn,en in labels if counts[k])
    en = ', '.join(f'{counts[k]} {label} positions' for k,cn,label in labels if counts[k])
    texts = [[f'本次披露 {len(rows)} 项证券：{zh}。不同股份类别和期权分别计数。',
              f'This filing contains {len(rows)} securities: {en}. Share classes and options are counted separately.']]
    if data.get('meta', {}).get('snapshotType'):
        texts.append(['这是历史权益披露快照，不是当前完整组合；不同记录的披露日期和估值时点不能合并解释为实时持仓。',
                      'This is a historical disclosure snapshot, not a complete current portfolio. Different disclosure and valuation dates cannot establish a live position.'])
        result = context(data,name,'holdings',texts)
        result['comparisonState']='snapshot'
        return result
    if data['current'].get('valueQuality'):
        texts.append(['申报市值量级仍待核实；这里保留证券数量，暂不解读金额、权重或集中度。',
                      'The scale of reported values remains unverified. Security counts are retained; value, weight and concentration analysis is suspended.'])
        return context(data,name,'holdings',texts)
    total = sum(h['value'] for h in rows)
    if not total: return context(data,name,'holdings',texts)
    ranked = sorted(rows,key=lambda h:h['value'],reverse=True)
    biggest=ranked[0]
    texts.append([f'最大单项证券是 {security_name(biggest)}，申报值 {money(biggest["value"])}，占本次披露 {biggest["value"]/total*100:.1f}%。',
                  f'The largest single security is {security_name(biggest, True)}, with reported value {money(biggest["value"])} and {biggest["value"]/total*100:.1f}% of this filing.'])
    top=ranked[:3]
    texts.append([f'前三大证券合计占 {sum(h["value"] for h in top)/total*100:.1f}%：'+ '、'.join(h['ticker']+((' '+h['putCall'].upper()) if h.get('putCall') else '') for h in top)+'。这是证券集中度，同一企业的不同股份可能分别列示。',
                  f'The top three securities account for {sum(h["value"] for h in top)/total*100:.1f}%: '+', '.join(h['ticker']+((' '+h['putCall'].upper()) if h.get('putCall') else '') for h in top)+'. This is security concentration; different share classes of one company can be separate positions.'])
    if counts['CALL'] or counts['PUT']:
        texts.append([f'期权共 {counts["CALL"]+counts["PUT"]} 项。13F 中期权申报值对应标的证券价值，不能当作期权权利金，也不能仅凭 PUT/CALL 判断完整对冲策略。',
                      f'There are {counts["CALL"]+counts["PUT"]} option positions. Their 13F values refer to underlying securities, not option premiums; PUT/CALL alone does not establish the full hedge strategy.'])
    return context(data,name,'holdings',texts)


def history_facts(data, name):
    history=data.get('history', {})
    if (history.get('verification') or {}).get('status')=='unverified': return context(data,name,'history',[])
    points={}
    excluded=history.get('excludedValueQuarters', [])
    for i,q in enumerate(history.get('quarters', [])):
        if quarter_index(q) is None or q in excluded: continue
        rows=history.get('holdings', {}).get(q)
        value=sum(h['value'] for h in rows)/1e6 if rows and all(valid_number(h.get('value')) for h in rows) else (history.get('values', [])+[None]*len(history.get('quarters', [])))[i]
        if valid_number(value):points[q]=value*1e6
    qs=sorted(points,key=quarter_index)
    if not qs:return context(data,name,'history',[])
    texts=[[f'可用于市值趋势的记录有 {len(qs)} 个季度，覆盖 {qs[0]} 至 {qs[-1]}。这段历史反映披露范围内证券，不是基金净值曲线。',
            f'{len(qs)} quarters are usable for the reported-value chart, from {qs[0]} to {qs[-1]}. This history covers disclosed securities, not fund NAV.']]
    transition=data.get('meta', {}).get('reportingTransition') or {}
    peak_text=None
    if transition.get('comparisonScopeChanged'):
        texts.append([f'申报范围在 {transition.get("fromQuarter", "—")} 改变。最新可绘制申报值为 {money(points[qs[-1]])}；跨主体的金额差不用于判断增长或买卖。',
                      f'The reporting scope changed in {transition.get("fromQuarter", "—")}. The latest usable reported value is {money(points[qs[-1]])}; differences across scopes are not growth or trading signals.'])
    else:
        first,last=points[qs[0]],points[qs[-1]]
        pct=f'{(last/first-1)*100:+.1f}%' if first else '—'
        texts.append([f'披露市值从 {money(first)} 变为 {money(last)}（变化 {pct}）。金额同时受价格、买卖、资金流及披露范围影响，不能当作投资回报。',
                      f'Reported value moved from {money(first)} to {money(last)} ({pct}). Prices, trading, flows and disclosure scope all affect this amount; it is not investment return.'])
        peak=max(qs,key=points.get)
        peak_text=[f'历史最高披露值出现在 {peak}：{money(points[peak])}。峰值说明已披露规模，不能证明收益率最高。',
                   f'The highest reported value was {money(points[peak])} in {peak}. This is the peak disclosed amount, not the highest investment return.']
    holding_history=history.get('holdings', {})
    current_q=data['current']['quarter']
    streaks=[]
    meta=data.get('meta', {})
    for h in consolidate_holdings(data['current']['holdings']):
        count,start,index=0,current_q,quarter_index(current_q)
        boundary=quarter_index(meta.get('instrumentHistoryFrom')) if h['ticker'] in (meta.get('instrumentHistoryTickers') or []) else None
        if transition.get('comparisonScopeChanged'):
            scope_boundary=quarter_index(transition.get('fromQuarter'))
            if scope_boundary is not None:boundary=max(boundary,scope_boundary) if boundary is not None else scope_boundary
        while index is not None:
            q=f'{index//4} Q{index%4+1}'
            if boundary is not None and index<boundary:break
            records=holding_history.get(q)
            if not isinstance(records,list) or not any(identity(r)==identity(h) and r.get('shares',0)>0 for r in records):break
            count+=1;start=q;index-=1
        if count>=2:streaks.append((count,h,start))
    if streaks:
        count,h,start=max(streaks,key=lambda x:(x[0],x[1]['value']))
        texts.append([f'当前证券中，{security_name(h)} 已连续出现在 {count} 个可核实季度披露中（{start} 至 {current_q}）。这是连续披露记录，不是逐笔持有或交易证明。',
                      f'Among current securities, {security_name(h, True)} appears in {count} consecutive verified quarterly filings ({start}–{current_q}). This establishes consecutive disclosures, not a transaction-by-transaction holding record.'])
    all_indexes={quarter_index(q) for q in qs}
    missing=[f'{i//4} Q{i%4+1}' for i in range(quarter_index(qs[0]),quarter_index(qs[-1])+1) if i not in all_indexes]
    if missing or excluded:
        texts.append([('缺少或排除的市值季度：'+'、'.join(dict.fromkeys(missing+excluded))+'。不填零、不推断清仓，也不跨缺口计算季度变化。'),
                      'Missing or excluded value quarters: '+', '.join(dict.fromkeys(missing+excluded))+'. No zero filling, inferred exits or quarter-on-quarter comparisons across gaps.'])
    if peak_text:texts.append(peak_text)
    return context(data,name,'history',texts)
