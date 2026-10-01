import os
from pathlib import Path
import subprocess
import sys
import unittest


class TestCLIEncoding(unittest.TestCase):
    def test_help_with_legacy_redirected_encoding(self):
        result = subprocess.run(
            [sys.executable, str(Path(__file__).resolve().parents[1] / "cli.py"), "--help"],
            env={**os.environ, "PYTHONIOENCODING": "cp1252"},
            capture_output=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("抓取工具", result.stdout.decode("utf-8"))
