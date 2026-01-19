#!/usr/bin/env python3
"""
Test Wizard Backend Implementation
Tests payment terms, outcome events table, progressive auto-save, and NO_RESPONSE behavior.
"""

import sys
import os
import sqlite3
import tempfile
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if not os.environ.get("TEST_DB_PATH"):
    bootstrap_path = os.path.join(tempfile.gettempdir(), "test_wizard_backend_bootstrap.db")
    os.environ["TEST_DB_PATH"] = bootstrap_path

import database


def print_test(name: str, passed: bool, details: str = ""):
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} {name}")
    if details:
        print(f"      {details}")
    if not passed:
        print()


def inspect_table_schema(table_name: str):
    """Print table schema for debugging."""
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    schema = cursor.fetchall()
    conn.close()
    
    print(f"\n--- {table_name} Schema ---")
    for col in schema:
        print(f"  {col[1]:30s} {col[2]:15s} {'NOT NULL' if col[3] else 'NULL':10s} Default: {col[4]}")
    print()


def test_payment_terms_column():
    """Test that payment_terms_days column exists in quotes table."""
    print("\n=== TEST 1: Payment Terms Column ===")
    
    conn = database.get_connection()
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(quotes)")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()
    
    has_payment_terms = 'payment_terms_days' in columns
    print_test("payment_terms_days column exists", has_payment_terms)
    
    if has_payment_terms:
        print("      Column added successfully!")
    
    return has_payment_terms


def test_outcome_events_schema():
    """Test that quote_outcome_events has wizard columns."""
    print("\n=== TEST 2: Outcome Events Schema ===")
    
    conn = database.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(quote_outcome_events)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    conn.close()
    
    required_columns = [
        'original_price',
        'final_price',
        'price_changed',
        'original_leadtime_days',
        'final_leadtime_days',
        'leadtime_changed',
        'original_terms_days',
        'final_terms_days',
        'terms_changed',
        'other_notes',
        'wizard_completed',
        'wizard_step_reached'
    ]
    
    all_present = True
    for col in required_columns:
        exists = col in columns
        print_test(f"  Column: {col}", exists)
        if not exists:
            all_present = False
    
    return all_present


