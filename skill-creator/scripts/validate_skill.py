#!/usr/bin/env python3
import re, sys
from pathlib import Path

SECRETS = [re.compile(r"sk-or-v1-\w{20,}|sk-ant-[\w\-]{20,}|ghp_\w{20,}")]
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)#]+)\)")

def check(d: Path) -> list[str]:
    f = d / "SKILL.md"
    if not f.is_file(): return [f"Missing SKILL.md in {d}"]
    txt = f.read_text("utf-8")
    errs = ["SKILL.md > 500 lines"] if len(txt.splitlines()) > 500 else []
    if not txt.startswith("---\n") or "\n---\n" not in txt[4:]: return errs + ["Invalid YAML"]
    fm = {ln.split(":",1)[0].strip(): ln.split(":",1)[1].strip().strip("\"'") for ln in txt[4:txt.find("\n---\n",4)].splitlines() if ":" in ln and not ln.startswith("  ")}
    n, desc = fm.get("name",""), fm.get("description","")
    if not n or len(n)>64 or not NAME_RE.match(n) or n!=d.name: errs.append(f"Bad name: {n}")
    if not desc or len(desc)>1024: errs.append("Bad description")
    for rel in LINK_RE.findall(txt):
        if not rel.startswith(("http://","https://")) and not (d/rel).exists(): errs.append(f"Broken link: {rel}")
    for p in d.rglob("*"):
        if p.is_file():
            try:
                if any(r.search(p.read_text("utf-8")) for r in SECRETS): errs.append(f"Secret in {p.name}")
            except UnicodeDecodeError: pass
    return errs

t = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("skill-creator")
e = check(t.resolve())
print("\n".join(e) if e else f"OK: '{t.name}' passed all agentskills.io checks!")
sys.exit(1 if e else 0)
