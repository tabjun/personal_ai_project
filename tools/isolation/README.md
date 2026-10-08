# Project Isolation Runbook

| Project | Directory | Existing feature branch |
| --- | --- | --- |
| Stock | `quantitative_trading/` (server project), `stock/` (legacy alias) | `stock` |
| Apple | `apple/` | `apple` |
| Resume | `resum/` | `job_agent` |

`develop` integrates all projects; `main` receives tested develop integration.
No branch merges were performed when introducing these rules.

## Single Checkout Policy (2026-10-09)

At the user's request, the extra toy-stock, toy-apple and toy-integration
worktrees and their editor entry files were removed. Original project folders,
private data, environments and dirty resume changes remain intact. Branches
were not deleted; stock retains its fast-forward to dd316ef. No commit, push
or cross-project merge was performed. The server clone is unchanged.

All project folders now use the original root checkout. Opening a subfolder
does NOT give it an independent branch: every editor sees the root's current
branch. Work on one project at a time. Finish/review/commit outstanding changes
before switching; do not force checkout, auto-stash, or move dirty changes to
another branch. The current dirty job_agent checkout was not switched.

From the root, review a resume commit using explicit paths (replace the example
file names with the intended changes; do not stage personal/generated files):

```sh
git status --short --branch
git add -- resum/job_agent/cli.py resum/tests/test_ui.py
git diff --cached --name-status
python tools/isolation/check.py
git commit -m "feat(resume): describe the change"
git push origin job_agent
```

On a clean checkout, stock uses `git switch stock`, then
`git pull --ff-only origin stock` after the server pushes. Apple uses
`git switch apple` and `git pull --ff-only origin apple`. Review/stage only
quantitative_trading (or legacy stock) on stock, and only apple on apple.
Push the corresponding branch explicitly. Never use root-wide `git add .`.
The installed checker survives switching older branches. Use
`git hook run pre-commit` when that branch lacks the tracked checker files.
Local hooks do not automatically enforce rules on the server.

## Commit Guard

Requires Python 3.10+. Same commands work in PowerShell and Linux:

```sh
python tools/isolation/install.py
python tools/isolation/check.py
python -m unittest discover -s tools/isolation -p "test_*.py" -v
```

The hook checks staged paths, including both sides of renames. Unknown branches,
detached HEAD and normal commits on develop/main are blocked. Stage explicit
project paths, not `git add .` at the root. Root-wide changes must be separate.
Hooks are local safeguards, not a security boundary: `--no-verify` bypasses them.
The installer copies the guard and policy into the shared Git directory's
`project-isolation/` and configures an absolute hooksPath. Branch switches can
remove the tracked rule files without removing the installed guard. Rerun the
installer after updating rules. Existing unrelated hooks must be reviewed before
installation; these five managed hooks are replaced on reinstallation.
Git LFS lifecycle hooks remain installed there. On stock branches, the
existing `quantitative_trading/.githooks/pre-commit` notebook mirror and research
checks also run, followed by another ownership check on generated staged files.
Apple's previously inactive policy script is left inactive; the common ownership
guard does apply to apple. Remote/server clones need their own installation.
Each clone must run the installer separately; this does not install remote CI.

For this explicitly requested governance setup, isolate the rule files in their
own commit; do not stage the existing resume implementation changes with them:

```sh
git -c isolation.governance=true commit -m "chore: define project isolation"
```

This one-command exception allows only root/project AGENTS and the isolation
tools/hooks, not arbitrary files. Do not set it persistently. Distribute that
reviewed rules-only commit to project branches explicitly; never distribute
rules by merging stock business code into job_agent. Integration commits on
develop/main must be merges, not direct feature commits.

## Before Integrating

In a clean develop checkout, inspect the feature diff against the actual
integration base. A three-dot range reviews changes since the common ancestor:

```sh
python tools/isolation/check.py --range develop...stock --project stock
python tools/isolation/check.py --range develop...apple --project apple
python tools/isolation/check.py --range develop...job_agent --project resume
```

Separate governance commits need separate review. If historic branch changes
already include other projects, this check intentionally fails: inspect them,
do not blindly merge or rewrite history. Check conflicts with a temporary
integration checkout, test each project, then merge one project at a time.
Ordinary merge commits do not execute pre-commit; range checks are mandatory
before merging. These instructions do not install CI or branch protections.

Folder separation prevents independent edits from colliding in most cases,
but shared files and historical changes can still conflict. Do not claim a
guarantee of zero conflicts.

## Add A Project

In a separate governance request, add one unique directory and branch/prefix
entry to `projects.json`, add that directory's AGENTS, and test ownership rules.
Avoid overlapping directories or branch prefixes. Project code lives only in
its new directory; root governance remains shared.
