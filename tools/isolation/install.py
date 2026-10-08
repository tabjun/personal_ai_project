"""Install branch-independent local commit guards inside the shared Git directory."""

from pathlib import Path
import shutil
import subprocess


def install():
    source = Path(__file__).resolve().parent
    common = subprocess.check_output(
        ["git", "rev-parse", "--git-common-dir"], text=True,
    ).strip()
    target = Path(common).resolve() / "project-isolation"
    policy = target / "tools/isolation"
    hooks = target / ".githooks"
    policy.mkdir(parents=True, exist_ok=True)
    hooks.mkdir(parents=True, exist_ok=True)
    for name in ("check.py", "projects.json"):
        shutil.copy2(source / name, policy / name)
    for name in ("pre-commit", "post-checkout", "post-commit", "post-merge", "pre-push"):
        original = source.parent.parent / ".githooks" / name
        destination = hooks / name
        destination.write_bytes(original.read_bytes().replace(b"\r\n", b"\n"))
        destination.chmod(0o755)
    subprocess.run(["git", "config", "core.hooksPath", hooks.as_posix()], check=True)
    print(f"Installed local project guards: {hooks}")


if __name__ == "__main__":
    install()
