"""Testes locais da proteção contra mutação pelo Reviewer."""

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "orchestration" / "orchestrator.py"
SPEC = importlib.util.spec_from_file_location("orchestrator", MODULE_PATH)
orchestrator = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = orchestrator
SPEC.loader.exec_module(orchestrator)


class WorkspaceFingerprintTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        (self.root / "tracked.txt").write_text("inicial\n", encoding="utf-8")
        subprocess.run(["git", "add", "tracked.txt"], cwd=self.root, check=True)
        self.previous_root = orchestrator.ROOT
        orchestrator.ROOT = self.root

    def tearDown(self) -> None:
        orchestrator.ROOT = self.previous_root
        self.temporary_directory.cleanup()

    def test_detecta_conteudo_untracked_e_estados_tracked_e_staged(self) -> None:
        original = orchestrator.workspace_fingerprint()

        untracked = self.root / "temporario.txt"
        untracked.write_text("primeira versão\n", encoding="utf-8")
        with_untracked = orchestrator.workspace_fingerprint()
        self.assertNotEqual(original, with_untracked)

        untracked.write_text("segunda versão\n", encoding="utf-8")
        self.assertNotEqual(with_untracked, orchestrator.workspace_fingerprint())

        (self.root / "tracked.txt").write_text("alterado sem stage\n", encoding="utf-8")
        with_worktree_change = orchestrator.workspace_fingerprint()
        self.assertNotEqual(original, with_worktree_change)

        subprocess.run(["git", "add", "tracked.txt"], cwd=self.root, check=True)
        self.assertNotEqual(with_worktree_change, orchestrator.workspace_fingerprint())


if __name__ == "__main__":
    unittest.main()
