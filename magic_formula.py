"""Auditable Greenblatt calculations from issuer financial statements.

All amounts are in the report currency's base unit. Quotes are separate from
financial evidence. Missing facts never default to zero, and a non-positive
denominator never becomes an infinite or misleading ranking score.
"""
import math
import re
from urllib.parse import urlsplit

VERSION = 1
BALANCE_FIELDS = (
    'currentAssets', 'cash', 'restrictedCash', 'currentFinancialAssets',
    'currentLiabilities', 'currentDebt', 'noncurrentDebt',
    'currentLeases', 'noncurrentLeases', 'ppe', 'rou',
    'operatingInvestmentProperty', 'landUseRights', 'minorityInterest', 'preferredEquity',
    'currentNonOperatingLiabilities', 'otherNonOperatingCurrentAssets', 'noncurrentCashLike',
)
OFFICIAL_HOSTS = {
    'www.sec.gov', 'www.hkexnews.hk', 'www1.hkexnews.hk',
    'static.cninfo.com.cn', 'ir.tongrentangcm.com', 'doc.irasia.com',
    'www.langhamhospitality.com', 'www.vivagoods.hk',
}


def number(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError('Missing or non-finite financial input')
    return value


def amount(facts, name):
    return number(facts[name]['value'])


def financial_components(period):
    f = period['facts']
    operating_profit = amount(f, 'operatingProfit')
    adjustments = period.get('ebitAdjustments', [])
    ebit = operating_profit + sum(number(a['value']) for a in adjustments)
    current_finance = amount(f, 'currentDebt') + amount(f, 'currentLeases') + amount(f, 'currentNonOperatingLiabilities')
    excluded_assets = sum(amount(f, k) for k in ('cash', 'restrictedCash', 'currentFinancialAssets', 'otherNonOperatingCurrentAssets'))
    operating_assets = amount(f, 'currentAssets') - excluded_assets
    operating_liabilities = amount(f, 'currentLiabilities') - current_finance
    working_capital = operating_assets - operating_liabilities
    fixed_capital = sum(amount(f, k) for k in ('ppe', 'rou', 'operatingInvestmentProperty', 'landUseRights'))
    debt = sum(amount(f, k) for k in ('currentDebt', 'noncurrentDebt', 'currentLeases', 'noncurrentLeases'))
    # Only explicitly identified unrestricted cash/deposits/marketable
    # securities offset EV. Restricted cash and long-term equity holdings do
    # not. The financial-asset detail must sum to its balance-sheet total.
    cash_like = amount(f, 'cash') + number(period['evCashLikeFinancialAssets']['value']) + amount(f, 'noncurrentCashLike')
    return dict(ebit=ebit, operatingProfit=operating_profit,
        operatingCurrentAssets=operating_assets,
        operatingCurrentLiabilities=operating_liabilities,
        workingCapital=working_capital, fixedCapital=fixed_capital,
        investedCapital=working_capital+fixed_capital,
        debt=debt, cashLike=cash_like)


def calculate(company, quote, years=1):
    periods = sorted(company['annuals'], key=lambda x: x['end'], reverse=True)[:years]
    if len(periods) != years:
        return {'status': 'incomplete', 'reason': f'需要 {years} 个完整年度财报','quote':quote,'years':years}
    if any(p['months'] != 12 for p in periods):
        return {'status': 'incomplete', 'reason': '不能把半年财报当作全年','quote':quote,'years':years}
    ends=[int(p['end'][:4]) for p in periods]
    if years > 1 and ends != list(range(ends[0],ends[0]-years,-1)):
        return {'status': 'incomplete', 'reason': '三年财报年度不连续','quote':quote,'years':years}
    parts = [financial_components(p) for p in periods]
    ebit = sum(p['ebit'] for p in parts)/years
    capital = sum(p['investedCapital'] for p in parts)/years
    latest = financial_components(company.get('latestBalance') or periods[0])
    price, rate = number(quote['price']), number(quote['fxToReportCurrency'])
    shares = amount((company.get('latestBalance') or periods[0])['facts'], 'ordinaryShares')
    ratio = number(quote['ordinarySharesPerQuoteUnit'])
    if min(price, rate, shares, ratio) <= 0:
        raise ValueError('Invalid price, share count, FX or ADS ratio')
    equity = price*rate*shares/ratio
    current_facts=(company.get('latestBalance') or periods[0])['facts']
    ev = equity+latest['debt']+amount(current_facts,'minorityInterest')+amount(current_facts,'preferredEquity')-latest['cashLike']
    reasons=[]
    if ebit <= 0: reasons.append('经营利润为零或亏损')
    if capital <= 0: reasons.append('投入资本非正数，资本回报率不适用')
    if ev <= 0: reasons.append('企业价值非正数，盈利收益率不适用')
    return dict(status='ranked' if not reasons else 'not_ranked',reason='；'.join(reasons),
        capitalCaution=('三年平均资本为正，但有年度的投入资本非正数；比率对经营负债变化敏感' if years==3 and capital>0 and any(p['investedCapital']<=0 for p in parts) else ''),
        years=years,periods=[p['end'][:4] for p in periods],ebit=ebit,
        investedCapital=capital,enterpriseValue=ev,equityValue=equity,
        earningsYield=ebit/ev if ev>0 else None,
        returnOnCapital=ebit/capital if capital>0 else None,
        annualComponents=parts,balanceComponents=latest,quote=quote)


def rank(results):
    for r in results:
        for k in ('earningsRank','capitalRank','rankSum','overallRank'):r.pop(k,None)
    eligible=[r for r in results if r.get('status')=='ranked']
    for metric, field in [('earningsYield','earningsRank'),('returnOnCapital','capitalRank')]:
        ordered=sorted(eligible,key=lambda r:-r[metric])
        previous=None;place=0
        for i,r in enumerate(ordered,1):
            if previous is None or not math.isclose(r[metric],previous,rel_tol=1e-12,abs_tol=1e-12):place=i
            r[field]=place;previous=r[metric]
    for r in eligible:r['rankSum']=r['earningsRank']+r['capitalRank']
    ordered=sorted(eligible,key=lambda r:(r['rankSum'],r.get('id','')))
    previous=None;place=0
    for i,r in enumerate(ordered,1):
        if previous!=r['rankSum']:place=i
        r['overallRank']=place;previous=r['rankSum']
    return ordered + [r for r in results if r.get('status')!='ranked']


def validate_company(company):
    sources=company['sources']
    for listing in company.get('listings',[]):
        if listing['ordinarySharesPerQuoteUnit']>1:
            proof=company.get('adsConversion',{})
            if proof.get('value')!=listing['ordinarySharesPerQuoteUnit'] or proof.get('sourceId') not in sources or not proof.get('evidence'):
                raise ValueError('ADS ratio needs original-report evidence')
    for sid,source in sources.items():
        url=urlsplit(source['url'])
        if url.scheme!='https' or url.hostname not in OFFICIAL_HOSTS:
            raise ValueError('Financial inputs must link to original issuer/SEC/HKEX/CNINFO reports')
        if source.get('kind') not in ('annual_report','interim_report','financial_results') or not re.fullmatch(r'[a-f0-9]{64}',source.get('sha256','')):
            raise ValueError('Missing financial-report identity or content digest')
    for p in company['annuals']+([company['latestBalance']] if company.get('latestBalance') else []):
        required=BALANCE_FIELDS+('operatingProfit',)
        if p is (company.get('latestBalance') or max(company['annuals'],key=lambda a:a['end'])):
            required+=('ordinaryShares',)
        for key in required:
            f=p['facts'][key];number(f['value'])
            if f.get('sourceId') not in sources or not f.get('label') or not f.get('evidence'):
                raise ValueError('Missing row-level source evidence: '+key)
            if key!='operatingProfit' and f['value']<0:
                raise ValueError('Negative balance sheet fact: '+key)
        detail=p['evCashLikeFinancialAssets'];number(detail['value'])
        if detail.get('sourceId') not in sources or not detail.get('evidence'):
            raise ValueError('Missing EV cash-deduction evidence')
        if detail['value']<0 or detail['value']>amount(p['facts'],'currentFinancialAssets')+.01:
            raise ValueError('EV deduction must be backed by the current financial-asset breakdown')
        for a in p.get('ebitAdjustments',[]):
            number(a['value'])
            if a.get('sourceId') not in sources or not a.get('evidence'):raise ValueError('Unsupported EBIT adjustment')
        if sum(amount(p['facts'],k) for k in ('cash','restrictedCash','currentFinancialAssets','otherNonOperatingCurrentAssets'))>amount(p['facts'],'currentAssets')+.01:
            raise ValueError('Financial assets exceed current assets (possible duplicate deposits)')
        if sum(amount(p['facts'],k) for k in ('currentDebt','currentLeases','currentNonOperatingLiabilities'))>amount(p['facts'],'currentLiabilities')+.01:
            raise ValueError('Current financing exceeds current liabilities')
        financial_components(p)


def validate_dataset(data):
    if data.get('version')!=VERSION:raise ValueError('Unsupported personal portfolio version')
    companies=data['companies']
    if len({c['id'] for c in companies})!=len(companies):raise ValueError('Duplicate holdings')
    for c in companies:
        validate_company(c)
        for ticker,group in c.get('results',{}).items():
            listing=next((l for l in c['listings'] if l['ticker']==ticker),None)
            if not listing:raise ValueError('Quote is not a configured holding listing')
            for window,result in group.items():
                q=result['quote']
                if q['currency']!=listing['currency'] or q['ordinarySharesPerQuoteUnit']!=listing['ordinarySharesPerQuoteUnit']:
                    raise ValueError('Quote currency / ADS conversion does not match the report-backed listing')
                if not re.match(r'^\d{4}-\d{2}-\d{2}',q.get('asOf','')) or not q.get('sourceUrl'):
                    raise ValueError('Missing dated quote provenance')
                rebuilt=calculate(c,result['quote'],int(window))
                if result['status']!=rebuilt['status']:raise ValueError('Published eligibility does not match financial inputs')
                for field in ['ebit','investedCapital','enterpriseValue','equityValue','earningsYield','returnOnCapital']:
                    a,b=result.get(field),rebuilt.get(field)
                    if a is None and b is None:continue
                    if a is None or b is None or not math.isclose(a,b,rel_tol=1e-10,abs_tol=.001):raise ValueError('Published calculation does not match report facts: '+c['id']+' '+field)
