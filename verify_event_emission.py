"""
Verification Script: QUOTE_OVERRIDDEN Event Emission

Demonstrates the complete Control Surface -> Ledger Core flow:
1. Control Surface detects override (final_price != anchor_price)
2. Control Surface emits event to Ledger Core
3. Ledger Core persists event to append-only storage
4. Event query confirms persistence

Constitutional Authority: C7 (Overrides Must Leave Scars)
"""

import database
import json


def verify_event_emission():
    """Simulate the quote save flow with override detection."""
    
    print("\n" + "="*80)
    print("VERIFICATION: QUOTE_OVERRIDDEN Event Emission")
    print("="*80 + "\n")
    
    # Step 1: Create test entities (customer, part)
    print("[STEP 1] Creating test entities...")
    
    customer_id = database.resolve_customer(
        name="Verification Test Customer",
        email_domain="verify.test.com"
    )
    print(f"  Customer ID: {customer_id}")
    
    part_id = database.upsert_part(
        genesis_hash="verify_test_hash_001",
        filename="verify_test.step",
        fingerprint_json="[2.0, 3.0, 4.0, 5.0, 10.0]",
        volume=20.0,
        surface_area=100.0,
        dimensions_json='{"x": 3.0, "y": 4.0, "z": 5.0}',
        process_routing_json='["3-Axis Mill"]'
    )
    print(f"  Part ID: {part_id}")
    
    # Step 2: Create quote with override
    print("\n[STEP 2] Creating quote with price override...")
    
    system_price_anchor = 100.0
    final_quoted_price = 135.0  # +35% override
    
    print(f"  System Anchor: ${system_price_anchor:.2f}")
    print(f"  Final Price:   ${final_quoted_price:.2f}")
    print(f"  Override:      +${final_quoted_price - system_price_anchor:.2f} (+{((final_quoted_price - system_price_anchor) / system_price_anchor) * 100:.1f}%)")
    
    quote_id = database.create_quote(
        part_id=part_id,
        customer_id=customer_id,
        contact_id=None,
        quote_id="VERIFY-001",
        user_id=None,
        material="Aluminum 6061",
        system_price_anchor=system_price_anchor,
        final_quoted_price=final_quoted_price,
        quantity=1,
        status='Draft'
    )
    print(f"  Quote ID: {quote_id}")
    
    # Step 3: Emit QUOTE_OVERRIDDEN event (simulates app.py logic)
    print("\n[STEP 3] Emitting QUOTE_OVERRIDDEN event to Ledger Core...")
    
    override_delta = final_quoted_price - system_price_anchor
    override_percent = (override_delta / system_price_anchor) * 100.0
    
    event_data = {
        'system_price_anchor': system_price_anchor,
        'final_quoted_price': final_quoted_price,
        'override_delta': override_delta,
        'override_percent': override_percent,
        'material': 'Aluminum 6061',
        'quantity': 1
    }
    
    event_id = database.emit_event(
        event_type='QUOTE_OVERRIDDEN',
        quote_id=quote_id,
        event_data=event_data
    )
    print(f"  Event ID: {event_id}")
    print(f"  Event Type: QUOTE_OVERRIDDEN (descriptive, not evaluative)")
    
    # Step 4: Query events to verify persistence
    print("\n[STEP 4] Querying events for this quote...")
    
    events = database.get_events_for_quote(quote_id=quote_id)
    
    print(f"  Found {len(events)} event(s)")
    
    for event in events:
        print(f"\n  Event ID: {event['id']}")
        print(f"  Type: {event['event_type']}")
        print(f"  Created: {event['created_at']}")
        print(f"  Data: {json.dumps(event['event_data'], indent=4)}")
    
    # Step 5: Verify constitutional constraints
    print("\n[STEP 5] Verifying constitutional constraints...")
    
    # Check append-only constraint
    import sqlite3
    conn = sqlite3.connect('cutter.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE cutter__operational_events SET event_type = 'MODIFIED' WHERE id = ?", (event_id,))
        conn.commit()
        print("  [FAIL] UPDATE should have been blocked")
        conn.close()
        return False
    except sqlite3.IntegrityError as e:
        print(f"  [PASS] C4 (Irreversible Memory): UPDATE blocked")
        conn.close()
    
    conn = sqlite3.connect('cutter.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM cutter__operational_events WHERE id = ?", (event_id,))
        conn.commit()
        print("  [FAIL] DELETE should have been blocked")
        conn.close()
        return False
    except sqlite3.IntegrityError as e:
        print(f"  [PASS] C7 (Overrides Must Leave Scars): DELETE blocked")
        conn.close()
    
    print("\n" + "="*80)
    print("VERIFICATION: Event emission functioning as specified")
    print("="*80 + "\n")
    
    return True


if __name__ == '__main__':
    success = verify_event_emission()
    exit(0 if success else 1)
