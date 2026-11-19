"""Which repos a session covers, and whether they bring their own hooks.

A session opened inside a repo covers that repo. A session opened one level
above (cloud threads start in /home/user, repos in /home/user/<name>) covers
every git repo directly below it. Claude Code only runs .claude/settings.json
of the folder it was opened in, so repo-hooks.py runs the others.
"""
import json
import os
import subprocess


def project_dir():
    return os.path.abspath(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())


def is_repo(d):
    return os.path.isdir(os.path.join(d, ".git"))


def settings_text(d):
    try:
        return open(os.path.join(d, ".claude", "settings.json"), encoding="utf-8").read()
    except OSError:
        return ""


def child_repos(d):
    try:
        names = sorted(os.listdir(d))
    except OSError:
        return []
    return [os.path.join(d, n) for n in names
            if not n.startswith(".") and is_repo(os.path.join(d, n))]


def git_root(d):
    r = subprocess.run(["git", "-C", d, "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def covered_repos():
    """Repos this session works on: the opened repo, else the repos one level down."""
    d = project_dir()
    root = git_root(d)
    return [root] if root else child_repos(d)


def hooked_children():
    """Child repos whose own project hooks Claude Code will NOT run (repo-hooks.py runs them)."""
    d = project_dir()
    if git_root(d) or settings_text(d):
        return []
    return [r for r in child_repos(d) if '"hooks"' in settings_text(r)]


HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Plugins that already bring the hook (Mac has superpowers and ponytail as plugins).
PLUGIN_FOR = {"superpowers-session-start": "superpowers@", "ponytail-activate": "ponytail@",
              "ponytail-mode-tracker": "ponytail@", "ponytail-subagent": "ponytail@"}


def user_settings():
    d = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")
    return load_json(_read(os.path.join(d, "settings.json")))


def _read(p):
    try:
        return open(p, encoding="utf-8").read()
    except OSError:
        return ""


def user_has(marker):
    """True when user settings run this hook outside claude-hooks, or a plugin brings it."""
    s = user_settings()
    plugin = PLUGIN_FOR.get(marker)
    if plugin and any(k.startswith(plugin) and v for k, v in (s.get("enabledPlugins") or {}).items()):
        return True
    for groups in (s.get("hooks") or {}).values():
        for g in groups:
            for h in g.get("hooks", []):
                c = h.get("command", "")
                if marker in c and HERE not in c:
                    return True
    return False


def has_own(marker):
    """True when a repo of this session, the user settings or a plugin already run this hook."""
    if user_has(marker):
        return True
    d = project_dir()
    root = git_root(d) or d
    if marker in settings_text(root):
        return True
    return any(marker in settings_text(r) for r in hooked_children())


def load_json(text):
    try:
        v = json.loads(text or "{}")
        return v if isinstance(v, dict) else {}
    except ValueError:
        return {}
