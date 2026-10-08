"""Fail closed on staged changes outside the current project's directory."""

import argparse
import json
from pathlib import Path
import subprocess
import sys


def git(*args):
    return subprocess.check_output(["git", *args])


def project_for_branch(policy, branch):
    for name, project in policy["projects"].items():
        if branch in project["branches"] or any(
            branch.startswith(prefix) and branch != prefix
            for prefix in project["prefixes"]
        ):
            return name
    return None


def violations(policy, project, paths):
    if project == "governance":
        allowed = lambda path: path in policy["governance_files"] or any(
            path.startswith(directory + "/")
            for directory in policy["governance_directories"]
        )
    else:
        owner = policy["projects"][project]
        directories = [owner["directory"], *owner.get("aliases", [])]
        allowed = lambda path: any(path.startswith(directory + "/") for directory in directories)
    return [path for path in paths if not allowed(path)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--range", dest="revision_range", help="Review BASE..HEAD or BASE...HEAD")
    parser.add_argument("--project", help="Required owner for range review; governance for shared rules")
    args = parser.parse_args()
    policy = json.loads(Path(__file__).with_name("projects.json").read_text(encoding="utf-8"))
    branch = git("branch", "--show-current").decode().strip()
    project = project_for_branch(policy, branch)
    if args.revision_range:
        project = args.project
        diff = ["diff", "--name-only", "-z", "--no-renames", args.revision_range, "--"]
    else:
        if args.project:
            parser.error("--project requires --range; staged ownership comes from the branch")
        governance = subprocess.run(
            ["git", "config", "--bool", "--get", "isolation.governance"],
            capture_output=True, text=True,
        ).stdout.strip()
        if governance == "true":
            project = "governance"
        diff = ["diff", "--cached", "--name-only", "-z", "--no-renames", "--"]
    if project not in {*policy["projects"], "governance"}:
        print("BLOCKED: unknown/integration branch; use an explicit project range review.", file=sys.stderr)
        return 1
    # --no-renames checks both source deletions and destination additions.
    paths = [path.decode("utf-8", errors="surrogateescape") for path in git(*diff).split(b"\0") if path]
    blocked = violations(policy, project, paths)
    if blocked:
        print(f"BLOCKED: {project} cannot change:", file=sys.stderr)
        for path in blocked:
            print(f"  {path}", file=sys.stderr)
        return 1
    print(f"OK: {project}, {len(paths)} changed paths")
    return 0


if __name__ == "__main__":
    sys.exit(main())
