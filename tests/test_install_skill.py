"""Isolated CLI tests: no real agent directories or release payload used."""
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from contextlib import redirect_stdout


INSTALLER = Path(__file__).resolve().parents[1] / "scripts" / "install_skill.py"
NAME = "scientific-article-appraisal"


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo = self.root / "repo"
        self.script = self.repo / "scripts" / "install_skill.py"
        self.script.parent.mkdir(parents=True)
        if INSTALLER.exists():
            shutil.copyfile(INSTALLER, self.script)
        self.source = self.repo / "skills" / NAME
        self.source.mkdir(parents=True)
        (self.source / "SKILL.md").write_text(
            '---\nname: scientific-article-appraisal\nversion: "fixture0.1"\n---\nFixture\n', encoding="utf-8"
        )
        (self.source / "references").mkdir()
        (self.source / "references" / "data.bin").write_bytes(b"\x00payload\xff")
        self.home = self.root / "home"
        self.home.mkdir()
        self.env = dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home), PYTHONDONTWRITEBYTECODE="1")
        self.env.pop("HERMES_HOME", None)
        self.target = self.root / "new-parent" / NAME

    def cli(self, *args, success=True):
        result = subprocess.run(
            [sys.executable, "-B", str(self.script), *map(str, args)],
            env=self.env, text=True, capture_output=True, timeout=10,
        )
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        try:
            data = json.loads(result.stdout)
        except ValueError:
            self.fail(f"Not JSON stdout: {result.stdout!r}; stderr={result.stderr!r}")
        self.assertIn("status", data)
        return data


    def test_explicit_target_dry_run_writes_nothing(self):
        before = sorted(str(p.relative_to(self.root)) for p in self.root.rglob("*"))
        result = self.cli("--target-dir", self.target, "--dry-run")
        self.assertEqual(result["status"], "dry_run")
        self.assertEqual(result["target"], str(self.target))
        self.assertEqual(result["version"], "fixture0.1")
        self.assertEqual(before, sorted(str(p.relative_to(self.root)) for p in self.root.rglob("*")))


    def test_agent_routing_and_argument_errors_are_json(self):
        expected = {
            "hermes": self.home / ".hermes" / "skills" / NAME,
            "codex": self.home / ".agents" / "skills" / NAME,
            "claude": self.home / ".claude" / "skills" / NAME,
        }
        for agent, target in expected.items():
            with self.subTest(agent=agent):
                self.assertEqual(self.cli("--agent", agent, "--dry-run")["target"], str(target))
        self.env["HERMES_HOME"] = str(self.root / "profile")
        self.assertEqual(self.cli("--agent", "hermes", "--dry-run")["target"],
                         str(self.root / "profile" / "skills" / NAME))
        for arguments in [(), ("--agent", "unknown"), ("--agent", "codex", "--target-dir", str(self.target)),
                          ("--target-dir", str(self.target), "--check", "--dry-run")]:
            with self.subTest(arguments=arguments):
                self.assertEqual(self.cli(*arguments, success=False)["status"], "error")

    def test_unsafe_paths_and_symlinks_are_rejected_before_writes(self):
        unsafe = [self.root / "wrong-name", self.source, self.source / "nested" / NAME,
                  str(self.root / ".." / NAME), "", ".", "/"]
        for target in unsafe:
            with self.subTest(target=str(target)):
                self.cli("--target-dir", target, "--dry-run", success=False)
        outside = self.root / "outside"
        outside.mkdir()
        link = self.root / "linked"
        link.symlink_to(outside, target_is_directory=True)
        self.cli("--target-dir", link / NAME, "--dry-run", success=False)
        self.target.parent.mkdir()
        self.target.symlink_to(outside, target_is_directory=True)
        self.cli("--target-dir", self.target, "--dry-run", success=False)
        self.target.unlink()
        for relative in ["linked-file", "__pycache__/hidden-link"]:
            with self.subTest(relative=relative):
                source_link = self.source / relative
                source_link.parent.mkdir(exist_ok=True)
                source_link.symlink_to(outside, target_is_directory=True)
                self.cli("--target-dir", self.target, "--dry-run", success=False)
                source_link.unlink()
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse(self.target.exists())

    def test_reparse_points_are_rejected_in_paths_and_payloads(self):
        import stat
        module = self.module()
        original_lstat = Path.lstat
        candidates = (self.root / "junction", self.source / "references" / "data.bin")
        for suspicious in candidates:
            def with_reparse(path, *args, **kwargs):
                if path == suspicious:
                    return mock.Mock(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
                return original_lstat(path, *args, **kwargs)
            with self.subTest(path=suspicious), mock.patch.object(Path, "lstat", with_reparse):
                with self.assertRaises(ValueError):
                    if suspicious == candidates[0]:
                        module.safe_path(suspicious)
                    else:
                        module.validate_tree(self.source)

    def test_new_install_copies_payload_only_and_preserves_siblings(self):
        for cache in ["__pycache__", ".git", ".pytest_cache", "caches"]:
            (self.source / cache).mkdir()
            (self.source / cache / "ignored").write_text("cache", encoding="utf-8")
        (self.source / "references" / "ignored.pyc").write_bytes(b"cache")
        (self.source / "empty-directory").mkdir()
        self.target.parent.mkdir()
        sibling = self.target.parent / "unrelated-skill"
        sibling.mkdir()
        (sibling / "keep").write_bytes(b"keep")
        before = {str(p.relative_to(self.source)): p.read_bytes()
                  for p in self.source.rglob("*") if p.is_file()}
        result = self.cli("--target-dir", self.target)
        self.assertEqual(result["status"], "installed")
        self.assertEqual(result["files"], 2)
        self.assertEqual(len(result["sha256"]), 64)
        self.assertEqual((self.target / "references" / "data.bin").read_bytes(), b"\x00payload\xff")
        self.assertTrue((self.target / "empty-directory").is_dir())
        self.assertEqual(sorted(str(p.relative_to(self.target)) for p in self.target.rglob("*")),
                         ["SKILL.md", "empty-directory", "references", "references/data.bin"])
        self.assertEqual(before, {str(p.relative_to(self.source)): p.read_bytes()
                                 for p in self.source.rglob("*") if p.is_file()})
        self.assertEqual((sibling / "keep").read_bytes(), b"keep")
        self.assertEqual(sorted(p.name for p in self.target.parent.iterdir()), [NAME, "unrelated-skill"])

    def test_existing_identical_is_noop_and_customized_requires_replace(self):
        self.cli("--target-dir", self.target)
        before = {str(p): p.stat().st_mtime_ns for p in self.target.rglob("*")}
        result = self.cli("--target-dir", self.target)
        self.assertEqual(result["status"], "already_installed")
        self.assertEqual(before, {str(p): p.stat().st_mtime_ns for p in self.target.rglob("*")})
        custom = self.target / "custom.txt"
        custom.write_text("my customization", encoding="utf-8")
        for flags in [(), ("--dry-run",)]:
            with self.subTest(flags=flags):
                result = self.cli("--target-dir", self.target, *flags, success=False)
                self.assertIn("--replace", result["error"])
        self.assertEqual(custom.read_text(encoding="utf-8"), "my customization")
        self.assertEqual([p.name for p in self.target.parent.iterdir()], [NAME])

    def test_generated_cache_does_not_count_as_customization(self):
        self.cli("--target-dir", self.target)
        cache = self.target / "references" / "__pycache__"
        cache.mkdir()
        (cache / "generated.pyc").write_bytes(b"generated cache")
        self.assertEqual(self.cli("--target-dir", self.target, "--check")["status"], "verified")
        self.assertEqual(self.cli("--target-dir", self.target)["status"], "already_installed")
        self.assertEqual((cache / "generated.pyc").read_bytes(), b"generated cache")

    def test_check_is_read_only_and_detects_same_size_tampering(self):
        self.cli("--target-dir", self.target, "--check", success=False)
        self.assertFalse(self.target.parent.exists())
        installed = self.cli("--target-dir", self.target)
        before = {str(p): p.stat().st_mtime_ns for p in self.target.rglob("*")}
        result = self.cli("--target-dir", self.target, "--check")
        self.assertEqual(result["status"], "verified")
        self.assertEqual(result["sha256"], installed["sha256"])
        self.assertEqual(before, {str(p): p.stat().st_mtime_ns for p in self.target.rglob("*")})
        file = self.target / "references" / "data.bin"
        stat = file.stat()
        file.write_bytes(b"\x00changed\xff")
        os.utime(file, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        result = self.cli("--target-dir", self.target, "--check", success=False)
        self.assertEqual(result["status"], "error")
        self.assertEqual(file.read_bytes(), b"\x00changed\xff")
        self.cli("--target-dir", self.target, "--check", "--replace", success=False)
        self.assertEqual(list(self.target.parent.iterdir()), [self.target])

    def test_replace_makes_unique_hidden_backups_and_dry_run_is_read_only(self):
        self.cli("--target-dir", self.target)
        custom = self.target / "custom.txt"
        custom.write_bytes(b"first custom")
        before = sorted(str(p) for p in self.root.rglob("*"))
        result = self.cli("--target-dir", self.target, "--replace", "--dry-run")
        self.assertEqual(result["status"], "dry_run")
        self.assertEqual(before, sorted(str(p) for p in self.root.rglob("*")))
        first = self.cli("--target-dir", self.target, "--replace")
        self.assertEqual(first["status"], "replaced")
        backup1 = Path(first["backup"])
        self.assertEqual(backup1.parent, self.target.parent)
        self.assertTrue(backup1.name.startswith(f".{NAME}.backup-"))
        self.assertEqual((backup1 / "custom.txt").read_bytes(), b"first custom")
        self.assertFalse(custom.exists())
        self.cli("--target-dir", self.target, "--check")
        custom.write_bytes(b"second custom")
        second = self.cli("--target-dir", self.target, "--replace")
        backup2 = Path(second["backup"])
        self.assertNotEqual(backup1, backup2)
        self.assertEqual((backup2 / "custom.txt").read_bytes(), b"second custom")
        self.assertEqual((backup1 / "custom.txt").read_bytes(), b"first custom")
        self.assertEqual(set(self.target.parent.iterdir()), {self.target, backup1, backup2})
    def module(self):
        spec = importlib.util.spec_from_file_location("fixture_installer", self.script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


    def test_interrupted_replace_restores_original_and_removes_stage(self):
        self.cli("--target-dir", self.target)
        (self.target / "custom").write_bytes(b"original")
        module = self.module()
        original_rename = Path.rename

        def interrupt_stage(path, destination):
            if ".stage-" in path.name:
                raise KeyboardInterrupt("injected interruption")
            return original_rename(path, destination)

        with mock.patch.object(Path, "rename", interrupt_stage):
            with self.assertRaises(KeyboardInterrupt):
                module.install(self.target, module.manifest(self.source, True), module.manifest(self.target))
        self.assertTrue(self.target.is_dir(), "Original destination must be restored on interruption")
        self.assertEqual((self.target / "custom").read_bytes(), b"original")
        self.assertEqual(list(self.target.parent.iterdir()), [self.target])

    @unittest.skipIf(os.name == "nt", "Windows SIGTERM bypasses Python cleanup handlers")
    def test_sigterm_during_copy_cleans_stage_and_reports_json(self):
        code = (
            "import os, runpy, shutil, signal, sys; "
            "shutil.copy2 = lambda *a, **k: os.kill(os.getpid(), signal.SIGTERM); "
            f"sys.argv = [{str(self.script)!r}, '--target-dir', {str(self.target)!r}]; "
            f"runpy.run_path({str(self.script)!r}, run_name='__main__')"
        )
        result = subprocess.run([sys.executable, "-B", "-c", code], env=self.env,
                                capture_output=True, text=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(result.stdout.strip().startswith("{"), result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "error")
        self.assertFalse(self.target.exists())
        self.assertEqual(list(self.target.parent.iterdir()), [])
        self.assertEqual((self.source / "references" / "data.bin").read_bytes(), b"\x00payload\xff")

    def test_invalid_frontmatter_is_json_failure_without_writes(self):
        for text in ["no frontmatter", "---\nname: test\n---\nBody", "---\nversion: fixture0.1\nBody"]:
            with self.subTest(text=text):
                (self.source / "SKILL.md").write_text(text, encoding="utf-8")
                self.cli("--target-dir", self.target, "--dry-run", success=False)
                self.assertFalse(self.target.parent.exists())

    def test_unreadable_source_subdirectory_is_not_silently_omitted(self):
        module = self.module()
        original_scandir = os.scandir

        def denied(path):
            if str(path) == str(self.source / "references"):
                raise PermissionError("injected unreadable directory")
            return original_scandir(path)

        output = io.StringIO()
        with mock.patch.object(os, "scandir", denied), mock.patch.object(
            sys, "argv", [str(self.script), "--target-dir", str(self.target), "--dry-run"]
        ), redirect_stdout(output):
            status = module.main()
        self.assertNotEqual(status, 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "error")
        self.assertFalse(self.target.parent.exists())

    def test_help_is_json_without_selecting_or_writing_a_target(self):
        self.assertEqual(self.cli("--help")["status"], "help")
        self.assertFalse(self.target.parent.exists())

    def test_destination_files_links_and_extra_or_missing_paths_fail_closed(self):
        self.target.parent.mkdir()
        self.target.write_bytes(b"not a skill directory")
        self.cli("--target-dir", self.target, "--replace", success=False)
        self.assertEqual(self.target.read_bytes(), b"not a skill directory")
        self.target.unlink()
        self.cli("--target-dir", self.target)
        link = self.target / "dangling-link"
        link.symlink_to(self.root / "nonexistent")
        self.cli("--target-dir", self.target, "--replace", success=False)
        link.unlink()
        extra = self.target / "extra-empty-directory"
        extra.mkdir()
        self.cli("--target-dir", self.target, "--check", success=False)
        extra.rmdir()
        (self.target / "references" / "data.bin").unlink()
        self.cli("--target-dir", self.target, "--check", success=False)
        self.assertEqual(list(self.target.parent.iterdir()), [self.target])


if __name__ == "__main__":
    unittest.main()
