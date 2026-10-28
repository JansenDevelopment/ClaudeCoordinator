#!/usr/bin/env python
"""Een sessie in een worktree merget en pusht niet: dat doet de coordinator.

Werkwijze: een coordinator-sessie in de hoofdcheckout van een repo en losse sessies (chips)
in `.claude/worktrees/<naam>`. Toen dat alleen een afspraak in tekst was, mergeden en pushten
chips toch zelf naar main - een ervan met een regressie erin - en commitde er een in de
hoofdcheckout. Deze hook maakt de afspraak deterministisch:

  Draait de sessie in een worktree (cwd bevat `.claude/worktrees/`), dan weigert hij
    - elke `git push`, en `gh pr merge`, `gh release create|upload|edit|delete`;
    - een schrijvende git-opdracht (commit, merge, rebase, reset, checkout, switch, pull,
      cherry-pick, revert, tag, update-ref, stash, am, apply) die op de hoofdcheckout gericht
      is: via `git -C <pad>` of `cd <pad>` naar een map buiten `.claude/worktrees/`;
    - een `git update-ref`/`git branch -f` op main/master, ook in de worktree zelf.
  Commits op de eigen branch in de eigen worktree blijven gewoon mogen.

De coordinator draait in de hoofdcheckout en wordt dus nooit geraakt.

Fail-open: bij een parse-fout gaat het commando door (exit 0, geen output), zodat een bug
hier nooit normaal werk blokkeert. Dit is een vangnet, geen waterdicht slot: een script
dat git zelf aanroept (`python doe-het.py`) ziet de hook niet.
"""
import sys
import json
import re
import os

WT = re.compile(r"[\\/]\.claude[\\/]worktrees[\\/]", re.I)
WRITES = r"(commit|merge|rebase|reset|checkout|switch|pull|cherry-pick|revert|tag|update-ref|stash|am|apply)"


def norm(p):
    return p.strip().strip('"').strip("'")


def deny(why):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                why + " Deze sessie draait in een worktree: commit op je eigen branch en rond af "
                "met wrap_up (de app stuurt je recap naar de ⚡-coordinator die je startte) met wat "
                "er gedaan is, de tests en wat er nog open staat. "
                "Mergen naar main, pushen en releasen doet de coordinator."
            ),
        }
    }))
    sys.exit(0)


def main():
    data = json.load(sys.stdin)
    cwd = data.get("cwd") or ""
    if not WT.search(cwd + os.sep):
        return
    cmd = (data.get("tool_input") or {}).get("command") or ""
    if not cmd:
        return

    # `git stash push` is geen push naar een remote.
    if re.search(r"\bgit\b(?![^;&|\n]*\bstash\s+push\b)[^;&|\n]*\bpush\b", cmd):
        deny("git push is geweigerd.")
    if re.search(r"\bgh\s+pr\s+merge\b|\bgh\s+release\s+(create|upload|edit|delete)\b", cmd):
        deny("Een PR mergen of een release maken is geweigerd.")
    if re.search(r"\bgit\b[^;&|\n]*\b(update-ref\s+(refs/heads/)?(main|master)\b|branch\s+-[fFD]\s+(main|master)\b)", cmd):
        deny("main/master verzetten is geweigerd.")

    # Elke map waar een git-opdracht in deze regel op gericht kan zijn: -C <pad> en cd <pad>.
    targets = [norm(m) for m in re.findall(r"\bgit\s+-C\s+(\"[^\"]+\"|'[^']+'|\S+)", cmd)]
    targets += [norm(m) for m in re.findall(r"(?:^|[;&|\n]\s*)(?:cd|Set-Location|pushd)\s+(?:/d\s+)?(\"[^\"]+\"|'[^']+'|\S+)", cmd)]
    # Only an absolute path can leave the worktree by name; `cd scripts` stays inside it.
    absolute = re.compile(r"^([A-Za-z]:|/|~)")
    outside = [t for t in targets if absolute.match(t) and not WT.search(t.replace("/", os.sep) + os.sep)]
    if outside and re.search(r"\bgit\b[^;&|\n]*\b" + WRITES + r"\b", cmd):
        deny(f"Een schrijvende git-opdracht buiten je worktree ({outside[0]}) is geweigerd.")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        pass
    sys.exit(0)
