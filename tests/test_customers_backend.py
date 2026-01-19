"""
Test Suite for Customers Feature Backend (Phase 5.6)
Tests: Migration 07, Database Functions, API Endpoints

Run: python test_customers_backend.py
"""
import sqlite3
import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:5000"
TEST_CUSTOMER_ID = None
TEST_CONTACT_ID = None
TEST_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_test(text, status=""):
    if status == "PASS":
        print(f"  [PASS] {text}")
    elif status == "FAIL":
        print(f"  [FAIL] {text}")
    else:
        print(f"  {text}")

# ============================================================================
# TEST 1: Database Migration (Tables & Data)
# ============================================================================

def test_migration():
    print_header("TEST 1: Database Migration (Tables & Relationships)")
    
    try:
        conn = sqlite3.connect('cutter.db')
        cursor = conn.cursor()
        
        # Test 1.1: customer_parts table exists
        print_test("Checking customer_parts table...", "")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customer_parts'")
        if cursor.fetchone():
            print_test("customer_parts table exists", "PASS")
            
            # Check data
            cursor.execute("SELECT COUNT(*) FROM customer_parts")
            count = cursor.fetchone()[0]
            print_test(f"  Found {count} customer-part relationships", "PASS" if count > 0 else "FAIL")
        else:
            print_test("customer_parts table NOT found", "FAIL")
            return False
        
        # Test 1.2: contact_companies table exists
        print_test("Checking contact_companies table...", "")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contact_companies'")
        if cursor.fetchone():
            print_test("contact_companies table exists", "PASS")
            
            # Check data
            cursor.execute("SELECT COUNT(*) FROM contact_companies")
            count = cursor.fetchone()[0]
            print_test(f"  Found {count} contact-company relationships", "PASS" if count > 0 else "FAIL")
        else:
            print_test("contact_companies table NOT found", "FAIL")
            return False
        
        # Test 1.3: Indices exist
        print_test("Checking indices...", "")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_customer%'")
        indices = cursor.fetchall()
        print_test(f"  Found {len(indices)} customer indices", "PASS" if len(indices) >= 4 else "FAIL")
        
        conn.close()
        return True
        
    except Exception as e:
        print_test(f"Migration test failed: {e}", "FAIL")
        return False


# ============================================================================
# TEST 2: Database Functions
# ============================================================================

def test_database_functions():
    print_header("TEST 2: Database Functions (CRUD Operations)")
    
    try:
        import database
        
        # Test 2.1: get_all_customers()
        print_test("Testing get_all_customers()...", "")
        customers = database.get_all_customers()
        print_test(f"  Retrieved {len(customers)} customers", "PASS")
        
        if customers:
            sample = customers[0]
            required_keys = ['id', 'company_name', 'parts_count', 'contacts_count', 'quotes_count']
            missing = [k for k in required_keys if k not in sample]
            if missing:
                print_test(f"  Missing keys: {missing}", "FAIL")
            else:
                print_test(f"  All required keys present", "PASS")
        
        # Test 2.2: create_customer()
        print_test("Testing create_customer()...", "")
        global TEST_CUSTOMER_ID
        TEST_CUSTOMER_ID = database.create_customer(f"Test Corp Backend {TEST_TIMESTAMP}", "testcorp.com")
        print_test(f"  Created customer ID: {TEST_CUSTOMER_ID}", "PASS")
        
        # Test 2.3: get_customer_details()
        print_test("Testing get_customer_details()...", "")
        details = database.get_customer_details(TEST_CUSTOMER_ID)
        if details and details['company_name'] == "Test Corp Backend":
            print_test(f"  Retrieved customer details", "PASS")
            print_test(f"    Parts: {len(details['parts'])}, Contacts: {len(details['contacts'])}", "")
        else:
            print_test(f"  Failed to retrieve details", "FAIL")
        
        # Test 2.4: update_customer()
        print_test("Testing update_customer()...", "")
        success = database.update_customer(TEST_CUSTOMER_ID, company_name="Test Corp Updated")
        if success:
            details = database.get_customer_details(TEST_CUSTOMER_ID)
            if details['company_name'] == "Test Corp Updated":
                print_test(f"  Customer updated successfully", "PASS")
            else:
                print_test(f"  Update didn't persist", "FAIL")
        else:
            print_test(f"  Update failed", "FAIL")
        
        # Test 2.5: create_contact_for_customer()
        print_test("Testing create_contact_for_customer()...", "")
        global TEST_CONTACT_ID
        TEST_CONTACT_ID = database.create_contact_for_customer(
            TEST_CUSTOMER_ID, 
            "Test Contact", 
            "test@testcorp.com", 
            "555-1234"
        )
        print_test(f"  Created contact ID: {TEST_CONTACT_ID}", "PASS")
        
        # Test 2.6: update_contact()
        print_test("Testing update_contact()...", "")
        success = database.update_contact(TEST_CONTACT_ID, contact_name="Test Contact Updated")
        print_test(f"  Contact update: {'success' if success else 'failed'}", "PASS" if success else "FAIL")
        
        # Test 2.7: delete_contact() (soft delete)
        print_test("Testing delete_contact() (soft delete)...", "")
        success = database.delete_contact(TEST_CONTACT_ID)
        print_test(f"  Contact soft delete: {'success' if success else 'failed'}", "PASS" if success else "FAIL")
        
        # Test 2.8: delete_customer() (soft delete)
        print_test("Testing delete_customer() (soft delete)...", "")
        success = database.delete_customer(TEST_CUSTOMER_ID)
        print_test(f"  Customer soft delete: {'success' if success else 'failed'}", "PASS" if success else "FAIL")
        
        return True
        
    except Exception as e:
        print_test(f"Database functions test failed: {e}", "FAIL")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# TEST 3: API Endpoints
