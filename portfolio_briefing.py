"""Readable portfolio narratives derived from disclosed numbers, never trade motives."""
from collections import defaultdict
import re

from holdings_diff import consolidate_holdings, same_security
from portfolio_review import review, category
from tab_insights import quarter_index, valid_number, identity

SECTOR_EN={'互联网':'Internet','电商':'E-commerce','科技':'Technology','金融':'Finance','消费':'Consumer',
           '能源':'Energy','娱乐':'Entertainment','金融服务':'Financial services','半导体':'Semiconductors',
           '煤炭':'Coal','油气钻探':'Oil & gas drilling','冶金/煤炭':'Metallurgical coal',
           '医药':'Healthcare','工业':'Industrials','保险':'Insurance','综合金融':'Conglomerate',
           '金融/银行':'Banking','社交':'Social media','公用事业':'Utilities','游戏':'Gaming','教育':'Education'}


def pair(zh, en):
    return [zh, en]


def amount(n, en=False):
    if en:
        return 'US$'+f'{n/(1e9 if abs(n)>=1e9 else 1e6):,.2f}'+('B' if abs(n)>=1e9 else 'M')
    if abs(n)<10000:return f'{n:,.0f}美元'
    return f'{n/(1e8 if abs(n)>=1e8 else 1e4):,.2f}'+('亿美元' if abs(n)>=1e8 else '万美元')


def stock(h, en=False):
    name=(h.get('name') if en else h.get('cnName')) or h.get('name') or h['ticker']
    suffix=' '+h['putCall'].upper() if h.get('putCall') else (' PRN' if h.get('shareType','SH')!='SH' else '')
    return f'{name} ({h["ticker"]}{suffix})'


def pct(n):
    if 99.9<=abs(n)<100:return f'{n:.2f}'
    if 0<abs(n)<.001:return f'{n:.3g}'
    return f'{n:.1f}' if abs(n)>=1 else f'{n:.3f}'.rstrip('0').rstrip('.')


def quantity(n, en=False):
    if en or abs(n)<10000:return f'{n:,.0f}'
    return f'{n/10000:,.2f}万'


def detail(label, text):
    return dict(label=label, text=text)


def brief(headline, lead, details=None, notes=None):
    return dict(version=1, headline=headline, lead=lead, details=details or [], notes=notes or [])


def names(rows, en=False):
    return ('; ' if en else '、').join(stock(h,en) for h in rows)


