"""Evidence-bound projections for unresolved symbols, not name-based guesses.

A record binds one CUSIP/common class from its effective date. It is not an
alias for future successor securities: known symbols are never rewritten;
a changed CUSIP, class, issuer, merger or ticker reuse requires independent
source evidence. Existing corporate-action price guards remain in force.
The effective date is a lower bound, not a promise of perpetual fungibility.
"""
import copy
import json
import re
from datetime import date
from pathlib import Path


def records():
    return json.loads(Path(__file__).with_suffix('.json').read_text()).get('entries',{})


def name_key(value):
    return re.sub(r'[^A-Z0-9]','',str(value).upper())


def identity_for(row, quarter, entries=None):
    entry=(records() if entries is None else entries).get(row.get('cusip'))
    if not entry or row.get('putCall') or row.get('shareType','SH')!='SH':return None
    if row.get('cls','').strip().upper() not in entry.get('classes',[]):return None
    if name_key(row.get('name'))!=name_key(entry.get('issuer')):return None
    if not re.fullmatch(r'\d{4} Q[1-4]',quarter or ''):return None
    year,q=int(quarter[:4]),int(quarter[-1])
    try:
        end=date(year+int(q==4),1 if q==4 else q*3+1,1)
        effective=date.fromisoformat(entry['effectiveDate'])
    except (KeyError,ValueError):return None
    if effective>=end:return None
    if not re.fullmatch(r'https://www\.sec\.gov/Archives/edgar/data/\d+/[\w/-]+\.htm[l]?',entry.get('sourceURL','')):return None
    return {**entry,'cusip':row['cusip'],'method':'issuer_cusip_common_symbol_effective_date'}


def project(row,quarter,entries=None):
    evidence=identity_for(row,quarter,entries)
    if not evidence or not row.get('ticker','').startswith('?'):return row
    result=copy.deepcopy(row)
    result.setdefault('reportedIdentity',{k:row[k] for k in ('ticker','cusip','name','cls') if k in row})
    result['ticker']=evidence['ticker'];result['priceIdentityEvidence']=evidence
    return result


def quote_matches(row,quote):
    e=row.get('priceIdentityEvidence')
    if not e:return True
    return (e.get('cusip')==row.get('cusip') and e.get('ticker')==row.get('ticker')
            and quote.get('symbol')==e['ticker'] and quote.get('currency')=='USD'
            and name_key(quote.get('verifiedName'))==name_key(e['issuer']))


def browser_records_source():
    return '// Generated from verified_security_symbols.json; do not edit by hand.\n' + 'globalThis.VERIFIED_SECURITY_SYMBOL_RECORDS = ' + json.dumps(records(),ensure_ascii=False,sort_keys=True,separators=(',',':')) + ';\n'


if __name__=='__main__':
    Path(__file__).with_suffix('.js').write_text(browser_records_source())