# ============================================================================

def test_api_endpoints():
    print_header("TEST 3: API Endpoints (10 Routes)")
    
    print_test("NOTE: Server must be running at http://localhost:5000", "")
    print_test("Run in another terminal: python app.py", "")
    print()
    
    try:
        # Test 3.1: GET /api/customers
        print_test("Testing GET /api/customers...", "")
        response = requests.get(f"{BASE_URL}/api/customers")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_test(f"  Retrieved {len(data.get('customers', []))} customers", "PASS")
            else:
                print_test(f"  API returned success=false", "FAIL")
        else:
            print_test(f"  Status code: {response.status_code}", "FAIL")
        
        # Test 3.2: POST /api/customer (create)
        print_test("Testing POST /api/customer (create)...", "")
        payload = {
            "company_name": f"API Test Corp {TEST_TIMESTAMP}",
            "domain": "apitest.com"
        }
        response = requests.post(f"{BASE_URL}/api/customer", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                global TEST_CUSTOMER_ID
                TEST_CUSTOMER_ID = data.get('customer_id')
                print_test(f"  Created customer ID: {TEST_CUSTOMER_ID}", "PASS")
            else:
                print_test(f"  API returned success=false", "FAIL")
        else:
            print_test(f"  Status code: {response.status_code}", "FAIL")
            return False
        
        # Test 3.3: GET /api/customer/<id> (details)
        print_test("Testing GET /api/customer/<id>...", "")
        response = requests.get(f"{BASE_URL}/api/customer/{TEST_CUSTOMER_ID}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                customer = data.get('customer')
                print_test(f"  Retrieved: {customer.get('company_name')}", "PASS")
            else:
                print_test(f"  API returned success=false", "FAIL")
        else:
            print_test(f"  Status code: {response.status_code}", "FAIL")
        
        # Test 3.4: PUT /api/customer/<id> (update)
        print_test("Testing PUT /api/customer/<id>...", "")
        payload = {"company_name": "API Test Corp Updated"}
        response = requests.put(f"{BASE_URL}/api/customer/{TEST_CUSTOMER_ID}", json=payload)
        if response.status_code == 200:
            data = response.json()
            print_test(f"  Update: {'success' if data.get('success') else 'failed'}", "PASS" if data.get('success') else "FAIL")
        else:
            print_test(f"  Status code: {response.status_code}", "FAIL")
        
        # Test 3.5: POST /api/customer/<id>/contact (create contact)
        print_test("Testing POST /api/customer/<id>/contact...", "")
        payload = {
            "contact_name": "API Test Contact",
            "email": "contact@apitest.com",
            "phone": "555-9999"
        }
        response = requests.post(f"{BASE_URL}/api/customer/{TEST_CUSTOMER_ID}/contact", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                global TEST_CONTACT_ID
                TEST_CONTACT_ID = data.get('contact_id')
                print_test(f"  Created contact ID: {TEST_CONTACT_ID}", "PASS")
            else:
                print_test(f"  API returned success=false", "FAIL")
        else:
            print_test(f"  Status code: {response.status_code}", "FAIL")
            return False
        
        # Test 3.6: PUT /api/contact/<id> (update contact)
        print_test("Testing PUT /api/contact/<id>...", "")
        payload = {"contact_name": "API Test Contact Updated"}
        response = requests.put(f"{BASE_URL}/api/contact/{TEST_CONTACT_ID}", json=payload)
        if response.status_code == 200:
            data = response.json()
            print_test(f"  Update: {'success' if data.get('success') else 'failed'}", "PASS" if data.get('success') else "FAIL")
        else:
            print_test(f"  Status code: {response.status_code}", "FAIL")
        
        # Test 3.7: DELETE /api/contact/<id> (soft delete)
        print_test("Testing DELETE /api/contact/<id>...", "")
        response = requests.delete(f"{BASE_URL}/api/contact/{TEST_CONTACT_ID}")
        if response.status_code == 200:
            data = response.json()
            print_test(f"  Delete: {'success' if data.get('success') else 'failed'}", "PASS" if data.get('success') else "FAIL")
        else:
            print_test(f"  Status code: {response.status_code}", "FAIL")
        
        # Test 3.8: DELETE /api/customer/<id> (soft delete)
        print_test("Testing DELETE /api/customer/<id>...", "")
        response = requests.delete(f"{BASE_URL}/api/customer/{TEST_CUSTOMER_ID}")
        if response.status_code == 200:
            data = response.json()
            print_test(f"  Delete: {'success' if data.get('success') else 'failed'}", "PASS" if data.get('success') else "FAIL")
        else:
            print_test(f"  Status code: {response.status_code}", "FAIL")
        
        # Test 3.9: Error handling (404)
        print_test("Testing error handling (404)...", "")
        response = requests.get(f"{BASE_URL}/api/customer/999999")
        if response.status_code == 404:
            print_test(f"  Correctly returned 404", "PASS")
        else:
            print_test(f"  Expected 404, got {response.status_code}", "FAIL")
        
        # Test 3.10: Validation (missing required field)
        print_test("Testing validation (missing required field)...", "")
        payload = {"domain": "test.com"}  # Missing company_name
        response = requests.post(f"{BASE_URL}/api/customer", json=payload)
        if response.status_code == 400:
            print_test(f"  Correctly returned 400 for missing field", "PASS")
        else:
            print_test(f"  Expected 400, got {response.status_code}", "FAIL")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print_test("CANNOT CONNECT TO SERVER", "FAIL")
        print_test("Start server: python app.py", "")
        return False
    except Exception as e:
        print_test(f"API endpoints test failed: {e}", "FAIL")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# RUN ALL TESTS
# ============================================================================

def main():
    print("\n" + "#" * 70)
    print("  CUSTOMERS FEATURE BACKEND TEST SUITE")
    print("  Phase 5.6 - Migration + Database + API")
    print("#" * 70)
    
    results = {
        'migration': False,
        'database': False,
        'api': False
    }
    
    # Test 1: Migration
    results['migration'] = test_migration()
    
    # Test 2: Database Functions
    results['database'] = test_database_functions()
    
    # Test 3: API Endpoints (requires server running)
    print()
    print("[INFO] API tests require Flask server running at http://localhost:5000")
    print("[INFO] Waiting 3 seconds for server to be ready...")
    import time
    time.sleep(3)
    results['api'] = test_api_endpoints()
    
    # Summary
    print_header("TEST SUMMARY")
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print_test(f"{test_name.upper()}: {status}", status)
    
    print()
    print(f"  Total: {passed}/{total} test suites passed")
    
    if passed == total:
        print()
        print("  [SUCCESS] All backend tests passed!")
        print("  [NEXT] Ready to add frontend (CSS + JavaScript)")
        return 0
    else:
        print()
        print("  [FAIL] Some tests failed. Fix issues before continuing.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
