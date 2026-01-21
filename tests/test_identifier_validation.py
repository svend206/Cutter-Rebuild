"""
Test Guild-Safe Identifier Validation

Verifies constitutional enforcement of identifier format conventions.
See: canon/constitution/identifier_conventions.md
"""

import unittest
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from state_ledger import validation


class TestOrgRefValidation(unittest.TestCase):
    """Test org_ref format validation."""
    
    def test_valid_org_refs(self):
        """Valid org_ref formats should pass."""
        valid_refs = [
            "org:acme.com",
            "org:shop-42",
            "org:guild-a",
            "org:a",
            "org:test-org.example.com",
            "org:sub.domain.example",
        ]
        
        for ref in valid_refs:
            with self.subTest(ref=ref):
                is_valid, error = validation.validate_org_ref(ref)
                self.assertTrue(is_valid, f"Expected valid, got error: {error}")
                self.assertEqual(error, "")
    
    def test_invalid_org_refs(self):
        """Invalid org_ref formats should fail with clear errors."""
        invalid_cases = [
            ("", "org_ref cannot be empty"),
            ("acme.com", "org_ref must start with 'org:'"),
            ("org:", "org_ref format invalid"),
            ("Org:acme.com", "org_ref must be lowercase"),
            ("org:ACME.COM", "org_ref must be lowercase"),
            ("org:acme com", "org_ref format invalid"),
            ("org:acme_com", "org_ref format invalid"),
            ("org:acme/com", "org_ref format invalid"),
            ("org:" + "a" * 254, "org_ref too long"),
        ]
        
        for ref, expected_substring in invalid_cases:
            with self.subTest(ref=ref):
                is_valid, error = validation.validate_org_ref(ref)
                self.assertFalse(is_valid, f"Expected invalid for: {ref}")
                self.assertIn(expected_substring, error.lower(), 
                             f"Expected '{expected_substring}' in error: {error}")


class TestActorRefValidation(unittest.TestCase):
    """Test actor_ref format validation."""
    
    def test_valid_actor_refs(self):
        """Valid actor_ref formats should pass."""
        valid_refs = [
            "org:acme.com/actor:alice",
            "org:shop-42/actor:bob.smith",
            "org:guild-a/actor:operator-7",
            "org:test/actor:a",
            "org:example.com/actor:user_123",
        ]
        
        for ref in valid_refs:
            with self.subTest(ref=ref):
                is_valid, error = validation.validate_actor_ref(ref)
                self.assertTrue(is_valid, f"Expected valid, got error: {error}")
                self.assertEqual(error, "")
    
    def test_invalid_actor_refs(self):
        """Invalid actor_ref formats should fail with clear errors."""
        invalid_cases = [
            ("", "actor_ref cannot be empty"),
            ("alice", "actor_ref must contain '/actor:'"),
            ("org:acme.com/alice", "actor_ref must contain '/actor:'"),
            ("org:acme.com/actor:", "actor_ref format invalid"),
            ("Org:acme.com/actor:alice", "actor_ref must be lowercase"),
            ("org:acme.com/Actor:alice", "actor_ref must be lowercase"),
            ("org:acme.com/actor:Alice", "actor_ref must be lowercase"),
            ("invalid-org/actor:alice", "actor_ref has invalid org prefix"),
            ("org:acme.com/actor:alice bob", "actor_ref format invalid"),
        ]
        
        for ref, expected_substring in invalid_cases:
            with self.subTest(ref=ref):
                is_valid, error = validation.validate_actor_ref(ref)
                self.assertFalse(is_valid, f"Expected invalid for: {ref}")
                self.assertIn(expected_substring, error.lower(), 
                             f"Expected '{expected_substring}' in error: {error}")