def holdings_briefing(data):
    rows=consolidate_holdings(data['current']['holdings'])
    if data.get('meta',{}).get('snapshotType'):
        return brief(pair('这是历史档案，当前持仓尚不能确认','An archive, with present holdings unconfirmed'),
            pair(f'表中保留 {len(rows)} 项历史披露证券。它们可供研究过往持仓，但日期和估值时点不统一，不能合并成今天的完整组合。',
                 f'The table retains {len(rows)} historically disclosed securities. Their differing dates and valuation times do not establish a complete portfolio today.'))
    if data['current'].get('valueQuality'):
        return brief(pair('先看持有哪些证券，金额与集中度暂不下结论','Security identities are usable; value and concentration remain unresolved'),
            pair(f'本期列出 {len(rows)} 项证券，但原表申报值的量级仍待核实。股数和证券类别可以查看，金额占比目前不能可靠比较。',
                 f'This filing lists {len(rows)} securities, but the reported value scale remains unverified. Share counts and security types are visible; value percentages are not reliable.'))
    rows.sort(key=lambda h:h['value'],reverse=True)
    total=sum(h['value'] for h in rows)
    if not total:return brief(pair('本期没有可计算权重的申报金额','No reported amount available for weight analysis'),pair('保留证券记录，暂不计算组合占比。','Security records are retained without portfolio weights.'))
    top=rows[:3];top_pct=sum(h['value'] for h in top)/total*100
    headline=pair(f'前三项占 {pct(top_pct)}%，组合重心'+('集中在少数证券' if top_pct>=60 else '分布在更多证券'),
                  f'Top three: {pct(top_pct)}% — '+('a concentrated core' if top_pct>=60 else 'a broader spread of positions'))
    lead=pair(f'本期 13F 披露 {amount(total)}、{len(rows)} 项证券。{names(top)} 合计占 {pct(top_pct)}%；其余 {len(rows)-len(top)} 项合计占 {pct(100-top_pct)}%。'+('这三项是理解本期组合结构的重点。' if top_pct>=50 else '其余持仓合计仍占一半以上，不能只看前三项。'),
              f'The filing reports {amount(total,True)} across {len(rows)} securities. {names(top,True)} together represent {pct(top_pct)}%, leaving {pct(100-top_pct)}% across the other {len(rows)-len(top)} positions. '+('The leading positions therefore dominate the disclosed composition.' if top_pct>=50 else 'The rest of the portfolio still accounts for more than half.'))
    details=[];equity=[h for h in rows if not h.get('putCall') and h.get('shareType','SH')=='SH']
    groups=defaultdict(list)
    # CGS: the first six CUSIP/CINS characters identify the issuer. Keep options separate.
    for h in equity:
        cusip=h.get('cusip','')
        key=cusip[:6] if re.fullmatch(r'[A-Z0-9*@#]{8}[0-9]',cusip) else repr(identity(h))
        groups[key].append(h)
    if groups:
        group=max(groups.values(),key=lambda g:sum(h['value'] for h in g));weight=sum(h['value'] for h in group)/total*100
        details.append(detail(pair('最大普通股公司敞口','Largest ordinary-share issuer'),
            pair(f'{names(group)} 合计占申报总值 {weight:.1f}%。'+('同一发行人的不同股份类别在表中分列，这里合并看公司层面的集中度。' if len(group)>1 else '这是该普通股在已披露组合中的比重。'),
                 f'{names(group,True)} represent {weight:.1f}% of reported value. '+('Separate share classes of this issuer are combined here to show issuer concentration.' if len(group)>1 else 'This is its weight within the disclosed portfolio.'))))
    sectors=defaultdict(float)
    for h in equity:
        if h.get('sector') and h['sector'] not in ('其他','Unknown','Other'):sectors[h['sector']]+=h['value']
    if sectors:
        ranked=sorted(sectors.items(),key=lambda x:x[1],reverse=True)[:2]
        known=sum(sectors.values())/total*100
        zh='、'.join(f'{s} {v/total*100:.1f}%' for s,v in ranked)
        details.append(detail(pair('行业重心','Sector composition'),
            pair(f'普通股中申报值最多的行业是 {zh}。已识别行业覆盖申报总值 {known:.1f}%，未分类证券和期权未并入这些行业比例。',
                 'Leading ordinary-share sectors: '+', '.join(f'{SECTOR_EN.get(s,s)}: {v/total*100:.1f}%' for s,v in ranked)+f'. Classified ordinary shares cover {known:.1f}% of reported value; unclassified securities and options are outside these sector figures.')))
    small=[h for h in rows if h['value']/total<.01]
    if small:
        details.append(detail(pair('小仓位有多大','Scale of small positions'),
            pair(f'{len(small)} 项证券各自低于 1%，合计仅占 {sum(h["value"] for h in small)/total*100:.2f}%。这些记录值得保留，但不能与核心仓位等量看待。',
                 f'{len(small)} securities individually weigh less than 1%, together just {sum(h["value"] for h in small)/total*100:.2f}%. These records have a different portfolio scale from the core positions.')))
    notes=[pair('统计仅覆盖本期 13F；港股补充行按各自披露日期单列。','Figures cover this 13F filing; supplementary HK rows retain their individual disclosure dates.')]
    options=[h for h in rows if h.get('putCall')]
    if options:notes.append(pair(f'含 {len(options)} 项期权：申报值是标的证券价值，不是权利金；未与普通股公司敞口相抵。',f'{len(options)} option positions report underlying security values, not premiums; they are not netted against ordinary-share issuer exposure.'))
    return brief(headline,lead,details[:3],notes)


def share_clause(h, en=False):
    k=category(h)
    if k in ('added','trimmed'):
        p=(h['shares']/h['prevShares']-1)*100
        percentage=('+' if p>0 else '')+pct(p)
        unit=('principal' if en else '本金') if h.get('shareType','SH')!='SH' else ('underlying shares' if en else '标的股') if h.get('putCall') else ('shares' if en else '股')
        return stock(h,en)+(f': {quantity(h["prevShares"],True)} → {quantity(h["shares"],True)} {unit} ({percentage}%)' if en else f'：{quantity(h["prevShares"])} → {quantity(h["shares"])} {unit}（{percentage}%）')+(' (split adjusted)' if en and h.get('shareAdjustment') else '（拆股后可比）' if h.get('shareAdjustment') else '')
    return stock(h,en)+(': new' if en and k=='new' else ': exited this filing' if en else '：新进入本期披露' if k=='new' else '：本期不再出现')