def test_progressive_auto_save():
    """Test progressive wizard auto-save (updates same event)."""
    print("\n=== TEST 3: Progressive Auto-Save ===")
    
    # Create test data
    customer_id, _ = database.resolve_customer("Test Wizard Corp", "testwizard.com")
    contact_id, _ = database.resolve_contact("Wizard Tester", "wizard@testwizard.com", customer_id)
    
    # Create part using upsert_part
    part_id = database.upsert_part(
        genesis_hash="WIZARD-TEST-HASH-001",
        filename="test_wizard.step",
        fingerprint_json='{}',
        volume=10.0,
        surface_area=50.0,
        dimensions_json='{"x": 2, "y": 2, "z": 2.5}',
        process_routing_json='[]'
    )
    
    quote_id = database.create_quote(
        part_id=part_id,
        customer_id=customer_id,
        contact_id=contact_id,
        quote_id="WIZ-TEST-001",
        user_id=1,
        material="6061-T6 Aluminum",
        system_price_anchor=150.00,
        final_quoted_price=150.00,
        quantity=10,
        lead_time_days=14,
        payment_terms_days=30,
        status='Sent'
    )
    
    print(f"      Created test quote ID: {quote_id}")
    
    # Step 1: Save initial outcome (WON)
    event_id_1 = database.save_quote_outcome_wizard(
        quote_id=quote_id,
        outcome_type='WON',
        actor_user_id=1,
        original_price=150.00,
        wizard_step=0
    )
    
    print_test("Initial save (Step 0)", event_id_1 > 0, f"Event ID: {event_id_1}")
    
    # Step 2: Update with price (Step 1)
    event_id_2 = database.save_quote_outcome_wizard(
        quote_id=quote_id,
        outcome_type='WON',
        actor_user_id=1,
        original_price=150.00,
        final_price=140.00,
        wizard_step=1
    )
    
    print_test("Update with price (Step 1)", event_id_2 == event_id_1, 
                f"Same event updated (ID: {event_id_2})")
    
    # Step 3: Update with leadtime (Step 2)
    event_id_3 = database.save_quote_outcome_wizard(
        quote_id=quote_id,
        outcome_type='WON',
        actor_user_id=1,
        original_price=150.00,
        final_price=140.00,
        original_leadtime=14,
        final_leadtime=10,
        wizard_step=2
    )
    
    print_test("Update with leadtime (Step 2)", event_id_3 == event_id_1,
                f"Same event updated (ID: {event_id_3})")
    
    # Step 4: Update with terms (Step 3)
    event_id_4 = database.save_quote_outcome_wizard(
        quote_id=quote_id,
        outcome_type='WON',
        actor_user_id=1,
        original_price=150.00,
        final_price=140.00,
        original_leadtime=14,
        final_leadtime=10,
        original_terms=30,
        final_terms=30,
        wizard_step=3
    )
    
    print_test("Update with terms (Step 3)", event_id_4 == event_id_1,
                f"Same event updated (ID: {event_id_4})")
    
    # Step 5: Complete with other notes (Step 4)
    event_id_5 = database.save_quote_outcome_wizard(
        quote_id=quote_id,
        outcome_type='WON',
        actor_user_id=1,
        original_price=150.00,
        final_price=140.00,
        original_leadtime=14,
        final_leadtime=10,
        original_terms=30,
        final_terms=30,
        other_notes="Customer negotiated price, needed faster delivery",
        wizard_step=4
    )
    
    print_test("Complete wizard (Step 4)", event_id_5 == event_id_1,
                f"Same event updated (ID: {event_id_5})")
    
    # Verify final state
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            outcome_type, original_price, final_price, price_changed,
            original_leadtime_days, final_leadtime_days, leadtime_changed,
            original_terms_days, final_terms_days, terms_changed,
            other_notes, wizard_step_reached, wizard_completed
        FROM ops__quote_outcome_events
        WHERE id = ?
    """, (event_id_1,))
    
    event = cursor.fetchone()
    conn.close()
    
    if event:
        print("\n      Final Event State:")
        print(f"        Outcome: {event['outcome_type']}")
        print(f"        Price: ${event['original_price']} -> ${event['final_price']} (Changed: {event['price_changed']})")
        print(f"        Lead Time: {event['original_leadtime_days']} -> {event['final_leadtime_days']} days (Changed: {event['leadtime_changed']})")
        print(f"        Terms: Net {event['original_terms_days']} -> Net {event['final_terms_days']} (Changed: {event['terms_changed']})")
        print(f"        Notes: {event['other_notes']}")
        print(f"        Wizard Step: {event['wizard_step_reached']} | Completed: {event['wizard_completed']}")
        
        # Verify change detection
        price_changed_correct = event['price_changed'] == 1  # 140 != 150
        leadtime_changed_correct = event['leadtime_changed'] == 1  # 10 != 14
        terms_changed_correct = event['terms_changed'] == 0  # 30 == 30
        wizard_completed = event['wizard_completed'] == 1
        
        print_test("Change Detection - Price", price_changed_correct, "Correctly detected price change")
        print_test("Change Detection - Lead Time", leadtime_changed_correct, "Correctly detected leadtime change")
        print_test("Change Detection - Terms", terms_changed_correct, "Correctly detected no terms change")
        print_test("Wizard Completed Flag", wizard_completed, "Wizard marked as completed")
        
        return all([price_changed_correct, leadtime_changed_correct, terms_changed_correct, wizard_completed])
    else:
        print_test("Verify final event state", False, "Event not found in database")
        return False


def test_no_response_behavior():
    """Test that NO_RESPONSE stays on exception list."""
    print("\n=== TEST 4: NO_RESPONSE Behavior ===")
    
    # Create test quote
    customer_id = database.resolve_customer("No Response Corp", "noresponse.com")
    contact_id = database.resolve_contact("Silent Customer", "silent@noresponse.com", customer_id)
    
    part_id = database.upsert_part(
        genesis_hash="NORESPONSE-TEST-HASH-001",
        filename="test_noresponse.step",
        fingerprint_json='{}',
        volume=15.0,
        surface_area=60.0,
        dimensions_json='{"x": 3, "y": 2, "z": 2.5}',
        process_routing_json='[]'
    )
    
    quote_id = database.create_quote(
        part_id=part_id,
        customer_id=customer_id,
        contact_id=contact_id,
        quote_id="NORESP-TEST-001",
        user_id=1,
        material="6061-T6 Aluminum",
        system_price_anchor=200.00,
        final_quoted_price=200.00,
        quantity=5,
        lead_time_days=21,
        payment_terms_days=30,
        status='Sent'
    )
    
    print(f"      Created test quote ID: {quote_id}")
    
    # Check unclosed list before NO_RESPONSE
    unclosed_before = database.get_unclosed_quotes()
    unclosed_ids_before = [q['id'] for q in unclosed_before]
    is_unclosed_before = quote_id in unclosed_ids_before
    
    print_test("Quote is unclosed before outcome", is_unclosed_before)
    
    # Save NO_RESPONSE outcome
    event_id = database.save_quote_outcome_wizard(
        quote_id=quote_id,
        outcome_type='NO_RESPONSE',
        actor_user_id=1,
        wizard_step=0
    )
    
    print_test("NO_RESPONSE saved", event_id > 0, f"Event ID: {event_id}")
    
    # Check unclosed list after NO_RESPONSE
    unclosed_after = database.get_unclosed_quotes()
    unclosed_ids_after = [q['id'] for q in unclosed_after]
    is_still_unclosed = quote_id in unclosed_ids_after
    
    print_test("Quote STILL on exception list after NO_RESPONSE", is_still_unclosed,
                "NO_RESPONSE doesn't remove from exception list (can be revisited)")
    
    return is_still_unclosed


def test_won_lost_removes_from_list():
    """Test that WON/LOST removes quotes from exception list."""
    print("\n=== TEST 5: WON/LOST Removes From List ===")
    
    # Create test quote
    customer_id = database.resolve_customer("Win Corp", "win.com")
    contact_id = database.resolve_contact("Winner", "winner@win.com", customer_id)
    
    part_id = database.upsert_part(
        genesis_hash="WIN-TEST-HASH-001",
        filename="test_win.step",
        fingerprint_json='{}',
        volume=8.0,
        surface_area=40.0,
        dimensions_json='{"x": 2, "y": 2, "z": 2}',
        process_routing_json='[]'
    )
    
    quote_id = database.create_quote(
        part_id=part_id,
        customer_id=customer_id,
        contact_id=contact_id,
        quote_id="WIN-TEST-001",
        user_id=1,
        material="6061-T6 Aluminum",
        system_price_anchor=100.00,
        final_quoted_price=100.00,
        quantity=20,
        lead_time_days=7,
        payment_terms_days=30,
        status='Sent'
    )
    
    print(f"      Created test quote ID: {quote_id}")
    
    # Check unclosed before
    unclosed_before = database.get_unclosed_quotes()
    is_unclosed_before = quote_id in [q['id'] for q in unclosed_before]
    print_test("Quote is unclosed before WON", is_unclosed_before)
    
    # Save WON outcome
    event_id = database.save_quote_outcome_wizard(
        quote_id=quote_id,
        outcome_type='WON',
        actor_user_id=1,
        original_price=100.00,
        final_price=100.00,
        wizard_step=0
    )
    
    print_test("WON saved", event_id > 0, f"Event ID: {event_id}")
    
    # Check unclosed after
    unclosed_after = database.get_unclosed_quotes()
    is_closed_after = quote_id not in [q['id'] for q in unclosed_after]
    print_test("Quote REMOVED from exception list after WON", is_closed_after,
                "WON removes quote from exception list")
    
    # Verify quote status updated
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, closed_at FROM ops__quotes WHERE id = ?", (quote_id,))
    row = cursor.fetchone()
    conn.close()
    
    status_correct = row['status'] == 'Won'
    has_closed_at = row['closed_at'] is not None
    
    print_test("Quote status updated to 'Won'", status_correct, f"Status: {row['status']}")
    print_test("closed_at timestamp set", has_closed_at, f"Closed at: {row['closed_at']}")
    
    return is_closed_after and status_correct and has_closed_at


def test_back_button_overwrites():
    """Test that going back and changing values overwrites (not creates new event)."""
    print("\n=== TEST 6: Back Button Overwrites ===")
    
    # Create test quote
    customer_id = database.resolve_customer("Back Button Corp", "backbutton.com")
    contact_id = database.resolve_contact("Changer", "changer@backbutton.com", customer_id)
    
    part_id = database.upsert_part(
        genesis_hash="BACK-TEST-HASH-001",
        filename="test_back.step",
        fingerprint_json='{}',
        volume=12.0,
        surface_area=55.0,
        dimensions_json='{"x": 2.5, "y": 2.5, "z": 2}',
        process_routing_json='[]'
    )
    
    quote_id = database.create_quote(
        part_id=part_id,
        customer_id=customer_id,
        contact_id=contact_id,
        quote_id="BACK-TEST-001",
        user_id=1,
        material="6061-T6 Aluminum",
        system_price_anchor=175.00,
        final_quoted_price=175.00,
        quantity=15,
        lead_time_days=10,
        payment_terms_days=30,
        status='Sent'
    )
    
    print(f"      Created test quote ID: {quote_id}")
    
    # Step 1: Save outcome
    event_id = database.save_quote_outcome_wizard(
        quote_id=quote_id,
        outcome_type='LOST',
        actor_user_id=1,
        original_price=175.00,
        wizard_step=0
    )
    
    # Step 2: Update price to $160
    database.save_quote_outcome_wizard(
        quote_id=quote_id,
        outcome_type='LOST',
        original_price=175.00,
        final_price=160.00,
        wizard_step=1
    )
    
    print(f"      Step 1: Set price to $160")
    
    # Step 3: Go BACK and change price to $155 (simulating back button)
    database.save_quote_outcome_wizard(
        quote_id=quote_id,
        outcome_type='LOST',
        original_price=175.00,
        final_price=155.00,  # Changed from $160 to $155
        wizard_step=1
    )
    
    print(f"      Step 2: User hit BACK, changed price to $155")
    
    # Verify only ONE event exists with LATEST value ($155)
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) as count, final_price
        FROM ops__quote_outcome_events
        WHERE quote_id = ?
    """, (quote_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    only_one_event = row['count'] == 1
    final_price_correct = row['final_price'] == 155.00
    
    print_test("Only ONE event exists", only_one_event, f"Event count: {row['count']}")
    print_test("Final price is LATEST value ($155)", final_price_correct, 
                f"Final price: ${row['final_price']} (overwrote $160)")
    
    return only_one_event and final_price_correct


def main():
    """Run all wizard backend tests."""
    print("=" * 60)
    print("WIZARD BACKEND TEST SUITE")
    print("=" * 60)
    
    # Initialize database
    print("\nInitializing database...")
    database.initialize_database()
    print("Database initialized.")
    
    # Clean up test data from previous runs
    print("Cleaning up test data from previous runs...")
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ops__quotes WHERE quote_id LIKE 'WIZ-%' OR quote_id LIKE 'NORESP-%' OR quote_id LIKE 'WIN-%' OR quote_id LIKE 'BACK-%'")
    cursor.execute("DELETE FROM ops__parts WHERE genesis_hash LIKE '%-TEST-HASH-%'")
    cursor.execute("DELETE FROM ops__customers WHERE domain LIKE '%testwizard.com%' OR domain LIKE '%noresponse.com%' OR domain LIKE '%win.com%' OR domain LIKE '%backbutton.com%'")
    conn.commit()
    conn.close()
    print("Test data cleaned.")
    
    # Optional: Show schema
    # inspect_table_schema('quotes')
    # inspect_table_schema('quote_outcome_events')
    
    # Run tests
    results = []
    
    results.append(("Payment Terms Column", test_payment_terms_column()))
    results.append(("Outcome Events Schema", test_outcome_events_schema()))
    results.append(("Progressive Auto-Save", test_progressive_auto_save()))
    results.append(("NO_RESPONSE Behavior", test_no_response_behavior()))
    results.append(("WON/LOST Removes From List", test_won_lost_removes_from_list()))
    results.append(("Back Button Overwrites", test_back_button_overwrites()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\nALL TESTS PASSED - Backend is ready for frontend integration!")
        return 0
    else:
        print("\nSOME TESTS FAILED - Review errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())

