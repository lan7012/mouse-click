import os
import json
import urllib.request
import urllib.error

TOKEN = os.environ.get('GITHUB_TOKEN')
if not TOKEN:
    raise SystemExit('Missing GITHUB_TOKEN')

req = urllib.request.Request(
    'https://api.github.com/user',
    headers={
        'Authorization': f'token {TOKEN}',
        'Accept': 'application/vnd.github+json'
    }
)
try:
    with urllib.request.urlopen(req) as resp:
        print('OK')
        print('Scopes:', resp.getheader('X-OAuth-Scopes'))
        print(resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print('ERROR', e.code)
    print(e.read().decode('utf-8'))
    raise
