import os
import json
import urllib.request
import urllib.error

TOKEN = os.environ.get('GITHUB_TOKEN')
if not TOKEN:
    raise SystemExit('Missing GITHUB_TOKEN')

url = 'https://api.github.com/user/repos'
headers = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github+json',
    'Content-Type': 'application/json'
}
data = json.dumps({
    'name': 'mouse-click',
    'private': False,
    'description': 'Windows 自动点击工具',
    'auto_init': False,
}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers=headers, method='POST')
try:
    with urllib.request.urlopen(req) as resp:
        print('ok')
        print(resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print('error', e.code)
    print(e.read().decode('utf-8'))
    raise
