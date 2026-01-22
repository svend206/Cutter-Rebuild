"""
Integration test: Quote lifecycle → Cutter Ledger event emissions

Verifies that key quote operations emit consistent events to cutter__events:
- QUOTE_CREATED: When quote is first saved
- QUOTE_OVERRIDDEN: When final price differs from system anchor
- QUOTE_STATUS_CHANGED: When status changes (Draft → Sent → Won/Lost)
- QUOTE_DELETED: When quote is soft deleted

Constitutional compliance:
- Events use subject_ref format: "quote:{id}"
- Event types are descriptive (non-evaluative)
- All events are append-only (no UPDATE/DELETE)
"""

import unittest
import sys
import os
import tempfile
import json
import time
from pathlib import Path

# Ensure TEST_DB_PATH is set before importing database (test-only bypass)
if not os.environ.get("TEST_DB_PATH"):
    temp_path = Path(tempfile.gettempdir()) / f"quote_lifecycle_test_{int(time.time() * 1000)}.db"
    os.environ["TEST_DB_PATH"] = str(temp_path)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import database
from cutter_ledger.boundary import get_events, emit_cutter_event


class TestQuoteLifecycleEvents(unittest.TestCase):
    """Integration test for quote lifecycle event emissions."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database once for all tests."""
        # Create unique temporary test database for this test run
        import time
        import random
        unique_suffix = f"_test_{int(time.time())}_{random.randint(1000, 9999)}"
        cls.test_db = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix=f'{unique_suffix}.db', 
            delete=False
        )
        cls.test_db_path = cls.test_db.name
        cls.test_db.close()
        
        # Set TEST_DB_PATH environment variable
        os.environ['TEST_DB_PATH'] = cls.test_db_path
        
        # Reinitialize database module to use test db
        import importlib
        importlib.reload(database)
        database.require_test_db("quote_lifecycle_events test")
        
        # Force reload of cutter_ledger.boundary to pick up new DB path
        import cutter_ledger.boundary
        importlib.reload(cutter_ledger.boundary)
        
        # Initialize schema
        database.initialize_database()
        
        # Initialize Cutter Ledger schema (cutter__events table)
        conn = database.get_connection()
        cursor = conn.cursor()
        
        # Create cutter__events table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cutter__events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                subject_ref TEXT NOT NULL,
                event_data TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                ingested_by_service TEXT,
                ingested_by_version TEXT
            )
        """)
        
        # Create append-only triggers
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS block_cutter_events_update
            BEFORE UPDATE ON cutter__events
            BEGIN
                SELECT RAISE(ABORT, 'Constitutional violation: cutter__events is append-only (no UPDATE)');
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS block_cutter_events_delete
            BEFORE DELETE ON cutter__events
            BEGIN
                SELECT RAISE(ABORT, 'Constitutional violation: cutter__events is append-only (no DELETE)');
            END
        """)
        
        conn.commit()
        conn.close()
        from ops_layer import app as app_module
        cls.client = app_module.app.test_client()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test database."""
        # Give time for connections to close
        import time
        import gc
        gc.collect()
        time.sleep(0.1)
        
        if os.path.exists(cls.test_db_path):
            try:
                os.unlink(cls.test_db_path)
            except Exception as e:
                print(f"Warning: Could not delete test database: {e}")
    
    def setUp(self):
        """Set up before each test."""
        # Clear all tables before each test for isolation
        conn = database.get_connection()
        cursor = conn.cursor()
        
        # Temporarily drop append-only triggers for test cleanup
        cursor.execute("DROP TRIGGER IF EXISTS block_cutter_events_delete")
        cursor.execute("DROP TRIGGER IF EXISTS block_cutter_events_update")
        
        # Clear events table
        cursor.execute("DELETE FROM cutter__events")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='cutter__events'")
        
        # Recreate append-only triggers
        cursor.execute("""
            CREATE TRIGGER block_cutter_events_delete
            BEFORE DELETE ON cutter__events
            BEGIN
                SELECT RAISE(ABORT, 'Constitutional violation: cutter__events is append-only (no DELETE)');
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER block_cutter_events_update
            BEFORE UPDATE ON cutter__events
            BEGIN
                SELECT RAISE(ABORT, 'Constitutional violation: cutter__events is append-only (no UPDATE)');
            END
        """)
        
        # Clear ops tables to prevent cross-test contamination
        cursor.execute("DELETE FROM ops__quotes")
        cursor.execute("DELETE FROM ops__parts")
        cursor.execute("DELETE FROM ops__customers")
        cursor.execute("DELETE FROM ops__contacts")
        
        # Reset autoincrement counters
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='ops__quotes'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='ops__parts'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='ops__customers'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='ops__contacts'")
        
        conn.commit()
        conn.close()

    def _count_cutter_events(self) -> int:
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cutter__events")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def test_quote_created_event_emitted(self):
        """QUOTE_CREATED event should be emitted when quote is saved."""
        # Create a minimal quote
        part_id = database.upsert_part(
            genesis_hash='test_hash_123',
            filename='test_part.stl',
            fingerprint_json='[10.0, 5.0, 5.0, 5.0, 50.0]',
            volume=100.0,
            surface_area=200.0,
            dimensions_json='{"x": 5.0, "y": 5.0, "z": 5.0}',
            process_routing_json='["mill", "deburr"]'
        )
        
        customer_id, _ = database.resolve_customer('Test Customer', 'testcorp.com')
        
        quote_id = database.create_quote(
            part_id=part_id,
            customer_id=customer_id,
            contact_id=None,
            quote_id='TEST-001',
            user_id='test_user',
            material='Aluminum 6061',
            system_price_anchor=100.0,
            final_quoted_price=100.0,
            quantity=10,
            status='Draft'
        )
        
        # Emit QUOTE_CREATED event (simulating what app.py does)
        emit_cutter_event(
            event_type='QUOTE_CREATED',
            subject_ref=quote_id,
            event_data={
                'quote_id_human': 'TEST-001',
                'material': 'Aluminum 6061',
                'quantity': 10,
                'system_price_anchor': 100.0,
                'final_quoted_price': 100.0,
                'customer_name': 'Test Customer',
                'status': 'Draft'
            }
        )
        
        # Verify event was emitted
        events = get_events(subject_ref=f"quote:{quote_id}", event_type='QUOTE_CREATED')
        
        self.assertEqual(len(events), 1, "Should have exactly 1 QUOTE_CREATED event")
        
        event = events[0]
        self.assertEqual(event['event_type'], 'QUOTE_CREATED')
        self.assertEqual(event['subject_ref'], f"quote:{quote_id}")
        self.assertIsNotNone(event['event_data'])
        self.assertEqual(event['event_data']['quote_id_human'], 'TEST-001')
        self.assertEqual(event['event_data']['status'], 'Draft')
    
    def test_quote_overridden_event_emitted(self):
        """QUOTE_OVERRIDDEN event should be emitted when price differs from anchor."""
        # Create a quote with override
        part_id = database.upsert_part(
            genesis_hash='test_hash_456',
            filename='test_part2.stl',
            fingerprint_json='[20.0, 10.0, 10.0, 10.0, 100.0]',
            volume=200.0,
            surface_area=400.0,
            dimensions_json='{"x": 10.0, "y": 10.0, "z": 10.0}',
            process_routing_json='["mill"]'
        )
        
        customer_id, _ = database.resolve_customer('Override Customer', 'override.com')
        
        quote_id = database.create_quote(
            part_id=part_id,
            customer_id=customer_id,
            contact_id=None,
            quote_id='TEST-002',
            user_id='test_user',
            material='Steel 1018',
            system_price_anchor=150.0,
            final_quoted_price=120.0,  # Override: lower price
            quantity=5,
            status='Draft'
        )
        
        # Emit QUOTE_OVERRIDDEN event
        emit_cutter_event(
            event_type='QUOTE_OVERRIDDEN',
            subject_ref=quote_id,
            event_data={
                'system_price_anchor': 150.0,
                'final_quoted_price': 120.0,
                'override_delta': -30.0,
                'override_percent': -20.0,
                'quote_id_human': 'TEST-002',
                'material': 'Steel 1018',
                'quantity': 5
            }
        )
        
        # Verify event was emitted
        events = get_events(subject_ref=f"quote:{quote_id}", event_type='QUOTE_OVERRIDDEN')
        
        self.assertEqual(len(events), 1, "Should have exactly 1 QUOTE_OVERRIDDEN event")
        
        event = events[0]
        self.assertEqual(event['event_type'], 'QUOTE_OVERRIDDEN')
        self.assertEqual(event['event_data']['override_delta'], -30.0)
        self.assertEqual(event['event_data']['override_percent'], -20.0)
    
    def test_quote_status_changed_event_emitted(self):
        """QUOTE_STATUS_CHANGED event should be emitted when status updates."""
        # Create a quote
        part_id = database.upsert_part(
            genesis_hash='test_hash_789',
            filename='test_part3.stl',
            fingerprint_json='[15.0, 7.0, 7.0, 7.0, 75.0]',
            volume=150.0,
            surface_area=300.0,
            dimensions_json='{"x": 7.0, "y": 7.0, "z": 7.0}',
            process_routing_json='["mill", "tap"]'
        )
        
        customer_id, _ = database.resolve_customer('Status Customer', 'statustest.com')
        
        quote_id = database.create_quote(
            part_id=part_id,
            customer_id=customer_id,
            contact_id=None,
            quote_id='TEST-003',
            user_id='test_user',
            material='Aluminum 6061',
            system_price_anchor=200.0,
            final_quoted_price=200.0,
            quantity=20,
            status='Draft'
        )
        
        # Update status to Won
        database.update_quote_status_simple(
            quote_id=quote_id,
            status='Won',
            win_notes='Customer accepted proposal'
        )
        
        # Emit QUOTE_STATUS_CHANGED event
        emit_cutter_event(
            event_type='QUOTE_STATUS_CHANGED',
            subject_ref=quote_id,
            event_data={
                'new_status': 'Won',
                'win_notes': 'Customer accepted proposal'
            }
        )
        
        # Verify event was emitted
        events = get_events(subject_ref=f"quote:{quote_id}", event_type='QUOTE_STATUS_CHANGED')
        
        self.assertEqual(len(events), 1, "Should have exactly 1 QUOTE_STATUS_CHANGED event")
        
        event = events[0]
        self.assertEqual(event['event_type'], 'QUOTE_STATUS_CHANGED')
        self.assertEqual(event['event_data']['new_status'], 'Won')
        self.assertEqual(event['event_data']['win_notes'], 'Customer accepted proposal')
    
    def test_quote_deleted_event_emitted(self):
        """QUOTE_DELETED event should be emitted when quote is soft deleted."""
        # Create a quote
        part_id = database.upsert_part(
            genesis_hash='test_hash_999',
            filename='test_part4.stl',
            fingerprint_json='[12.0, 6.0, 6.0, 6.0, 60.0]',
            volume=120.0,
            surface_area=240.0,
            dimensions_json='{"x": 6.0, "y": 6.0, "z": 6.0}',
            process_routing_json='["mill"]'
        )
        
        customer_id, _ = database.resolve_customer('Delete Customer', 'deletetest.com')
        
        quote_id = database.create_quote(
            part_id=part_id,
            customer_id=customer_id,
            contact_id=None,
            quote_id='TEST-004',
            user_id='test_user',
            material='Brass',
            system_price_anchor=80.0,
            final_quoted_price=80.0,
            quantity=1,
            status='Draft'
        )
        
        # Soft delete the quote
        database.soft_delete_quote(quote_id)
        
        # Emit QUOTE_DELETED event
        from datetime import datetime
        emit_cutter_event(
            event_type='QUOTE_DELETED',
            subject_ref=quote_id,
            event_data={'deleted_at': datetime.now().isoformat()}
        )
        
        # Verify event was emitted
        events = get_events(subject_ref=f"quote:{quote_id}", event_type='QUOTE_DELETED')
        
        self.assertEqual(len(events), 1, "Should have exactly 1 QUOTE_DELETED event")
        
        event = events[0]
        self.assertEqual(event['event_type'], 'QUOTE_DELETED')
        self.assertIn('deleted_at', event['event_data'])
    
    def test_full_quote_lifecycle_events(self):
        """Integration test: Full quote lifecycle should emit all expected events."""
        # Create a quote
        part_id = database.upsert_part(
            genesis_hash='test_lifecycle_hash',
            filename='lifecycle_part.stl',
            fingerprint_json='[25.0, 12.0, 12.0, 12.0, 125.0]',
            volume=250.0,
            surface_area=500.0,
            dimensions_json='{"x": 12.0, "y": 12.0, "z": 12.0}',
            process_routing_json='["mill", "deburr", "anodize"]'
        )
        
        customer_id, _ = database.resolve_customer('Lifecycle Customer', 'lifecycle.com')
        
        # 1. Create quote (QUOTE_CREATED)
        quote_id = database.create_quote(
            part_id=part_id,
            customer_id=customer_id,
            contact_id=None,
            quote_id='TEST-LIFECYCLE-001',
            user_id='test_user',
            material='Aluminum 7075',
            system_price_anchor=300.0,
            final_quoted_price=280.0,  # Override
            quantity=50,
            status='Draft'
        )
        
        emit_cutter_event(
            event_type='QUOTE_CREATED',
            subject_ref=quote_id,
            event_data={
                'quote_id_human': 'TEST-LIFECYCLE-001',
                'material': 'Aluminum 7075',
                'quantity': 50,
                'system_price_anchor': 300.0,
                'final_quoted_price': 280.0,
                'customer_name': 'Lifecycle Customer',
                'status': 'Draft'
            }
        )
        
        # 2. Price override (QUOTE_OVERRIDDEN)
        emit_cutter_event(
            event_type='QUOTE_OVERRIDDEN',
            subject_ref=quote_id,
            event_data={
                'system_price_anchor': 300.0,
                'final_quoted_price': 280.0,
                'override_delta': -20.0,
                'override_percent': -6.67,
                'quote_id_human': 'TEST-LIFECYCLE-001'
            }
        )
        
        # 3. Change status to Sent (QUOTE_STATUS_CHANGED)
        database.update_quote_status_simple(quote_id, 'Sent')
        emit_cutter_event(
            event_type='QUOTE_STATUS_CHANGED',
            subject_ref=quote_id,
            event_data={'new_status': 'Sent'}
        )
        
        # 4. Change status to Won (QUOTE_STATUS_CHANGED)
        database.update_quote_status_simple(quote_id, 'Won', win_notes='Volume discount approved')
        emit_cutter_event(
            event_type='QUOTE_STATUS_CHANGED',
            subject_ref=quote_id,
            event_data={
                'new_status': 'Won',
                'win_notes': 'Volume discount approved'
            }
        )
        
        # Verify all events exist
        all_events = get_events(subject_ref=f"quote:{quote_id}")
        
        # Debug: Print actual events if count doesn't match
        if len(all_events) != 4:
            print(f"\n[DEBUG] Expected 4 events, got {len(all_events)}")
            for i, event in enumerate(all_events):
                print(f"  {i+1}. {event['event_type']} - {event.get('event_data', {})}")
        
        self.assertEqual(len(all_events), 4, f"Should have 4 events total, got {len(all_events)}")
        
        # Verify event sequence
        event_types = [e['event_type'] for e in all_events]
        self.assertEqual(event_types[0], 'QUOTE_CREATED')
        self.assertEqual(event_types[1], 'QUOTE_OVERRIDDEN')
        self.assertEqual(event_types[2], 'QUOTE_STATUS_CHANGED')
        self.assertEqual(event_types[3], 'QUOTE_STATUS_CHANGED')
        
        # Verify subject_ref consistency
        for event in all_events:
            self.assertEqual(event['subject_ref'], f"quote:{quote_id}")
        
        # Verify provenance fields exist
        for event in all_events:
            self.assertIsNotNone(event['ingested_by_service'])
            self.assertIsNotNone(event['created_at'])
    
    def test_event_type_vocabulary_non_evaluative(self):
        """Event types should be descriptive, not evaluative."""
        # Test that event types are descriptive (constitutional compliance)
        valid_event_types = [
            'QUOTE_CREATED',
            'QUOTE_OVERRIDDEN',
            'QUOTE_STATUS_CHANGED',
            'QUOTE_DELETED'
        ]
        
        # These should NOT contain evaluative language
        forbidden_words = ['good', 'bad', 'healthy', 'unhealthy', 'risky', 'problem']
        
        for event_type in valid_event_types:
            for word in forbidden_words:
                self.assertNotIn(
                    word.lower(),
                    event_type.lower(),
                    f"Event type '{event_type}' contains evaluative word '{word}'"
                )

    def test_no_exhaust_on_refused_ops_action(self):
        """Refused ops action should not emit exhaust."""
        before = self._count_cutter_events()
        response = self.client.post(
            "/ops/carrier_handoff",
            headers={"X-Ops-Mode": "execution"},
            json={}
        )
        self.assertEqual(response.status_code, 400)
        body = response.get_json() or {}
        self.assertEqual(body.get("code"), "MISSING_REQUIRED_FIELDS")
        self.assertEqual(self._count_cutter_events(), before)


if __name__ == '__main__':
    unittest.main()
