"""
Test Script: Soft Delete Functionality
Verifies that deleted quotes are excluded from history and vector search.
"""
import database
import vector_engine
import json

def test_soft_delete():
    print("=" * 60)
    print("SOFT DELETE FEATURE TEST")
    print("=" * 60)
    
    # 1. Get initial history count
    print("\n[1] Initial State")
    initial_history = database.get_all_history()
    initial_count = len(initial_history)
    print(f"   Active quotes in history: {initial_count}")
    
    if initial_count == 0:
        print("   WARNING: No quotes in history. Create a test quote first.")
        return
    
    # 2. Select a quote to delete (use the most recent one)
    test_quote = initial_history[0]
    test_id = test_quote['id']
    test_quote_id = test_quote.get('quote_id', f"#{test_id}")
    test_filename = test_quote['filename']
    
    print(f"\n[2] Test Target")
    print(f"   Quote ID: {test_quote_id}")
    print(f"   DB ID: {test_id}")
    print(f"   Filename: {test_filename}")
    
    # 3. Verify quote is in vector search results (if it has a fingerprint)
    fingerprint_str = test_quote.get('fingerprint')
    if fingerprint_str:
        print(f"\n[3] Vector Search (Before Delete)")
        try:
            fingerprint = json.loads(fingerprint_str)
            similar = vector_engine.find_similar_parts(fingerprint)
            
            # Check if test quote is in results
            found_in_search = any(m['id'] == test_id for m in similar)
            print(f"   Test quote found in search: {found_in_search}")
            print(f"   Similar parts count: {len(similar)}")
        except Exception as e:
            print(f"   WARNING: Vector search error: {e}")
    else:
        print(f"\n[3] Vector Search: Skipped (no fingerprint)")
    
    # 4. Perform soft delete
    print(f"\n[4] Performing Soft Delete...")
    success = database.soft_delete_quote(test_id)
    
    if not success:
        print(f"   FAIL: Soft delete failed!")
        return
    else:
        print(f"   SUCCESS: Soft delete successful")
    
    # 5. Verify quote is NOT in history
    print(f"\n[5] History Check (After Delete)")
    new_history = database.get_all_history()
    new_count = len(new_history)
    quote_in_history = any(q['id'] == test_id for q in new_history)
    
    print(f"   Active quotes in history: {new_count}")
    print(f"   Expected count: {initial_count - 1}")
    print(f"   Test quote in history: {quote_in_history}")
    
    if quote_in_history:
        print(f"   FAIL: Quote still visible in history!")
    else:
        print(f"   PASS: Quote hidden from history")
    
    # 6. Verify quote is NOT in vector search
    if fingerprint_str:
        print(f"\n[6] Vector Search (After Delete)")
        try:
            similar_after = vector_engine.find_similar_parts(fingerprint)
            found_after_delete = any(m['id'] == test_id for m in similar_after)
            
            print(f"   Test quote found in search: {found_after_delete}")
            print(f"   Similar parts count: {len(similar_after)}")
            
            if found_after_delete:
                print(f"   FAIL: Deleted quote still in vector search!")
            else:
                print(f"   PASS: Deleted quote excluded from search")
        except Exception as e:
            print(f"   WARNING: Vector search error: {e}")
    
    # 7. Verify quote still exists in DB (forensic recovery)
    print(f"\n[7] Forensic Recovery Check")
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, is_deleted FROM ops__quote_history WHERE id = ?", (test_id,))
    db_row = cursor.fetchone()
    conn.close()
    
    if db_row:
        is_deleted = db_row[1]
        print(f"   Quote exists in DB: True")
        print(f"   is_deleted flag: {is_deleted}")
        
        if is_deleted == 1:
            print(f"   PASS: Data preserved with is_deleted = 1")
        else:
            print(f"   FAIL: is_deleted flag not set correctly!")
    else:
        print(f"   FAIL: Quote completely removed from DB (hard delete)!")
    
    # 8. Summary
    print(f"\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = (
        not quote_in_history and 
        (not fingerprint_str or not found_after_delete) and
        db_row and db_row[1] == 1
    )
    
    if all_passed:
        print(">>> ALL TESTS PASSED <<<")
        print("\nSoft Delete feature working correctly:")
        print("  [OK] Quote hidden from history")
        print("  [OK] Quote excluded from vector search")
        print("  [OK] Data preserved for recovery")
    else:
        print(">>> SOME TESTS FAILED <<<")
        print("\nReview output above for details.")
    
    print("\n" + "=" * 60)
    
    # Optional: Restore the quote for future testing
    print("\n[RESTORE] Restore Test Quote? (for future testing)")
    restore = input("   Type 'yes' to restore: ").strip().lower()
    
    if restore == 'yes':
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE ops__quote_history SET is_deleted = 0 WHERE id = ?", (test_id,))
        conn.commit()
        conn.close()
        print(f"   SUCCESS: Quote {test_quote_id} restored (is_deleted = 0)")
    else:
        print(f"   Quote {test_quote_id} remains archived")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_soft_delete()

