import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).parent
SPEC = importlib.util.spec_from_file_location("isolation_check", HERE / "check.py")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)
POLICY = json.loads((HERE / "projects.json").read_text(encoding="utf-8"))


class IsolationTests(unittest.TestCase):
    def test_existing_branches(self):
        for branch, project in (("stock", "stock"), ("apple", "apple"), ("job_agent", "resume")):
            self.assertEqual(CHECK.project_for_branch(POLICY, branch), project)

    def test_unknown_and_integration_branches(self):
        for branch in ("", "develop", "main", "stockish", "feature/stock/", "feature/resume/new"):
            self.assertIsNone(CHECK.project_for_branch(POLICY, branch))

    def test_scoped_features(self):
        self.assertEqual(CHECK.project_for_branch(POLICY, "feature/apple/new"), "apple")

    def test_server_stock_directory_alias(self):
        paths = ["quantitative_trading/main.py", "stock/main.py", "resum/README.md", "quantitative_trading-other/main.py"]
        self.assertEqual(CHECK.violations(POLICY, "stock", paths), paths[2:])
        self.assertEqual(CHECK.violations(POLICY, "resume", paths), [paths[0], paths[1], paths[3]])

    def test_foreign_and_root_paths(self):
        paths = ["resum/code.py", "stock/code.py", "apple/code.py", ".gitignore", "resum-other/a"]
        self.assertEqual(CHECK.violations(POLICY, "resume", paths), paths[1:])

    def test_governance_is_narrow(self):
        self.assertEqual(CHECK.violations(POLICY, "governance", [
            "AGENTS.md", "stock/AGENTS.md", "tools/isolation/check.py",
            "resum/job_agent/cli.py", ".env",
        ]), ["resum/job_agent/cli.py", ".env"])

    def test_real_git_rename_range_and_disjoint_merges(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            def git(*args):
                return subprocess.check_output(["git", *args], cwd=root, stderr=subprocess.STDOUT)

            def check(*args):
                return subprocess.run(
                    [__import__("sys").executable, str(HERE / "check.py"), *args],
                    cwd=root, capture_output=True, text=True,
                )

            git("init", "-b", "develop")
            git("config", "user.name", "Fixture")
            git("config", "user.email", "fixture@example.invalid")
            git("config", "commit.gpgsign", "false")
            for project in ("stock", "apple", "resum"):
                (root / project).mkdir()
                (root / project / "sample.txt").write_text("initial", encoding="utf-8")
            git("add", ".")
            git("commit", "-m", "fixture")
            (root / "tools/isolation").mkdir(parents=True)
            for name in ("check.py", "projects.json"):
                shutil.copy2(HERE / name, root / "tools/isolation" / name)
            (root / ".githooks").mkdir()
            hook = root / ".githooks/pre-commit"
            shutil.copy2(HERE.parent.parent / ".githooks/pre-commit", hook)
            hook.chmod(0o755)
            git("config", "core.hooksPath", ".githooks")
            self.assertNotEqual(check().returncode, 0)
            git("switch", "-c", "job_agent")
            git("mv", "stock/sample.txt", "resum/moved.txt")
            rejected = check()
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("stock/sample.txt", rejected.stderr)
            with self.assertRaises(subprocess.CalledProcessError) as failure:
                git("commit", "-m", "must be blocked")
            self.assertIn(b"stock/sample.txt", failure.exception.output)
            # Undo only the fixture's move, never touch the real checkout.
            git("mv", "resum/moved.txt", "stock/sample.txt")
            self.assertEqual(check().returncode, 0)
            for branch in ("stock", "apple"):
                git("switch", "develop")
                git("switch", "-c", branch)
                (root / branch / "sample.txt").write_text(branch, encoding="utf-8")
                git("add", branch)
                self.assertEqual(check().returncode, 0)
                git("commit", "-m", branch)
                self.assertEqual(check("--range", f"develop...{branch}", "--project", branch).returncode, 0)
                self.assertNotEqual(check("--range", f"develop...{branch}", "--project", "resume").returncode, 0)
            git("switch", "develop")
            git("merge", "--no-ff", "stock", "-m", "integrate stock")
            git("merge", "--no-ff", "apple", "-m", "integrate apple")
            self.assertEqual((root / "stock/sample.txt").read_text(), "stock")
            self.assertEqual((root / "apple/sample.txt").read_text(), "apple")
            self.assertEqual((root / "resum/sample.txt").read_text(), "initial")

    def test_linked_worktree_shared_hook_and_independent_index(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "primary"
            root.mkdir()
            linked = root.parent / "stock-worktree"

            def git(cwd, *args):
                return subprocess.check_output(["git", *args], cwd=cwd, stderr=subprocess.STDOUT)

            git(root, "init", "-b", "job_agent")
            git(root, "config", "user.name", "Fixture")
            git(root, "config", "user.email", "fixture@example.invalid")
            git(root, "config", "commit.gpgsign", "false")
            for project in ("quantitative_trading", "resum"):
                (root / project).mkdir()
                (root / project / "sample.txt").write_text("initial", encoding="utf-8")
            git(root, "add", ".")
            git(root, "commit", "-m", "fixture")
            (root / "tools/isolation").mkdir(parents=True)
            for name in ("check.py", "projects.json"):
                shutil.copy2(HERE / name, root / "tools/isolation" / name)
            (root / ".githooks").mkdir()
            hook = root / ".githooks/pre-commit"
            shutil.copy2(HERE.parent.parent / ".githooks/pre-commit", hook)
            hook.chmod(0o755)
            git(root, "config", "core.hooksPath", (root / ".githooks").as_posix())
            git(root, "worktree", "add", "-b", "stock", str(linked))
            self.assertFalse((linked / "tools/isolation/check.py").exists())
            (root / "resum/sample.txt").write_text("preserve staged resume", encoding="utf-8")
            git(root, "add", "resum/sample.txt")
            # A project hook may generate/stage mirrors; guard its output too.
            project_hooks = linked / "quantitative_trading/.githooks"
            project_hooks.mkdir()
            project_hook = project_hooks / "pre-commit"
            project_hook.write_text(
                "#!/bin/sh\nprintf mirror > quantitative_trading/mirror.txt\n"
                "git add quantitative_trading/mirror.txt\n", encoding="utf-8",
            )
            (linked / "quantitative_trading/sample.txt").write_text("stock update", encoding="utf-8")
            git(linked, "add", "quantitative_trading/sample.txt")
            git(linked, "commit", "-m", "stock update")
            self.assertEqual(git(linked, "show", "HEAD:quantitative_trading/mirror.txt"), b"mirror")
            self.assertEqual(git(root, "branch", "--show-current").strip(), b"job_agent")
            self.assertEqual(git(root, "diff", "--cached", "--name-only").strip(), b"resum/sample.txt")
            self.assertEqual((root / "resum/sample.txt").read_text(), "preserve staged resume")
            (linked / "resum/sample.txt").write_text("wrong project", encoding="utf-8")
            git(linked, "add", "resum/sample.txt")
            with self.assertRaises(subprocess.CalledProcessError) as failure:
                git(linked, "commit", "-m", "blocked foreign project")
            self.assertIn(b"resum/sample.txt", failure.exception.output)
            # Only the disposable fixture's index is reset.
            git(linked, "reset", "HEAD", "--", "resum/sample.txt")
            project_hook.write_text(
                "#!/bin/sh\nprintf foreign > resum/generated.txt\ngit add resum/generated.txt\n",
                encoding="utf-8",
            )
            with self.assertRaises(subprocess.CalledProcessError) as failure:
                git(linked, "commit", "-m", "blocked generated foreign project")
            self.assertIn(b"resum/generated.txt", failure.exception.output)

    def test_installer_survives_removal_of_checkout_rules(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.check_output(["git", *args], cwd=root, stderr=subprocess.STDOUT)
            git("init", "-b", "job_agent")
            git("config", "user.name", "Fixture")
            git("config", "user.email", "fixture@example.invalid")
            git("config", "commit.gpgsign", "false")
            (root / "resum").mkdir()
            (root / "resum/file.txt").write_text("initial", encoding="utf-8")
            git("add", ".")
            git("commit", "-m", "fixture")
            policy = root / "tools/isolation"
            policy.mkdir(parents=True)
            for name in ("install.py", "check.py", "projects.json"):
                shutil.copy2(HERE / name, policy / name)
            hooks = root / ".githooks"
            hooks.mkdir()
            for name in ("pre-commit", "post-checkout", "post-commit", "post-merge", "pre-push"):
                shutil.copy2(HERE.parent.parent / ".githooks" / name, hooks / name)
            subprocess.run([sys.executable, str(policy / "install.py")], cwd=root, check=True, capture_output=True)
            shutil.rmtree(root / "tools")
            shutil.rmtree(hooks)
            self.assertEqual(git("hook", "run", "pre-commit").strip(), b"OK: resume, 0 changed paths")
            (root / "apple").mkdir()
            (root / "apple/file.txt").write_text("foreign", encoding="utf-8")
            git("add", "apple")
            with self.assertRaises(subprocess.CalledProcessError):
                git("hook", "run", "pre-commit")


if __name__ == "__main__":
    unittest.main()