class TestEntityRefValidation(unittest.TestCase):
    """Test entity_ref format validation."""
    
    def test_valid_entity_refs(self):
        """Valid entity_ref formats should pass."""
        valid_refs = [
            "org:acme.com/entity:customer:cust-123",
            "org:shop-42/entity:project:proj-alpha",
            "org:guild-a/entity:dept:engineering",
            "org:acme.com/entity:quote:q-2026-001",
            "org:test/entity:thing:x",
            "org:example.com/entity:customer:c_123",
        ]
        
        for ref in valid_refs:
            with self.subTest(ref=ref):
                is_valid, error = validation.validate_entity_ref(ref)
                self.assertTrue(is_valid, f"Expected valid, got error: {error}")
                self.assertEqual(error, "")
    
    def test_invalid_entity_refs(self):
        """Invalid entity_ref formats should fail with clear errors."""
        invalid_cases = [
            ("", "entity_ref cannot be empty"),
            ("customer:123", "entity_ref must contain '/entity:'"),
            ("org:acme.com/customer:123", "entity_ref must contain '/entity:'"),
            ("org:acme.com/entity:customer", "entity_ref must have format"),
            ("org:acme.com/entity::123", "entity_ref format invalid"),
            ("Org:acme.com/entity:customer:123", "entity_ref must be lowercase"),
            ("org:acme.com/Entity:customer:123", "entity_ref must be lowercase"),
            ("org:acme.com/entity:Customer:123", "entity_ref must be lowercase"),
            ("org:acme.com/entity:customer:Cust-123", "entity_ref must be lowercase"),
            ("invalid-org/entity:customer:123", "entity_ref has invalid org prefix"),
        ]
        
        for ref, expected_substring in invalid_cases:
            with self.subTest(ref=ref):
                is_valid, error = validation.validate_entity_ref(ref)
                self.assertFalse(is_valid, f"Expected invalid for: {ref}")
                self.assertIn(expected_substring, error.lower(), 
                             f"Expected '{expected_substring}' in error: {error}")


class TestScopeRefValidation(unittest.TestCase):
    """Test scope_ref format validation."""
    
    def test_valid_scope_refs(self):
        """Valid scope_ref formats should pass."""
        valid_refs = [
            "org:acme.com/scope:weekly-review",
            "org:shop-42/scope:q1-2026",
            "org:guild-a/scope:ops",
            "org:test/scope:x",
            "org:example.com/scope:dept:engineering",
        ]
        
        for ref in valid_refs:
            with self.subTest(ref=ref):
                is_valid, error = validation.validate_scope_ref(ref)
                self.assertTrue(is_valid, f"Expected valid, got error: {error}")
                self.assertEqual(error, "")
    
    def test_invalid_scope_refs(self):
        """Invalid scope_ref formats should fail with clear errors."""
        invalid_cases = [
            ("", "scope_ref cannot be empty"),
            ("weekly", "scope_ref must contain '/scope:'"),
            ("org:acme.com/weekly", "scope_ref must contain '/scope:'"),
            ("org:acme.com/scope:", "scope_ref format invalid"),
            ("Org:acme.com/scope:weekly", "scope_ref must be lowercase"),
            ("org:acme.com/Scope:weekly", "scope_ref must be lowercase"),
            ("org:acme.com/scope:Weekly", "scope_ref must be lowercase"),
            ("invalid-org/scope:weekly", "scope_ref has invalid org prefix"),
        ]
        
        for ref, expected_substring in invalid_cases:
            with self.subTest(ref=ref):
                is_valid, error = validation.validate_scope_ref(ref)
                self.assertFalse(is_valid, f"Expected invalid for: {ref}")
                self.assertIn(expected_substring, error.lower(), 
                             f"Expected '{expected_substring}' in error: {error}")


