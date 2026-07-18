import os
import json
import urllib.request
import urllib.parse
import urllib.error

TOKEN = os.environ.get('GITHUB_TOKEN')
if not TOKEN:
    raise SystemExit('Missing GITHUB_TOKEN')

headers = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github+json',
}
req = urllib.request.Request('https://api.github.com/user/repos?per_page=100', headers=headers)
with urllib.request.urlopen(req) as resp:
    repos = json.loads(resp.read().decode('utf-8'))
    for r in repos:
        print(r['full_name'], r['name'], r['html_url'])
    print('TOTAL', len(repos))
