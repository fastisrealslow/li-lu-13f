"""Supplement dated HKEX quantities with identified SEC investment-value facts.

Zero value (rounded dollars) is never converted into zero shares or a sale date.
"""
import argparse
from datetime import datetime, timezone
from decimal import Decimal
import html
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from fetch_13f_all import sec_fetch


def official(url):
    u=urlsplit(url)
    if u.scheme!='https' or u.netloc!='www.sec.gov' or not u.path.startswith('/Archives/edgar/data/'):
        raise ValueError('Investment-value evidence must link to SEC EDGAR')
    return u.path


def parse_values(document, watch, source):
    official(source['url'])
    contexts={}
    for match in re.finditer(r'<xbrli:context\b[^>]*>.*?</xbrli:context>',document,re.S|re.I):
        c=BeautifulSoup(match.group(),'html.parser')
        identifier=c.find('xbrli:identifier');instant=c.find('xbrli:instant')
        member=c.find('xbrldi:explicitmember',attrs={'dimension':watch.get('axis','us-gaap:InvestmentTypeAxis')})
        if identifier and instant and member and identifier.get_text().strip().zfill(10)==str(watch['cik']).zfill(10) and member.get_text().split(':')[-1]==watch['member']:
            contexts[c.find('xbrli:context')['id']]=instant.get_text().strip()
    units={}
    for match in re.finditer(r'<xbrli:unit\b[^>]*>.*?</xbrli:unit>',document,re.S|re.I):
        node=BeautifulSoup(match.group(),'html.parser')
        measures=node.find_all('xbrli:measure')
        if len(measures)==1 and measures[0].get_text().strip().split(':')[-1]=='USD':units[node.find('xbrli:unit')['id']]='USD'
    values=[]
    for match in re.finditer(r'<ix:nonfraction\b[^>]*>.*?</ix:nonfraction>',document,re.S|re.I):
        # Cheap prefilter avoids parsing thousands of unrelated IXBRL fragments.
        if watch.get('concept','us-gaap:OtherInvestments') not in match.group():continue
        node=BeautifulSoup(match.group(),'html.parser').find('ix:nonfraction')
        context=node.get('contextref');date=contexts.get(context)
        if not date or units.get(node.get('unitref'))!='USD' or node.get('name')!=watch.get('concept','us-gaap:OtherInvestments'):continue
        if date!=source['reportDate']:continue
        if str(node.get('format','')).endswith('fixed-zero'):amount=Decimal(0)
        else:
            text=html.unescape(node.get_text()).strip().replace(',','')
            if not re.fullmatch(r'\d+(?:\.\d+)?',text):continue
            amount=Decimal(text)*(Decimal(10)**int(node.get('scale','0')))
        if node.get('sign')=='-':amount=-amount
        if amount<0:raise ValueError('Negative long investment value')
        values.append(dict(ticker=watch['ticker'],entity=watch['entity'],as_of=date,
            reported_value_usd=int(amount),precision_usd=int(Decimal(10)**(-int(node.get('decimals','0')))),
            shares=None,source_url=source['url'],filing_date=source['filingDate'],accession=source['accession'],
            verification='sec_ixbrl_investment_value',concept=node['name'],member=watch['member'],
            note='财报申报价值，不是持股数；零值可能受列报精度影响，不能据此认定精确清仓日期或股数。'))
    unique={json.dumps(v,sort_keys=True,ensure_ascii=False):v for v in values}
    if len(unique)>1:raise ValueError('Conflicting investment facts for one report date')
    return list(unique.values())


def latest_reports(watch):
    data=json.loads(sec_fetch('submissions/CIK'+str(watch['cik']).zfill(10)+'.json'))
    r=data['filings']['recent'];reports=[]
    for i,form in enumerate(r['form']):
        if form not in ('10-Q','10-K'):continue
        accession=r['accessionNumber'][i]
        reports.append(dict(accession=accession,reportDate=r['reportDate'][i],filingDate=r['filingDate'][i],
          url=f"https://www.sec.gov/Archives/edgar/data/{int(watch['cik'])}/{accession.replace('-','')}/{r['primaryDocument'][i]}"))
    return sorted(reports,key=lambda s:s['reportDate'],reverse=True)[:2]


def run(root='.'):
    root=Path(root)
    for inv in json.loads((root/'investors.json').read_text())['investors']:
        watches=inv.get('hkDisclosure',{}).get('secValueSources',[])
        if not watches:continue
        path=root/inv['hkFile'];data=json.loads(path.read_text());errors=[]
        for watch in watches:
            row=next((h for h in data['holdings'] if h['ticker']==watch['ticker']),None)
            if row is None:errors.append('HK security has no verified identity');continue
            reports=list(watch.get('seedReports',[]))
            try:reports+=latest_reports(watch)
            except Exception as exc:errors.append(str(exc))
            stored={r['accession']:r for r in row.get('financial_disclosures',[])}
            checked=set(row.get('financial_reports_checked',[]))
            for source in reports:
                if source['accession'] in checked:continue
                try:
                    records=parse_values(sec_fetch(official(source['url'])).decode('utf-8'),watch,source)
                    if records:stored[source['accession']]=records[0]
                    checked.add(source['accession'])
                except Exception as exc:errors.append(f"{source['accession']}: {exc}")
            row['financial_disclosures']=sorted(stored.values(),key=lambda r:r['as_of'])
            row['financial_reports_checked']=sorted(checked)
        data['financial_audit']={'checkedAt':datetime.now(timezone.utc).isoformat(),'status':'partial' if errors else 'checked','errors':errors}
        temp=path.with_suffix('.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');temp.replace(path)
        if errors:
            from update_status import record_source_warning
            record_source_warning('hk_disclosures',inv['id']+' 港股财报补充资料部分未核实，将自动重试')
        print(inv['id'],data['financial_audit']['status'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='.');run(p.parse_args().root)
