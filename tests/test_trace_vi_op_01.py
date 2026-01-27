import shutil
import subprocess
import unittest
from pathlib import Path


class TraceVIOp01Tests(unittest.TestCase):
    def test_manual_quote_failure_events_visible(self) -> None:
        node_path = shutil.which("node")
        self.assertIsNotNone(node_path, "node is required to run the runtime test")

        repo_root = Path(__file__).resolve().parents[1]
        test_file = repo_root / "tests" / "test_trace_vi_op_01_runtime.js"

        result = subprocess.run(
            [node_path, str(test_file)],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            output = "\n".join(
                [
                    "Runtime failure visibility test failed.",
                    "stdout:",
                    result.stdout,
                    "stderr:",
                    result.stderr,
                ]
            )
            self.fail(output)


if __name__ == "__main__":
    unittest.main()
