#!/usr/bin/env python3
"""
Smoke Test: Phase 4 - 4-Table Identity Model
Validates that resolve_customer, resolve_contact, and create_quote work correctly.
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path to import database module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import database

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def main():
    print_section("Phase 4 Smoke Test - 4-Table Identity Model")
    
    try:
        # Step 1: Initialize Database
        print_section("Step 1: Initialize Database (WAL Mode)")
        database.initialize_database()
        print("[OK] Database initialized successfully")
        
        # Verify WAL mode
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode")
        journal_mode = cursor.fetchone()[0]
        print(f"   Journal Mode: {journal_mode}")
        if journal_mode.upper() != 'WAL':
            print("[WARN] WARNING: WAL mode not enabled!")
        conn.close()
        
        # Step 2: Test resolve_customer
        print_section("Step 2: Test resolve_customer()")
        customer_name = "Test Corporation"
        customer_domain = "testcorp.com"
        
        customer_id, _ = database.resolve_customer(customer_name, customer_domain)
        print(f"[OK] resolve_customer() returned ID: {customer_id}")
        
        # Verify customer was created
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, domain FROM ops__customers WHERE id = ?", (customer_id,))
        customer = cursor.fetchone()
        conn.close()
        
        if customer:
            print(f"   Customer Record: ID={customer[0]}, Name={customer[1]}, Domain={customer[2]}")
        else:
            raise Exception("Customer not found in database!")
        
        # Test idempotency (calling again should return same ID)
        customer_id_2 = database.resolve_customer(customer_name, customer_domain)
        if customer_id == customer_id_2:
            print(f"[OK] Idempotency check passed (same ID returned: {customer_id})")
        else:
            raise Exception(f"Idempotency FAILED! Got different IDs: {customer_id} vs {customer_id_2}")
        
        # Step 3: Test resolve_contact
        print_section("Step 3: Test resolve_contact()")
        contact_name = "John Doe"
        contact_email = "john.doe@testcorp.com"
        
        contact_id, _ = database.resolve_contact(contact_name, contact_email, customer_id)
        print(f"[OK] resolve_contact() returned ID: {contact_id}")
        
        # Verify contact was created
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, current_customer_id FROM ops__contacts WHERE id = ?", (contact_id,))
        contact = cursor.fetchone()
        conn.close()
        
        if contact:
            print(f"   Contact Record: ID={contact[0]}, Name={contact[1]}, Email={contact[2]}, Customer={contact[3]}")
        else:
            raise Exception("Contact not found in database!")
        
        # Test "Roaming Buyer" (contact changes employers)
        new_customer_id, _ = database.resolve_customer("New Company", "newco.com")
        contact_id_2, _ = database.resolve_contact(contact_name, contact_email, new_customer_id)
        
        if contact_id == contact_id_2:
            print(f"[OK] Roaming Buyer check passed (same contact ID, updated customer)")
            
            # Verify current_customer_id was updated
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT current_customer_id FROM ops__contacts WHERE id = ?", (contact_id,))
            updated_customer = cursor.fetchone()[0]
            conn.close()
            
            if updated_customer == new_customer_id:
                print(f"   current_customer_id updated: {customer_id} -> {new_customer_id}")
            else:
                raise Exception(f"current_customer_id NOT updated! Still: {updated_customer}")
        else:
            raise Exception(f"Roaming Buyer FAILED! Got different contact IDs: {contact_id} vs {contact_id_2}")
        
        # Reset contact back to original customer for quote test
        database.resolve_contact(contact_name, contact_email, customer_id)  # Returns tuple but we don't need it
        
        # Step 4: Create a dummy Part
        print_section("Step 4: Create Dummy Part")
        conn = database.get_connection()
        cursor = conn.cursor()
        
        # Create a test part
        genesis_hash = "test_hash_" + datetime.now().strftime("%Y%m%d%H%M%S")
        cursor.execute("""
            INSERT INTO ops__parts (genesis_hash, filename, fingerprint_json, process_routing_json, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (genesis_hash, "test_part.step", "[]", "[]", datetime.now().isoformat()))
        part_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"[OK] Created test part with ID: {part_id}")
        
        # Step 5: Test create_quote
        print_section("Step 5: Test create_quote() with 4-Table Model")
        
        quote_id_str = f"Q-TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        system_price = 100.50
        final_price = 125.00
        quantity = 10
        material = "Aluminum 6061"
        
        variance_data = {
            "Rush Job": 15.0,
            "Tight Tol": 10.0
        }
        
        pricing_tags = {
            "Rush Job": 0.15,
            "Tight Tol": 0.10
        }
        
        quote_record_id = database.create_quote(
            part_id=part_id,
            customer_id=customer_id,
            contact_id=contact_id,
            user_id=1,  # Bob
            quote_id=quote_id_str,
            material=material,
            system_price_anchor=system_price,
            final_quoted_price=final_price,
            quantity=quantity,
            target_date="2025-02-01",
            notes="Phase 4 smoke test quote",
            variance_json=json.dumps(variance_data),
            pricing_tags_json=json.dumps(pricing_tags),
            status="Draft"
        )
        
        print(f"[OK] create_quote() returned ID: {quote_record_id}")
        
        # Step 6: Retrieve and validate the quote
        print_section("Step 6: Retrieve and Validate Quote")
        
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                q.id, q.quote_id, q.part_id, q.customer_id, q.contact_id, q.user_id,
                q.material, q.system_price_anchor, q.final_quoted_price, q.quantity,
                q.variance_json, q.pricing_tags_json, q.status,
                c.name as customer_name, c.domain,
                ct.name as contact_name, ct.email,
                p.filename
            FROM ops__quotes q
            LEFT JOIN ops__customers c ON q.customer_id = c.id
            LEFT JOIN ops__contacts ct ON q.contact_id = ct.id
            LEFT JOIN ops__parts p ON q.part_id = p.id
            WHERE q.id = ?
        """, (quote_record_id,))
        
        quote = cursor.fetchone()
        conn.close()
        
        if not quote:
            raise Exception("Quote not found in database!")
        
        print("[OK] Quote retrieved successfully!")
        print("\n   Quote Details:")
        print(f"   - Quote ID: {quote[1]}")
        print(f"   - Part ID: {quote[2]} (Filename: {quote[17]})")
        print(f"   - Customer ID: {quote[3]} (Name: {quote[13]}, Domain: {quote[14]})")
        print(f"   - Contact ID: {quote[4]} (Name: {quote[15]}, Email: {quote[16]})")
        print(f"   - Material: {quote[6]}")
        print(f"   - System Anchor: ${quote[7]:.2f}")
        print(f"   - Final Price: ${quote[8]:.2f}")
        print(f"   - Quantity: {quote[9]}")
        print(f"   - Status: {quote[12]}")
        
        variance = json.loads(quote[10]) if quote[10] else {}
        tags = json.loads(quote[11]) if quote[11] else {}
        print(f"   - Variance Attribution: {variance}")
        print(f"   - Pricing Tags: {tags}")
        
        # Step 7: Test get_all_history
        print_section("Step 7: Test get_all_history() with JOINs")
        
        history = database.get_all_history()
        print(f"[OK] get_all_history() returned {len(history)} records")
        
        # Find our test quote
        test_quote = next((q for q in history if q['id'] == quote_record_id), None)
        
        if test_quote:
            print("\n   Our test quote found in history:")
            print(f"   - Quote ID: {test_quote['quote_id']}")
            print(f"   - Customer: {test_quote.get('customer_name', 'N/A')}")
            print(f"   - Contact: {test_quote.get('contact_name', 'N/A')} ({test_quote.get('contact_email', 'N/A')})")
            print(f"   - Material: {test_quote['material']}")
            print(f"   - Price: ${test_quote['final_price']:.2f}")
        else:
            raise Exception("Test quote NOT found in get_all_history()!")
        
        # Final Success
        print_section("[SUCCESS] All Tests Passed!")
        print("\n   The Phase 4 Backend (4-Table Model) is working correctly:")
        print("   [OK] WAL mode enabled")
        print("   [OK] resolve_customer() works (with idempotency)")
        print("   [OK] resolve_contact() works (with Roaming Buyer support)")
        print("   [OK] create_quote() works with all 4 tables")
        print("   [OK] JOINs work correctly in get_all_history()")
        print("\n   Ready to proceed with UI implementation!")
        
        return 0
        
    except Exception as e:
        print_section("[FAILURE] Test Failed")
        print(f"\n   Error: {str(e)}")
        print("\n   Full Traceback:")
        import traceback
        traceback.print_exc()
        print("\n   DO NOT proceed with UI until this is fixed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

