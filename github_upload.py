import os
import json
import urllib.request
import urllib.error
import urllib.parse

TOKEN = os.environ.get('GITHUB_TOKEN')
if not TOKEN:
    raise SystemExit('Missing GITHUB_TOKEN')

owner = 'lan7012'
repo_name = '鼠标点击'
repo_api_base = f'https://api.github.com/repos/{owner}/{urllib.parse.quote(repo_name, safe="")}'
headers = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github+json',
    'Content-Type': 'application/json',
}

# Create repo
create_url = 'https://api.github.com/user/repos'
create_data = json.dumps({
    'name': repo_name,
    'private': False,
    'description': 'Windows 自动点击工具',
    'auto_init': False,
}).encode('utf-8')
req = urllib.request.Request(create_url, data=create_data, headers=headers, method='POST')
try:
    with urllib.request.urlopen(req) as resp:
        print('repo-created')
        print(resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    if e.code == 422 and 'already exists' in body:
        print('repo-exists')
    else:
        print('repo-error', e.code)
        print(body)
        raise

# Verify repo
req = urllib.request.Request(repo_api_base, headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        print('repo-ok')
        print(resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print('repo-verify-failed', e.code)
    print(e.read().decode('utf-8'))
    raise

# Create release
tag_name = 'v1.0'
release_url = f'{repo_api_base}/releases'
release_data = json.dumps({
    'tag_name': tag_name,
    'name': tag_name,
    'body': 'Release with compiled executables for mouse clicker tools',
    'draft': False,
    'prerelease': False,
}).encode('utf-8')
req = urllib.request.Request(release_url, data=release_data, headers=headers, method='POST')
release = None
try:
    with urllib.request.urlopen(req) as resp:
        release = json.loads(resp.read().decode('utf-8'))
        print('release-created')
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    if e.code == 422 and 'already_exists' in body:
        req = urllib.request.Request(f'{repo_api_base}/releases/tags/{urllib.parse.quote(tag_name)}', headers=headers)
        with urllib.request.urlopen(req) as resp:
            release = json.loads(resp.read().decode('utf-8'))
            print('release-exists')
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
