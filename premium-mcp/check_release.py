"""Check both MCP boundaries using credentials supplied only through the environment."""
import argparse
import json
import os
import re
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Mcp:
    def __init__(self, url, token=None):
        location = urlsplit(url)
        if location.scheme != 'https' or not location.hostname or location.username or location.password or location.fragment:
            raise ValueError('Use an HTTPS MCP URL without embedded credentials or fragments')
        self.url = url
        self.token = token
        self.session = None
        self.protocol = '2025-06-18'
        self.opener = build_opener(NoRedirects)
        self.request_id = 0

    def request(self, method, params=None, notification=False):
        self.request_id += 1
        message = {'jsonrpc': '2.0', 'method': method}
        if params is not None:
            message['params'] = params
        if not notification:
            message['id'] = self.request_id
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream',
                   'MCP-Protocol-Version': self.protocol}
        if self.token:
            headers['Authorization'] = 'Bearer ' + self.token
        if self.session:
            headers['Mcp-Session-Id'] = self.session
        request = Request(self.url, data=json.dumps(message).encode(), headers=headers, method='POST')
        try:
            reply = self.opener.open(request, timeout=18)
        except HTTPError as error:
            reply = error
        with reply:
            status = reply.status
            self.session = reply.headers.get('Mcp-Session-Id', self.session)
            if status in (401, 402, 403) or notification:
                return status, {}
            if 'text/event-stream' in reply.headers.get('Content-Type', ''):
                for _ in range(200):
                    line = reply.readline(2_000_000)
                    if not line:
                        break
                    if line.startswith(b'data:'):
                        value = json.loads(line[5:])
                        if value.get('id') == self.request_id:
                            return status, value
                return status, {}
            raw = reply.read(2_000_001)
            if len(raw) > 2_000_000:
                raise ValueError('Response exceeds the release-check limit')
            try:
                return status, json.loads(raw)
            except ValueError:
                return status, {}

    def initialize(self):
        status, value = self.request('initialize', {
            'protocolVersion': self.protocol, 'capabilities': {},
            'clientInfo': {'name': 'investment-research-release-check', 'version': '1.0'}
        })
        if 'protocolVersion' in value.get('result', {}):
            self.protocol = value['result']['protocolVersion']
            self.request('notifications/initialized', notification=True)
        return status, value


def denied(status, value):
    if status in (401, 402, 403):
        return True
    result = value.get('result', {})
    error = value.get('error')
    if not error and not result.get('isError'):
        return False
    reason = str(error or result.get('content', ''))
    return bool(re.search(r'unauthori[sz]ed|forbidden|(?:subscription|payment|authorization) required|'
                          r'no active (?:plan|subscription)|(?:subscription|plan) expired|'
                          r'invalid (?:api key|token)|insufficient (?:entitlement|permissions)',
                          reason, re.IGNORECASE))


TOOLS = {
    'compare_investor_changes': {'ticker': 'PDD', 'format': 'csv'},
    'export_watchlist_report': {'investors': ['lilu'], 'tickers': ['PDD'], 'days': 90},
}


def check_negative(url, token=None):
    client = Mcp(url, token)
    if denied(*client.initialize()):
        return True
    return all(denied(*client.request('tools/call', {'name': name, 'arguments': args}))
               for name, args in TOOLS.items())


def check_positive(url, token):
    client = Mcp(url, token)
    status, value = client.initialize()
    if status != 200 or not value.get('result', {}).get('protocolVersion'):
        return False
    status, value = client.request('tools/list')
    names = {tool['name'] for tool in value.get('result', {}).get('tools', [])}
    if status != 200 or not TOOLS.keys() <= names:
        return False
    for name, args in TOOLS.items():
        status, value = client.request('tools/call', {'name': name, 'arguments': args})
        result = value.get('result', {})
        if status != 200 or result.get('isError') or not result.get('content', []):
            return False
        csv = result['content'][0].get('text', '')
        if 'PDD' not in csv or 'https://www.sec.gov/Archives/edgar/data/' not in csv:
            return False
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--origin', required=True)
    parser.add_argument('--gateway', required=True)
    args = parser.parse_args()
    if args.origin.rstrip('/') == args.gateway.rstrip('/'):
        parser.error('Provide the separate origin and gateway URLs')
    active = os.environ.get('MCPIZE_ACTIVE_TEST_TOKEN')
    inactive = os.environ.get('MCPIZE_INACTIVE_TEST_TOKEN')
    if active and active == inactive:
        parser.error('Use different active and inactive test credentials')
    checks = (
        ('Anonymous origin', lambda: check_negative(args.origin)),
        ('Anonymous gateway', lambda: check_negative(args.gateway)),
        ('Active subscription', lambda: check_positive(args.gateway, active) if active else None),
        ('Expired or unsubscribed account', lambda: check_negative(args.gateway, inactive) if inactive else None),
    )
    complete = True
    for name, check in checks:
        try:
            result = check()
        except Exception as error:
            # Print neither values returned by upstream nor token-bearing request URLs.
            print(f'FAIL {name} ({type(error).__name__})')
            complete = False
            continue
        print(f'{"PASS" if result else "SKIP" if result is None else "FAIL"} {name}')
        complete &= result is True
    return 0 if complete else 1


if __name__ == '__main__':
    raise SystemExit(main())
