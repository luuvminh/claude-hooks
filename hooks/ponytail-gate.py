#!/usr/bin/env python3
"""Stop hook: changed code must get a /ponytail-review before Claude says it is done.

Checks every repo of the session (the opened repo, or the git repos one level
below the session folder) that does not ship its own ponytail-gate. Scope per
repo = changed or new code files versus the remote default branch, minus
.claude/skills/* and globs in <repo>/.claude/ponytail-skip. No repo, no remote
or no code change = silent pass. The stamp lives in ~/.claude, never in the repo.
After the review:  python3 ~/.claude/claude-hooks/hooks/ponytail-gate.py --stamp
Exit 2 blocks once per turn (stop_hook_active), never a loop.
"""
import fnmatch
import hashlib
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bin"))
import repos  # noqa: E402

STATE = os.path.join(os.path.expanduser("~"), ".claude", "claude-hooks-state")
CODE = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".php", ".html", ".css", ".scss",
        ".sh", ".swift", ".kt", ".go", ".rs", ".rb", ".java", ".vue", ".svelte", ".yml", ".yaml",
        ".toml", ".plist", ".entitlements", ".sql"}
NAMES = {"_headers", "_redirects", "Makefile", "Dockerfile", "settings.json", "package.json"}


def git(repo, *args):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    return r.stdout.splitlines() if r.returncode == 0 else None


def base(repo):
    head = git(repo, "rev-parse", "--abbrev-ref", "origin/HEAD")
    for ref in ([head[0]] if head else []) + ["origin/main", "origin/master"]:
        if git(repo, "rev-parse", "--verify", "-q", ref):
            return ref
    return None


def fingerprint(repo):
    ref = base(repo)
    if not ref:
        return [], ""
    try:
        skip = [l.strip() for l in open(os.path.join(repo, ".claude", "ponytail-skip"))
                if l.strip() and not l.startswith("#")]
    except OSError:
        skip = []
    skip.append(".claude/skills/*")
    files = set(git(repo, "diff", "--name-only", ref) or []) | \
        set(git(repo, "ls-files", "--others", "--exclude-standard") or [])
    files = sorted(f for f in files
                   if (os.path.splitext(f)[1] in CODE or os.path.basename(f) in NAMES)
                   and not any(fnmatch.fnmatch(f, g) for g in skip))
    h = hashlib.sha1()
    for f in files:
        h.update(f.encode() + b"\0")
        p = os.path.join(repo, f)
        h.update(open(p, "rb").read() if os.path.isfile(p) else b"<deleted>")
    return files, h.hexdigest() if files else ""


def stamp_path(repo):
    return os.path.join(STATE, "ponytail-" + hashlib.sha1(repo.encode()).hexdigest()[:16])


def targets():
    return [r for r in repos.covered_repos() if "ponytail-gate" not in repos.settings_text(r)]


def main():
    if "--stamp" in sys.argv:
        os.makedirs(STATE, exist_ok=True)
        for repo in targets():
            files, fp = fingerprint(repo)
            open(stamp_path(repo), "w").write(fp)
            print("ponytail-stamp: %s, %d file(s) reviewed" % (repo, len(files)))
        return
    if repos.load_json(sys.stdin.read()).get("stop_hook_active"):
        return
    lines = []
    for repo in targets():
        files, fp = fingerprint(repo)
        sp = stamp_path(repo)
        if not fp or (os.path.isfile(sp) and open(sp).read().strip() == fp):
            continue
        lines.append("%s: %d code file(s) not reviewed since the last edit, e.g.:" % (repo, len(files)))
        lines += ["  " + f for f in files[:5]]
    if not lines:
        return
    sys.stderr.write("\n".join(
        ["Ponytail:"] + lines
        + ["Run /ponytail-review on these changes, fix what it finds,",
           "then run: python3 ~/.claude/claude-hooks/hooks/ponytail-gate.py --stamp"]) + "\n")
    sys.exit(2)


main()
