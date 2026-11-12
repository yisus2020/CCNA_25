#!/usr/bin/env python3
"""Documentation checks: balanced code fences, H1 title, version line, relative links.

Run from the repository root: python3 .github/scripts/check_docs.py
"""
import re
import subprocess
import sys
from pathlib import Path

SKIP_VERSION_LINE = {"README.md", "CHANGELOG.md", "TEMPLATE.md"}
errors = []
files = subprocess.check_output(["git", "ls-files", "*.md"], text=True).split()
for f in files:
    text = Path(f).read_text(encoding="utf8")
    lines = text.split("\n")
    if text.count("```") % 2:
        errors.append(f"{f}: unbalanced code fence")
    if not lines[0].startswith("# "):
        errors.append(f"{f}: first line must be an H1 title")
    if Path(f).name not in SKIP_VERSION_LINE and not (len(lines) > 2 and lines[2].startswith("> Document version:")):
        errors.append(f"{f}: missing '> Document version:' line under the title")
    for m in re.finditer(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", text):
        target = m.group(1)
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        if not (Path(f).parent / target).exists():
            errors.append(f"{f}: broken link {target}")
for e in errors:
    print("ERROR", e)
print(f"{len(files)} markdown files checked, {len(errors)} problem(s)")
sys.exit(1 if errors else 0)
