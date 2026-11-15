"""Market-aware quote refresh; disclosure collection continues on closed days."""
import argparse
import datetime as dt
import os
from zoneinfo import ZoneInfo


def opening_slot(now):
    eastern=now.astimezone(ZoneInfo('America/New_York'))
    return '15 14 * * *' if eastern.dst() else '15 15 * * *'


def active_markets(now=None,calendar=None):
    now=now or dt.datetime.now(dt.timezone.utc)
    if calendar is None:
        import exchange_calendars as xc
        calendar=xc.get_calendar
    active=[]
    for market,name in [('US','XNYS'),('HK','XHKG'),('CN','XSHG')]:
        try:
            cal=calendar(name)
            session=cal.minute_to_session(now, direction='previous')
            close=cal.session_close(session).to_pydatetime()
            opened=cal.session_open(session).to_pydatetime()
            # Includes a recent close (US overnight / Asia afternoon) and live sessions.
            if opened<=now<=close+dt.timedelta(hours=8):active.append(market)
        except Exception as exc:
            # A calendar outage must not suppress real quotes indefinitely.
            print('Calendar unavailable; refresh conservatively:',market,type(exc).__name__)
            active.append(market)
    return active


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--schedule',default='');a=p.parse_args()
    now=dt.datetime.now(dt.timezone.utc)
    run=a.schedule not in ('15 14 * * *','15 15 * * *') or a.schedule==opening_slot(now)
    markets=active_markets(now)
    with open(os.environ['GITHUB_ENV'],'a') as f:
        f.write('MARKET_REFRESH='+','.join(markets)+'\n')
    with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('run='+str(run).lower()+'\n')
