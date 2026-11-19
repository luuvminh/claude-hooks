#!/usr/bin/env python3
"""Link each bundled skill into ~/.claude/skills unless that name exists already,
or a plugin already brings that skill family (superpowers, ponytail)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import repos  # noqa: E402

SUPERPOWERS = {"brainstorming", "diagnosing-superpowers", "dispatching-parallel-agents", "executing-plans",
               "finishing-a-development-branch", "receiving-code-review", "requesting-code-review",
               "subagent-driven-development", "systematic-debugging", "test-driven-development",
               "using-git-worktrees", "using-superpowers", "verification-before-completion",
               "writing-plans", "writing-skills"}
plugins = [k for k, v in (repos.user_settings().get("enabledPlugins") or {}).items() if v]
has = lambda p: any(k.startswith(p) for k in plugins)  # noqa: E731
dest = sys.argv[1]
os.makedirs(dest, exist_ok=True)
src = os.path.join(repos.HERE, "skills")
for name in sorted(os.listdir(src)):
    if (name in SUPERPOWERS and has("superpowers@")) or (name.startswith("ponytail") and has("ponytail@")):
        continue
    t = os.path.join(dest, name)
    if not os.path.lexists(t):
        os.symlink(os.path.join(src, name), t)
        print("skill linked: " + name)
