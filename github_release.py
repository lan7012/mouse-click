import os
import json
import urllib.request
import urllib.error
import urllib.parse

TOKEN = os.environ.get('GITHUB_TOKEN')
if not TOKEN:
    raise SystemExit('Missing GITHUB_TOKEN')

owner = 'lan7012'
repo_name = 'mouse-click'
repo_api_base = f'https://api.github.com/repos/{owner}/{urllib.parse.quote(repo_name, safe="")}'
headers = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github+json',
    'Content-Type': 'application/json',
}

tag_name = 'v1.0'
release_data = json.dumps({
    'tag_name': tag_name,
    'name': tag_name,
    'body': 'Initial release with compiled executables for mouse clicker tools',
    'draft': False,
    'prerelease': False,
}).encode('utf-8')
release_url = f'{repo_api_base}/releases'
req = urllib.request.Request(release_url, data=release_data, headers=headers, method='POST')
release = None
try:
    with urllib.request.urlopen(req) as resp:
        release = json.loads(resp.read().decode('utf-8'))
        print('release-created', release['html_url'])
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    if e.code == 422 and 'already_exists' in body:
        req = urllib.request.Request(f'{repo_api_base}/releases/tags/{urllib.parse.quote(tag_name)}', headers=headers)
        with urllib.request.urlopen(req) as resp:
            release = json.loads(resp.read().decode('utf-8'))
            print('release-exists', release['html_url'])
    else:
        print('release-error', e.code)
        print(body)
        raise

upload_url = release['upload_url'].split('{')[0]
assets = ['dist/gui_auto_clicker.exe', 'dist/auto_clicker.exe']
for path in assets:
    name = os.path.basename(path)
    url = f"{upload_url}?name={urllib.parse.quote(name)}"
    print('uploading', name)
    with open(path, 'rb') as f:
        data = f.read()
    asset_headers = {**headers, 'Content-Type': 'application/octet-stream'}
    req = urllib.request.Request(url, data=data, headers=asset_headers, method='POST')
    try:
        with urllib.request.urlopen(req) as resp:
            print('asset-uploaded', name)
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        if e.code == 422 and 'already_exists' in body:
            print('asset-exists', name)
        else:
            print('asset-error', name, e.code)
            print(body)
            raise