def change_rank(h):
    if category(h)=='new':return h['value']
    if category(h)=='exited':return h.get('prevValue',0)
    return (h.get('prevValue') or 0)*abs(h['shares']/h['prevShares']-1) if h.get('prevShares') else 0


def changes_briefing(data):
    r=review(data);s=r['stats'];cur=data['current'];state=r['state']
    if state in ('snapshot','scope_changed','gap'):
        reasons={'snapshot':pair('历史快照没有完整季度对照','The archive has no complete quarterly comparison'),
                 'scope_changed':pair('本季申报范围改变，不能把差异读成交易','The reporting scope changed; differences cannot establish trades'),
                 'gap':pair('中间季度缺失，当前只能做跨期观察','A missing quarter prevents a quarter-on-quarter comparison')}
        return brief(reasons[state],pair(f'{cur["quarter"]} 的证券记录可以查看，但本页没有同一范围、相邻季度的完整对照，因此不列加减仓结论。',f'The securities in {cur["quarter"]} remain visible, but a complete comparison of adjacent quarters within the same scope is unavailable.'))
    rows=r['rows'];up=[h for h in rows if category(h) in ('new','added')];down=[h for h in rows if category(h) in ('trimmed','exited')]
    values_ok=not cur.get('valueQuality') and all(valid_number(h.get('prevValue')) and valid_number(h.get('value')) for h in rows)
    total=sum(h['value'] for h in rows);previous=sum(h.get('prevValue') or 0 for h in rows)
    new=[h for h in up if category(h)=='new'];exits=[h for h in down if category(h)=='exited']
    ranked=sorted(up+down,key=change_rank,reverse=True)
    if not up and not down:
        headline=pair('上季股数未核实，暂不判断组合调整','Prior share counts are unverified; portfolio adjustments cannot be established') if s['unknown'] else pair('已核实股数没有变化；重点看申报市值变化','Verified share counts did not change; reported value is the main difference')
    elif up and down:
        headline=pair(f'增加 {len(up)} 项、减少或退出 {len(down)} 项；重点看 '+names(ranked[:2]),
                      f'{len(up)} entries/additions and {len(down)} reductions/exits; focus on '+names(ranked[:2],True))
    else:
        headline=pair(f'本季'+(f'{len(up)} 项增加股数' if up else f'{len(down)} 项减少或退出披露')+'，核心变化在 '+names(ranked[:2]),
                      f'{len(up) if up else len(down)} '+('entries/additions' if up else 'reductions/exits')+'; the largest adjustments involve '+names(ranked[:2],True))
    if up and down and s['added']==1 and not s['new']:
        headline=pair(f'{len(down)} 项减少或退出，仅 {stock(up[0])} 增加股数',f'{len(down)} reductions/exits; only {stock(up[0],True)} added shares')
    elif up and exits and not new and len(up)<=2:
        headline=pair(f'增持集中在 {names(up)}，另有 {len(exits)} 项退出披露',f'Additions focus on {names(up,True)}; {len(exits)} positions left this filing')
    if values_ok and total and new and down and sum(h['value'] for h in new)/total<.01:
        n=sum(h['value'] for h in new)/total*100
        headline=pair(f'主要调整在旧仓；新仓合计仅占 {pct(n)}%',f'Existing positions are the main story; new positions total just {pct(n)}%')
    changes='、'.join(f'{label} {s[k]} 项' for k,label in [('new','新进入'),('added','增持'),('trimmed','减持'),('exited','退出披露')] if s[k])
    lead=pair(f'相比 {cur.get("prevQuarter") or "上季"}，'+(changes+'；' if changes else '没有已核实的股数增减；')+f'{s["hold"]} 项股数不变。'+('组合名单未变，没有新仓或退出。' if r['complete'] and not s['new'] and not s['exited'] and not s['unknown'] else ''),
              f'Compared with {cur.get("prevQuarter") or "the previous filing"}: {s["new"]} new, {s["added"]} added, {s["trimmed"]} reduced, {s["exited"]} exited, and {s["hold"]} unchanged share counts.')
    details=[];notes=[]
    if values_ok and previous:
        change=total-previous;p=change/previous*100
        lead[0]+=f'申报市值由 {amount(previous)} 变为 {amount(total)}（{p:+.1f}%，净'+('增加' if change>=0 else '减少')+f' {amount(abs(change))}）；金额变化与股数变化需要分开读。'
        lead[1]+=f' Reported value moved from {amount(previous,True)} to {amount(total,True)} ({p:+.1f}%, a net '+('increase' if change>=0 else 'decrease')+f' of {amount(abs(change),True)}); this amount is distinct from share-count changes.'
        contributors=sorted([h for h in rows if (h['value']-h['prevValue'])*(1 if change>=0 else -1)>0],key=lambda h:abs(h['value']-h['prevValue']),reverse=True)[:3]
        if contributors:
            n=sum(abs(h['value']-h['prevValue']) for h in contributors)
            unchanged=[h for h in contributors if category(h)=='hold']
            details.append(detail(pair('金额变化集中在哪里','Where reported value changed'),
                pair(f'{names(contributors)} 合计'+('增加' if change>=0 else '减少')+f'申报值 {amount(n)}。'+(f'其中 {names(unchanged)} 股数未变，这部分金额变化不能算作'+('加仓。' if change>=0 else '减仓。') if unchanged else '这反映申报金额的变化，不是实际成交金额。'),
                     f'{names(contributors,True)} together '+('increased' if change>=0 else 'decreased')+f' their reported values by {amount(n,True)}. '+(f'{names(unchanged,True)} had unchanged shares; their value changes are not additions or reductions.' if unchanged else 'These are reported-value differences, not transaction amounts.'))))
            opposing=[h for h in rows if h.get('prevShares') and h.get('prevValue') and category(h) in ('added','trimmed') and (h['shares']-h['prevShares'])*(h['value']-h['prevValue'])<0]
            if opposing:
                opposite=max(opposing,key=lambda h:abs(h['value']-h['prevValue']))
                sp=(opposite['shares']/opposite['prevShares']-1)*100;vp=(opposite['value']/opposite['prevValue']-1)*100
                details[-1]['text'][0]+=f'尤其是 {stock(opposite)}：股数'+('增加' if sp>0 else '减少')+f' {pct(abs(sp))}%，申报市值却'+('增加' if vp>0 else '减少')+f' {pct(abs(vp))}%，两项方向相反。'
                details[-1]['text'][1]+=f' In particular, {stock(opposite,True)} changed shares by '+('+' if sp>0 else '')+f'{pct(sp)}%, while reported value changed by '+('+' if vp>0 else '')+f'{pct(vp)}% — opposite directions.'
    for label,group in [(pair('增加股数的重点','Main share additions'),up),(pair('减少与退出的重点','Main reductions and exits'),down)]:
        selected=sorted(group,key=change_rank,reverse=True)[:2]
        if not selected:continue
        zh='；'.join(share_clause(h) for h in selected)+'。'
        en='; '.join(share_clause(h,True) for h in selected)+'.'
        if values_ok:
            for h in selected:
                if h['shares'] and total:
                    w=h['value']/total*100
                    zh+=f'{h["ticker"]} 本期占 {pct(w)}%。'
                    en+=f' {h["ticker"]} now weighs {pct(w)}%.'
        details.append(detail(label,pair(zh,en)))
    if values_ok and total and (new or exits):
        n=sum(h['value'] for h in new)/total*100;e=sum(h['prevValue'] for h in exits)/previous*100 if previous else None
        lead[0]+=('、'.join(([f'新仓合计占本期 {pct(n)}%'] if new else [])+([f'退出项原占上期 {pct(e)}%'] if exits and e is not None else [])))+'。'+('新仓体量很小，主要变化仍应看旧仓。' if new and n<1 else '')
        lead[1]+=f' New positions total {pct(n)}% of this filing'+(f'; exited positions were {pct(e)}% of the prior filing' if e is not None else '')+'.'+(' The new positions are small; existing holdings remain the main story.' if new and n<1 else '')
    if s['unknown']:
        lead[0]+=f'另有 {s["unknown"]} 项上季股数未知，未计入买卖方向。';lead[1]+=f' {s["unknown"]} prior share counts are unknown and have no assigned trade direction.'
    if state=='partial':notes.append(pair('上季完整申报缺失，已核实变化可看，退出数量未必完整。','The complete prior filing is missing; known changes remain visible, but exits may be incomplete.'))
    if cur.get('valueQuality'):notes.append(pair('申报值量级待核实，仅总结股数，不比较金额或权重。','Reported value scale is unresolved; only share counts are compared.'))
    if any(h.get('putCall') for h in rows):notes.append(pair('期权行的股数与申报值指其标的证券，不是期权权利金。','Option rows compare underlying shares and reported values, not option premiums.'))
    notes.append(pair('股数按披露净变化；金额不是成交资金。全部变动名单保留在下方。','Share counts are net disclosure differences; value changes are not transaction cash flows. Complete changes follow below.'))
    return brief(headline,lead,details[:3],notes)


