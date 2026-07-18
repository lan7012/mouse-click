import os, json, urllib.request, urllib.error, urllib.parse

TOKEN = os.environ.get('GITHUB_TOKEN')
if not TOKEN:
    raise SystemExit('Missing GITHUB_TOKEN')

headers = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github+json',
}
name = '鼠标点击'
url = f'https://api.github.com/repos/lan7012/{urllib.parse.quote(name, safe="")}'
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        print('FOUND', resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print('ERROR', e.code)
    print(e.read().decode('utf-8'))
