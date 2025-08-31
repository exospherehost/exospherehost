import subprocess, json, re, sys, urllib.request

def get_owner_repo_and_token():
    url = subprocess.check_output(["git","remote","get-url","origin"]).decode().strip()
    m = re.search(r"https://x-access-token:([^@]+)@github.com/([^/]+/[^/.]+)(?:\\.git)?$", url)
    if not m:
        return None, None
    token = m.group(1)
    owner_repo = m.group(2)
    return owner_repo, token

def get_current_branch():
    return subprocess.check_output(["git","rev-parse","--abbrev-ref","HEAD"]).decode().strip()

owner_repo, token = get_owner_repo_and_token()
branch = get_current_branch()
if not owner_repo or not token:
    print("")
    sys.exit(0)

payload = {
    "title": "docs: document Runtime.start() blocking behavior (#280)",
    "head": branch,
    "base": "main",
    "body": "This PR documents Runtime.start() blocking behavior and adds non-blocking examples. Fixes #280."
}

data = json.dumps(payload).encode()
req = urllib.request.Request(
    f"https://api.github.com/repos/{owner_repo}/pulls",
    data=data,
    headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-GitHub-Api-Version": "2022-11-28",
    },
    method="POST",
)
try:
    with urllib.request.urlopen(req) as resp:
        pr = json.loads(resp.read().decode())
        print(pr.get("html_url", ""))
except Exception as e:
    # On failure, print empty to fallback to compare URL construction outside
    print("")
