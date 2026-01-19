import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from state_ledger.boundary import register_entity, assign_owner, emit_state_declaration, get_declarations
import database


class TestStateEvidenceRefs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp()
        cls.test_db_path = Path(cls.test_dir) / "test_state_evidence_refs.db"
        os.environ["TEST_DB_PATH"] = str(cls.test_db_path)
        database.require_test_db("state evidence refs tests")

        result = subprocess.run(
            [sys.executable, "scripts/reset_db.py", "--db-path", str(cls.test_db_path)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        if result.returncode != 0:
            raise RuntimeError(f"reset_db failed: {result.stderr}")

    @classmethod
    def tearDownClass(cls):
        if cls.test_db_path.exists():
            cls.test_db_path.unlink()
        for suffix in ("-wal", "-shm"):
            extra = Path(str(cls.test_db_path) + suffix)
            if extra.exists():
                extra.unlink()

    def test_evidence_refs_stored_inert(self):
        entity_ref = "org:acme/entity:project:beta"
        scope_ref = "org:acme/scope:weekly"
        actor_ref = "org:acme/actor:owner"

        register_entity(entity_ref, "Acme Beta", cadence_days=7)
        assign_owner(entity_ref, actor_ref, "org:acme/actor:admin")

        evidence_refs = [
            {"type": "cutter_event", "ref": "cutter:event:123"},
            {"type": "ops_artifact", "ref": "ops:quote:456"}
        ]

        emit_state_declaration(
            entity_ref=entity_ref,
            scope_ref=scope_ref,
            state_text="State is unchanged",
            actor_ref=actor_ref,
            declaration_kind="REAFFIRMATION",
            evidence_refs=evidence_refs
        )

        declarations = get_declarations(entity_ref=entity_ref)
        self.assertGreaterEqual(len(declarations), 1)
        latest = declarations[0]
        self.assertIn("evidence_refs_json", latest)
        self.assertIsNotNone(latest["evidence_refs_json"])


if __name__ == "__main__":
    unittest.main()