class TestBoundaryIntegration(unittest.TestCase):
    """Test that boundary module enforces identifier validation."""
    
    def setUp(self):
        """Set up test database path."""
        import tempfile
        import database
        import sqlite3
        
        # Use isolated test database
        temp_dir = tempfile.gettempdir()
        self.test_db = Path(temp_dir) / "test_identifiers.db"
        
        if self.test_db.exists():
            self.test_db.unlink()
        
        os.environ["TEST_DB_PATH"] = str(self.test_db)
        
        # Reload database to pick up TEST_DB_PATH
        import importlib
        importlib.reload(database)
        
        # Initialize database (creates Ops + Cutter tables)
        database.initialize_database()
        
        # Create State Ledger tables directly
        conn = sqlite3.connect(self.test_db)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS state__entities (
                entity_ref TEXT PRIMARY KEY,
                entity_label TEXT,
                cadence_days INTEGER NOT NULL DEFAULT 7,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS state__recognition_owners (
                assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_ref TEXT NOT NULL,
                owner_actor_ref TEXT NOT NULL,
                assigned_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                unassigned_at TEXT,
                assigned_by_actor_ref TEXT NOT NULL,
                FOREIGN KEY (entity_ref) REFERENCES state__entities(entity_ref)
            );
            
            CREATE UNIQUE INDEX IF NOT EXISTS idx_current_owner 
            ON state__recognition_owners(entity_ref) 
            WHERE unassigned_at IS NULL;
            
            CREATE TABLE IF NOT EXISTS state__declarations (
                declaration_id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_ref TEXT NOT NULL,
                scope_ref TEXT NOT NULL,
                state_text TEXT NOT NULL,
                classification TEXT,
                declared_by_actor_ref TEXT NOT NULL,
                declared_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                declaration_kind TEXT NOT NULL CHECK (declaration_kind IN ('REAFFIRMATION','RECLASSIFICATION')),
                supersedes_declaration_id INTEGER,
                cutter_evidence_ref TEXT,
                evidence_refs_json TEXT DEFAULT '[]',
                FOREIGN KEY (entity_ref) REFERENCES state__entities(entity_ref)
            );
            
            -- Append-only enforcement triggers
            CREATE TRIGGER IF NOT EXISTS prevent_declaration_updates
            BEFORE UPDATE ON state__declarations
            BEGIN
                SELECT RAISE(ABORT, 'Constitutional violation: State declarations are append-only (C4: Irreversible Memory)');
            END;
            
            CREATE TRIGGER IF NOT EXISTS prevent_declaration_deletes
            BEFORE DELETE ON state__declarations
            BEGIN
                SELECT RAISE(ABORT, 'Constitutional violation: State declarations cannot be deleted (C4: Irreversible Memory)');
            END;
        """)
        conn.commit()
        conn.close()
        
        # Update boundary module's DB_PATH
        from state_ledger import boundary
        boundary.DB_PATH = self.test_db
    
    def tearDown(self):
        """Clean up test database."""
        if self.test_db.exists():
            self.test_db.unlink()
    
    def test_register_entity_rejects_invalid_entity_ref(self):
        """register_entity should reject malformed entity_ref."""
        from state_ledger.boundary import register_entity
        
        invalid_refs = [
            "customer:123",  # Missing org prefix
            "org:acme.com/customer:123",  # Missing /entity:
            "Customer:123",  # No org, uppercase
        ]
        
        for ref in invalid_refs:
            with self.subTest(ref=ref):
                with self.assertRaises(ValueError) as ctx:
                    register_entity(ref)
                self.assertIn("invalid entity_ref", str(ctx.exception).lower())
    
    def test_register_entity_accepts_valid_entity_ref(self):
        """register_entity should accept well-formed entity_ref."""
        from state_ledger.boundary import register_entity
        
        result = register_entity("org:test-shop/entity:customer:cust-001")
        self.assertTrue(result)
    
    def test_assign_owner_rejects_invalid_refs(self):
        """assign_owner should reject malformed refs."""
        from state_ledger.boundary import register_entity, assign_owner
        
        # Register valid entity first
        register_entity("org:test-shop/entity:customer:cust-001")
        
        # Test invalid entity_ref
        with self.assertRaises(ValueError) as ctx:
            assign_owner(
                entity_ref="customer:001",
                owner_actor_ref="org:test-shop/actor:alice",
                assigned_by_actor_ref="org:test-shop/actor:admin"
            )
        self.assertIn("invalid entity_ref", str(ctx.exception).lower())
        
        # Test invalid owner_actor_ref
        with self.assertRaises(ValueError) as ctx:
            assign_owner(
                entity_ref="org:test-shop/entity:customer:cust-001",
                owner_actor_ref="alice",
                assigned_by_actor_ref="org:test-shop/actor:admin"
            )
        self.assertIn("invalid owner_actor_ref", str(ctx.exception).lower())
        
        # Test invalid assigned_by_actor_ref
        with self.assertRaises(ValueError) as ctx:
            assign_owner(
                entity_ref="org:test-shop/entity:customer:cust-001",
                owner_actor_ref="org:test-shop/actor:alice",
                assigned_by_actor_ref="admin"
            )
        self.assertIn("invalid assigned_by_actor_ref", str(ctx.exception).lower())
    
    def test_emit_state_declaration_rejects_invalid_refs(self):
        """emit_state_declaration should reject malformed refs."""
        from state_ledger.boundary import register_entity, assign_owner, emit_state_declaration
        
        # Set up valid entity with owner
        register_entity("org:test-shop/entity:customer:cust-001")
        assign_owner(
            entity_ref="org:test-shop/entity:customer:cust-001",
            owner_actor_ref="org:test-shop/actor:alice",
            assigned_by_actor_ref="org:test-shop/actor:admin"
        )
        
        # Test invalid entity_ref
        with self.assertRaises(ValueError) as ctx:
            emit_state_declaration(
                entity_ref="customer:001",
                scope_ref="org:test-shop/scope:weekly",
                state_text="Customer is active",
                actor_ref="org:test-shop/actor:alice",
                declaration_kind="RECLASSIFICATION"
            )
        self.assertIn("identifier format validation failed", str(ctx.exception).lower())
        
        # Test invalid scope_ref
        with self.assertRaises(ValueError) as ctx:
            emit_state_declaration(
                entity_ref="org:test-shop/entity:customer:cust-001",
                scope_ref="weekly",
                state_text="Customer is active",
                actor_ref="org:test-shop/actor:alice",
                declaration_kind="RECLASSIFICATION"
            )
        self.assertIn("identifier format validation failed", str(ctx.exception).lower())
        
        # Test invalid actor_ref
        with self.assertRaises(ValueError) as ctx:
            emit_state_declaration(
                entity_ref="org:test-shop/entity:customer:cust-001",
                scope_ref="org:test-shop/scope:weekly",
                state_text="Customer is active",
                actor_ref="alice",
                declaration_kind="RECLASSIFICATION"
            )
        self.assertIn("identifier format validation failed", str(ctx.exception).lower())
    
    def test_emit_state_declaration_accepts_valid_refs(self):
        """emit_state_declaration should accept well-formed refs."""
        from state_ledger.boundary import register_entity, assign_owner, emit_state_declaration
        
        # Set up valid entity with owner
        register_entity("org:test-shop/entity:customer:cust-001")
        assign_owner(
            entity_ref="org:test-shop/entity:customer:cust-001",
            owner_actor_ref="org:test-shop/actor:alice",
            assigned_by_actor_ref="org:test-shop/actor:admin"
        )
        
        # Should succeed with valid refs
        declaration_id = emit_state_declaration(
            entity_ref="org:test-shop/entity:customer:cust-001",
            scope_ref="org:test-shop/scope:weekly",
            state_text="Customer is active and responsive",
            actor_ref="org:test-shop/actor:alice",
            declaration_kind="RECLASSIFICATION"
        )
        
        self.assertIsInstance(declaration_id, int)
        self.assertGreater(declaration_id, 0)


class TestMultiGuildScenario(unittest.TestCase):
    """Test that Guild-safe identifiers prevent collisions."""
    
    def setUp(self):
        """Set up test database."""
        import tempfile
        import database
        import sqlite3
        
        temp_dir = tempfile.gettempdir()
        self.test_db = Path(temp_dir) / "test_multiguild.db"
        
        if self.test_db.exists():
            self.test_db.unlink()
        
        os.environ["TEST_DB_PATH"] = str(self.test_db)
        
        import importlib
        importlib.reload(database)
        database.initialize_database()
        
        # Create State Ledger tables directly
        conn = sqlite3.connect(self.test_db)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS state__entities (
                entity_ref TEXT PRIMARY KEY,
                entity_label TEXT,
                cadence_days INTEGER NOT NULL DEFAULT 7,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS state__recognition_owners (
                assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_ref TEXT NOT NULL,
                owner_actor_ref TEXT NOT NULL,
                assigned_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                unassigned_at TEXT,
                assigned_by_actor_ref TEXT NOT NULL,
                FOREIGN KEY (entity_ref) REFERENCES state__entities(entity_ref)
            );
            
            CREATE UNIQUE INDEX IF NOT EXISTS idx_current_owner 
            ON state__recognition_owners(entity_ref) 
            WHERE unassigned_at IS NULL;
            
            CREATE TABLE IF NOT EXISTS state__declarations (
                declaration_id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_ref TEXT NOT NULL,
                scope_ref TEXT NOT NULL,
                state_text TEXT NOT NULL,
                classification TEXT,
                declared_by_actor_ref TEXT NOT NULL,
                declared_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                declaration_kind TEXT NOT NULL CHECK (declaration_kind IN ('REAFFIRMATION','RECLASSIFICATION')),
                supersedes_declaration_id INTEGER,
                cutter_evidence_ref TEXT,
                evidence_refs_json TEXT DEFAULT '[]',
                FOREIGN KEY (entity_ref) REFERENCES state__entities(entity_ref)
            );
        """)
        conn.commit()
        conn.close()
        
        from state_ledger import boundary
        boundary.DB_PATH = self.test_db
    
    def tearDown(self):
        """Clean up test database."""
        # Close any open connections first
        import gc
        gc.collect()
        
        import time
        for _ in range(3):
            try:
                if self.test_db.exists():
                    self.test_db.unlink()
                break
            except PermissionError:
                time.sleep(0.1)
    
    def test_two_guilds_same_local_ids_no_collision(self):
        """Two guilds can use same local IDs without collision."""
        from state_ledger.boundary import register_entity, assign_owner, emit_state_declaration
        
        # Guild A
        register_entity("org:guild-a/entity:customer:acme-inc")
        assign_owner(
            entity_ref="org:guild-a/entity:customer:acme-inc",
            owner_actor_ref="org:guild-a/actor:owner",
            assigned_by_actor_ref="org:guild-a/actor:owner"
        )
        
        # Guild B (same local ID "acme-inc" but different org)
        register_entity("org:guild-b/entity:customer:acme-inc")
        assign_owner(
            entity_ref="org:guild-b/entity:customer:acme-inc",
            owner_actor_ref="org:guild-b/actor:owner",
            assigned_by_actor_ref="org:guild-b/actor:owner"
        )
        
        # Both can emit declarations without collision
        decl_a = emit_state_declaration(
            entity_ref="org:guild-a/entity:customer:acme-inc",
            scope_ref="org:guild-a/scope:monthly",
            state_text="Customer is active in guild A",
            actor_ref="org:guild-a/actor:owner",
            declaration_kind="RECLASSIFICATION"
        )
        
        decl_b = emit_state_declaration(
            entity_ref="org:guild-b/entity:customer:acme-inc",
            scope_ref="org:guild-b/scope:monthly",
            state_text="Customer is active in guild B",
            actor_ref="org:guild-b/actor:owner",
            declaration_kind="RECLASSIFICATION"
        )
        
        self.assertNotEqual(decl_a, decl_b)
        
        # Verify both entities exist separately
        from state_ledger.boundary import get_declarations
        decls_a = get_declarations(entity_ref="org:guild-a/entity:customer:acme-inc")
        decls_b = get_declarations(entity_ref="org:guild-b/entity:customer:acme-inc")
        
        self.assertEqual(len(decls_a), 1)
        self.assertEqual(len(decls_b), 1)
        self.assertNotEqual(decls_a[0]['declaration_id'], decls_b[0]['declaration_id'])


if __name__ == '__main__':
    unittest.main()
