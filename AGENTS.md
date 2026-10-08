# Monorepo Project Isolation

This repository integrates independent projects into `develop`, then promotes
tested integration commits from `develop` to `main`.

## Mandatory Boundaries

- Read `tools/isolation/projects.json`, `tools/isolation/README.md` and the
  project's own `AGENTS.md` before editing. Domain-specific policies still apply.
- `stock/` and its server-used historical directory `quantitative_trading/`
  belong to `stock`; `apple/` belongs to `apple`; `resum/` belongs to
  `job_agent`. Never include another project's files in a project commit.
- Existing project branches are long-lived feature branches. Additional
  `feature/stock/*` and `feature/apple/*` branches are allowed; resume remains
  exclusively on `job_agent` under its own policy.
- Never merge another project branch, `develop`, or `main` into a project branch
  merely to prepare its workspace. Flow is project -> develop -> main.
- Never switch branches with unresolved or uncommitted work. Never discard
  another agent's changes. The user chose a single checkout, without extra
  worktrees. Work on only one project at a time; all editor windows share the
  root's current branch. Commit/review outstanding work before switching.
  Never auto-stash, force checkout or migrate dirty changes across branches.
- Dependencies, environments, tests, documentation, history and generated data
  belong inside their owning project. Do not import sibling project modules or
  reuse another project's secrets, browser sessions, databases or virtualenv.
- Root files and `tools/` are shared governance infrastructure. Change these only
  for an explicit repository-wide request, in a separate governance-only commit.
  Project agents must not edit root ignore rules, shared workflows or manifests
  as part of ordinary feature work.
- Do not rename the server-used `quantitative_trading/` directory during local
  project setup. It is an explicit stock-owned alias, not resume or apple scope.
- On develop, integrate one project's changes at a time in a clean integration
  checkout. Review the incoming path diff and run that project's tests. Do not
  resolve conflicts by accepting an entire side or deleting others' work.
- Keep personal files, credentials and generated results out of commits.
- Isolation reduces conflicts; it cannot guarantee zero conflicts in shared
  files, historical changes, renames or incompatible integrations.

## Enforcement And Rollout

Run `python tools/isolation/check.py` before committing. The shared pre-commit
hook rejects cross-project staged changes. See the runbook for installation,
reviewing integration ranges, governance exceptions and adding projects.

Before every commit and push, verify the root branch and review the explicit
project paths. Never use root-wide `git add .` for a project commit. Push the
intended project branch explicitly (`git push origin job_agent`, `stock`, or
`apple`); commits/pushes do not create independent per-folder branches.

Install with `python tools/isolation/install.py`. This local repository uses an
absolute hooksPath inside the shared Git directory's `project-isolation/`, so
the installed policy survives branch switches. Reinstall after policy updates.
Other machines/clones must install their own hooks; this is not remote CI.
For portable enforcement these files must exist in each checkout. Apply
only an explicitly reviewed governance commit to other branches; never merge
project business code backwards to distribute rules. Do not automatically merge,
cherry-pick, commit or push without the user's request.