def history_briefing(data):
    h=data.get('history',{});cur=data['current'];meta=data.get('meta',{})
    if (h.get('verification') or {}).get('status')=='unverified':
        return brief(pair('历史记录不足，暂不描绘增长轨迹','The archive cannot establish a reliable growth history'),pair('现有档案缺少可比、带日期的季度快照；因此不把它画成连续组合曲线，也不推断历史收益。','Comparable, dated quarterly snapshots are missing, so a continuous portfolio chart or historical return cannot be established.'))
    points={}
    for i,q in enumerate(h.get('quarters',[])):
        if q in h.get('excludedValueQuarters',[]) or quarter_index(q) is None:continue
        rows=h.get('holdings',{}).get(q)
        v=sum(r['value'] for r in rows) if rows and all(valid_number(r.get('value')) for r in rows) else (h.get('values',[])+[None]*len(h.get('quarters',[])))[i]
        if not rows and valid_number(v):v*=1e6
        if rows and not all(valid_number(r.get('value')) for r in rows) and valid_number(v):v*=1e6
        if valid_number(v):points[q]=v
    qs=sorted(points,key=quarter_index)
    if not qs:return brief(pair('暂无可比历史记录','No comparable history available'),pair('后续取得历史季度后再总结演变。','Historical evolution will be summarized when quarterly records become available.'))
    transition=meta.get('reportingTransition',{})
    if transition.get('comparisonScopeChanged'):
        return brief(pair('申报范围已改变，历史金额需分段阅读','The reporting scope changed; read the history in separate segments'),
            pair(f'申报范围在 {transition.get("fromQuarter","—")} 改变。最近可核实季度 {qs[-1]} 披露 {amount(points[qs[-1]])}；与旧主体的差额不能解释成组合增长或交易。',
                 f'The reporting scope changed in {transition.get("fromQuarter","—")}. The latest verified quarter, {qs[-1]}, reports {amount(points[qs[-1]],True)}; differences from the old scope do not establish growth or trades.'))
    recent=[];idx=quarter_index(cur['quarter'])
    instrument_boundary=quarter_index(meta.get('instrumentHistoryFrom')) if any(r['ticker'] in meta.get('instrumentHistoryTickers',[]) for r in cur['holdings']) else None
    byidx={quarter_index(q):q for q in qs}
    for n in range(idx,idx-4,-1):
        if instrument_boundary is not None and n<instrument_boundary:break
        if n not in byidx:break
        recent.insert(0,byidx[n])
    details=[];notes=[];current=consolidate_holdings(cur['holdings']);ranked=sorted(current,key=lambda r:r['value'],reverse=True)
    start,end=(recent[0],recent[-1]) if len(recent)>=2 else (qs[-1],qs[-1])
    current_ids={identity(r) for r in current if r['shares']>0}
    first_rows=h.get('holdings',{}).get(start)
    verified_rows=first_rows is not None and all(q in h.get('holdings',{}) for q in recent)
    if verified_rows:
        first_positions=consolidate_holdings([r for r in first_rows if r['shares']>0])
        first_ids={identity(r) for r in first_positions}
        remaining=list(first_positions);retained=0
        for r in current:
            if r['shares']<=0:continue
            match=next((i for i,p in enumerate(remaining) if same_security(r,p)),None)
            if match is not None:retained+=1;remaining.pop(match)
        entered=len(current_ids)-retained;left=len(first_ids)-retained
        headline=pair(f'最近 {len(recent)} 个连续季度：保留 {retained} 项，新增 {entered} 项、退出 {left} 项',
                      f'Last {len(recent)} consecutive quarters: {retained} retained, {entered} entered and {left} left') if len(recent)>=2 else pair('历史覆盖存在缺口，先看最近可核实的一段','History has gaps; start with the latest verified segment')
    else:headline=pair('先看最近连续记录，再看长期规模','Read the recent continuous record before the long-term scale')
    if len(recent)>=2:
        a,b=points[start],points[end];p=(b/a-1)*100 if a else None
        lead=pair(f'{start} 至 {end}，申报市值从 {amount(a)} 变为 {amount(b)}'+(f'（{p:+.1f}%）' if p is not None else '')+'。',
                  f'From {start} to {end}, reported value moved from {amount(a,True)} to {amount(b,True)}'+(f' ({p:+.1f}%)' if p is not None else '')+'.')
        if verified_rows:
            lead[0]+=f'当前 {len(current_ids)} 项持仓中，{retained} 项在这段起点已经出现；证券数量由 {len(first_ids)} 项变为 {len(current_ids)} 项。'
            lead[1]+=f' Of {len(current_ids)} current positive-share securities, {retained} were present at the start; the count moved from {len(first_ids)} to {len(current_ids)}.'
        persistent=[]
        for r in ranked:
            if all(any(same_security(p,r) and p['shares']>0 for p in h['holdings'].get(q,[])) for q in recent):persistent.append(r)
        if persistent:details.append(detail(pair('哪些核心证券持续出现','Core securities that persist'),pair(f'{names(persistent[:2])} 在这 {len(recent)} 个季度均有披露。持续出现说明组合核心的延续，不能证明期间从未交易。',f'{names(persistent[:2],True)} appear in all {len(recent)} quarters. This shows continuity in the disclosed core, not an absence of trading between filings.')))
        old=consolidate_holdings(first_rows or []);old_total=sum(r['value'] for r in old)
        if old_total and not cur.get('valueQuality'):
            before=sum(r['value'] for r in sorted(old,key=lambda r:r['value'],reverse=True)[:3])/old_total*100
            now=sum(r['value'] for r in ranked[:3])/sum(r['value'] for r in ranked)*100 if ranked and sum(r['value'] for r in ranked) else 0
            details.append(detail(pair('集中度怎样变化','How concentration changed'),pair(f'前三大证券占比由 {before:.1f}% 变为 {now:.1f}%，'+('提高' if now>=before else '下降')+f' {abs(now-before):.1f} 个百分点。'+('头部证券占比更高。' if now-before>=1 else '组合占比分布更分散。' if before-now>=1 else '头部占比基本稳定。'),f'The top-three weight moved from {before:.1f}% to {now:.1f}%, a {abs(now-before):.1f}-percentage-point '+('increase.' if now>=before else 'decrease.'))))
    else:
        lead=pair(f'最近可核实市值为 {qs[-1]} 的 {amount(points[qs[-1]])}。当前报告期附近缺少连续可比金额，暂不拼接成最近季度增长。',f'The latest verified value is {amount(points[qs[-1]],True)} in {qs[-1]}. Recent consecutive comparable amounts are missing; no recent-quarter growth is inferred.')
    peak=max(qs,key=points.get)
    details.append(detail(pair('长期规模的位置','Position in the longer record'),pair(f'全部可用记录覆盖 {qs[0]} 至 {qs[-1]}（{len(qs)} 个季度）。最高申报值在 {peak}，为 {amount(points[peak])}；'+('最新值即为该峰值。' if points[peak]==points[qs[-1]] else f'最新值较峰值低 {(1-points[qs[-1]]/points[peak])*100:.1f}%。'),f'The record spans {qs[0]}–{qs[-1]} ({len(qs)} usable quarters). Peak reported value: {amount(points[peak],True)} in {peak}; '+('the latest value equals that peak.' if points[peak]==points[qs[-1]] else f'the latest is {(1-points[qs[-1]]/points[peak])*100:.1f}% below it.'))))
    missing=[f'{n//4} Q{n%4+1}' for n in range(quarter_index(qs[0]),quarter_index(qs[-1])+1) if n not in byidx]
    if missing or h.get('excludedValueQuarters'):
        gaps=list(dict.fromkeys(missing+h.get('excludedValueQuarters',[])))
        notes.append(pair('缺少或排除的金额季度：'+'、'.join(gaps)+'。图表在缺口断开。','Missing/excluded value quarters: '+', '.join(gaps)+'. The chart breaks at these gaps.'))
    notes.append(pair('这里是披露证券的市值与结构变化，不是基金净值或投资回报。','This is evolution in disclosed security values and composition, not fund NAV or investment return.'))
    return brief(headline,lead,details[:3],notes)
