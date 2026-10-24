"""Refresh a venture investor's official project associations and dated SEC filings.

Project associations are not security positions. Unknown ownership, valuation,
cost and performance remain unknown; changes in the directory are observations.
"""
import hashlib
import json
from pathlib import Path
import re
from datetime import datetime, timezone
from urllib.parse import urlsplit, urljoin
import urllib.request

ROOT = Path(__file__).resolve().parent

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent':'13F-Tracker guoziyuan@xiaohongshu.com'})
    with urllib.request.urlopen(req, timeout=35) as response:
        return response.read()

def project_links(raw, source):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(raw, 'html.parser')
    # The reviewed official biography explicitly names the investor's projects.
    # Other links (colleagues, navigation and footer) cannot establish attribution.
    paragraphs = [p for p in soup.find_all('p') if 'first investor' in p.get_text(' ', strip=True).lower() and 'including' in p.get_text(' ', strip=True).lower()]
    if len(paragraphs) != 1:
        raise ValueError('Official project attribution paragraph changed; retain previous verified snapshot')
    paragraph = paragraphs[0]
    projects = []
    for anchor in paragraph.select('a[href]'):
        name = anchor.get_text(' ', strip=True)
        url = urljoin(source, anchor['href'])
        parsed = urlsplit(url)
        if not name or parsed.scheme != 'https' or not parsed.netloc or parsed.username or parsed.password:
            raise ValueError('Invalid official project identity/link')
        if name not in {p['name'] for p in projects}:
            projects.append(dict(name=name, url=url, sourceUrl=source, relationship='official_profile_association'))
    # Plain-text project names in this paragraph also carry direct attribution.
    # Keep these without inventing a company URL. The source remains the biography.
    text = paragraph.get_text(' ', strip=True)
    tail = re.split(r'\bincluding\b', text, flags=re.I)[-1].strip(' —–:')
    for label in re.split(r',|\band\b', tail):
        label = label.strip(' .—–')
        if label and len(label) < 65 and label not in {p['name'] for p in projects}:
            projects.append(dict(name=label, url=source, sourceUrl=source, relationship='official_profile_association'))
    if len(projects) < 8 or len(projects) > 80:
        raise ValueError('Official project count outside reviewed bounds')
    return projects

def sec_filings(payload, cik):
    if str(payload.get('cik', '')).lstrip('0') != str(cik).lstrip('0'):
        raise ValueError('SEC filer identity mismatch')
    recent = payload['filings']['recent']
    rows = []
    for i, form in enumerate(recent['form']):
        if not re.fullmatch(r'(?:SC 13[DG]|SCHEDULE 13[DG])(?:/A)?', form):
            continue
        accession = recent['accessionNumber'][i]
        if not re.fullmatch(r'\d{10}-\d{2}-\d{6}', accession):
            raise ValueError('Invalid SEC accession')
        document = recent['primaryDocument'][i]
        if not re.fullmatch(r'[A-Za-z0-9_./-]+', document) or '..' in document:
            raise ValueError('Invalid SEC document')
        rows.append(dict(form=form, filingDate=recent['filingDate'][i], accession=accession,
                         url=f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace("-", "")}/{document}'))
    return sorted(rows, key=lambda r:(r['filingDate'],r['accession']), reverse=True)

def refresh(config, root=ROOT, get=fetch):
    root = Path(root)
    sources = config['portfolioSources']
    projects = project_links(get(sources['profile']), sources['profile'])
    payload = json.loads(get(sources['submissions']))
    if any(form in ('13F-HR', '13F-HR/A') for form in payload['filings']['recent']['form']):
        raise ValueError('13F discovered: review the source adapter before changing portfolio mode')
    filings = sec_filings(payload, config['cik'])
    path = root/config['dataFile']
    old = json.loads(path.read_text()) if path.exists() else {}
    previous = {r['accession']:r for r in old.get('publicFilings',[])}
    for filing in filings:
        if previous.get(filing['accession'],{}).get('issuer'):
            filing['issuer'] = previous[filing['accession']]['issuer']
            continue
        raw = get(f"https://www.sec.gov/Archives/edgar/data/{int(config['cik'])}/{filing['accession']}.txt").decode('utf-8',errors='replace')
        match = re.search(r'SUBJECT COMPANY:.*?COMPANY CONFORMED NAME:\s*([^\r\n]+)', raw, re.S)
        if not match:
            raise ValueError('SEC ownership filing lacks identifiable subject company')
        filing['issuer'] = match[1].strip()
    # A discovery failure above leaves every previously published file intact.
    stamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    digest = hashlib.sha256(json.dumps(projects, sort_keys=True).encode()).hexdigest()
    snapshots = old.get('projectSnapshots', [])
    if not snapshots or snapshots[-1]['fingerprint'] != digest:
        snapshots.append(dict(observedAt=stamp, fingerprint=digest, projects=projects))
    data = dict(meta=dict(manager=config['manager'],managerCIK=config['cik'].zfill(10),notablePeople=config['people'],
                          portfolioMode='public_projects',lastUpdated=stamp,projectSource=sources['profile'],
                          filingSource=sources['submissions']),
                current=dict(quarter=stamp[:10],filingDate=None,periodEnd=None,totalValue=0,holdings=[],prevQuarter=None,previousHoldings=[]),
                history=dict(quarters=[],values=[],holdings={}),publicProjects=projects,publicFilings=filings,projectSnapshots=snapshots)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    prices = root/config['pricesFile']
    if not prices.exists():
        prices.write_text(json.dumps(dict(updatedAt=stamp,quotes={},costBasis={},portfolioMode='public_projects'),indent=2)+'\n')
    print(f"{config['id']}: {len(projects)} official associations, {len(filings)} dated ownership filings; no invented position sizes")
    return data

if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--investor',required=True);args=parser.parse_args()
    config=next(p for p in json.loads((ROOT/'investors.json').read_text())['investors'] if p['id']==args.investor)
    if config.get('portfolioMode')!='public_projects':raise ValueError('Unsupported portfolio source mode')
    refresh(config)
