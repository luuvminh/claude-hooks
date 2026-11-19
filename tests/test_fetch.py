"""repo-hooks.py SessionStart refreshes a stale origin/main:  python3 tests/test_fetch.py"""
import os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
t = tempfile.mkdtemp()
g = lambda d, *a: subprocess.run(["git", "-C", d, *a], check=True, capture_output=True, text=True).stdout.strip()
os.makedirs(t + "/src")
g(t + "/src", "init", "-q", "-b", "main")
g(t + "/src", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "1")
os.makedirs(t + "/home")
subprocess.run(["git", "clone", "-q", t + "/src", t + "/home/repo"], check=True)
g(t + "/src", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "2")
new = g(t + "/src", "rev-parse", "HEAD")
assert g(t + "/home/repo", "rev-parse", "origin/main") != new
subprocess.run([sys.executable, HERE + "/bin/repo-hooks.py", "SessionStart"], input="{}", text=True,
               cwd=t + "/home", env=dict(os.environ, CLAUDE_PROJECT_DIR=t + "/home"), check=True)
assert g(t + "/home/repo", "rev-parse", "origin/main") == new, "origin/main not refreshed"
print("fetch: ok")
