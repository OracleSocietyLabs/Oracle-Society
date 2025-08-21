
#!/usr/bin/env python3
Patch README badges/links using the repository's origin (owner/repo).

Usage:
  python scripts/patch_repo_identifiers.py

Notes:
 - Works for HTTPS or SSH remotes (github.com only).
 - If not in a git repo or no origin found, exits with message.

import os, re, subprocess, sys
from pathlib import Path

def get_origin():
    try:
        url = subprocess.check_output(["git","remote","get-url","origin"], text=True).strip()
        return url
    except Exception:
        return ""

def parse_owner_repo(url: str):
    if not url: return ("","")
    # https://github.com/owner/repo.git
    m = re.match(r"https?://github.com/([^/]+)/([^/]+)(?:\.git)?$", url)
    if m: return (m.group(1), m.group(2).removesuffix(".git"))
    # git@github.com:owner/repo.git
    m = re.match(r"git@github\.com:([^/]+)/([^/]+)(?:\.git)?$", url)
    if m: return (m.group(1), m.group(2).removesuffix(".git"))
    return ("","")

def rewrite_readme(owner, repo, path="README.md"):
    p = Path(path)
    if not p.exists(): 
        print("README.md not found")
        return False
    s = p.read_text(encoding="utf-8")

    # Replace relative workflow badges with absolute ones + links
    def badge(name, wf):
        img = f"https://github.com/{owner}/{repo}/actions/workflows/{wf}/badge.svg?branch=main"
        link = f"https://github.com/{owner}/{repo}/actions/workflows/{wf}"
        return f"[![{name}]({img})]({link})"
    ci_py    = badge("CI - Python","ci-python.yml")
    ci_dock  = badge("CI - Docker","ci-docker.yml")
    release  = badge("Release","release.yml")

    # Codecov badge
    codecov_badge = f"[![codecov](https://codecov.io/gh/{owner}/{repo}/graph/badge.svg)](https://codecov.io/gh/{owner}/{repo})"

    # A heuristic: find the first badge line and replace; otherwise insert below H1
    lines = s.splitlines()
    out = []
    inserted = False
    i = 0
    while i < len(lines):
        if i==0 and lines[i].startswith("# "):
            out.append(lines[i])
            # on the next non-empty line, inject badges
            # skip existing badge line(s)
            j = i+1
            while j < len(lines) and (lines[j].strip().startswith("![") or lines[j].strip().startswith("[!")):
                j += 1
            out.append("")
            out.append(" ".join([ci_py, ci_dock, release, codecov_badge]))
            out.extend(lines[j:])
            inserted = True
            break
        i += 1
    if not inserted:
        # fallback: prepend
        out = [" ".join([ci_py, ci_dock, release, codecov_badge]), ""] + lines
    new = "\n".join(out)
    if new != s:
        p.write_text(new, encoding="utf-8")
        print("README badges updated for", owner, "/", repo)
        return True
    print("README already up to date")
    return True

def main():
    origin = get_origin()
    if not origin:
        print("No git origin found. Run inside your repo with a configured 'origin'.")
        sys.exit(1)
    owner, repo = parse_owner_repo(origin)
    if not owner or not repo:
        print("Could not parse owner/repo from:", origin)
        sys.exit(2)
    ok = rewrite_readme(owner, repo)
    sys.exit(0 if ok else 3)

if __name__ == "__main__":
    main()
