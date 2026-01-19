"""
Frontend Integration Test - Customers Feature (Phase 5.6)
Tests that the frontend loads correctly with new customers module

Run: python test_frontend_integration.py
"""
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://localhost:5000"

def print_test(text, status=""):
    if status == "PASS":
        print(f"  [PASS] {text}")
    elif status == "FAIL":
        print(f"  [FAIL] {text}")
    else:
        print(f"  {text}")

def test_frontend_loads():
    """Test that the main page loads without errors"""
    print("\n=== TEST 1: Frontend Loads ===")
    
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print_test("Main page loads successfully", "PASS")
            return response.text
        else:
            print_test(f"Main page returned status {response.status_code}", "FAIL")
            return None
    except Exception as e:
        print_test(f"Error loading main page: {e}", "FAIL")
        return None

def test_html_elements(html):
    """Test that required HTML elements are present"""
    print("\n=== TEST 2: HTML Elements ===")
    
    if not html:
        print_test("No HTML to test", "FAIL")
        return False
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Test for customers view
    customers_view = soup.find(id='customers-view')
    if customers_view:
        print_test("customers-view element exists", "PASS")
    else:
        print_test("customers-view element NOT found", "FAIL")
        return False
    
    # Test for customer table
    customer_table = soup.find(id='customer-table-body')
    if customer_table:
        print_test("customer-table-body element exists", "PASS")
    else:
        print_test("customer-table-body element NOT found", "FAIL")
        return False
    
    # Test for modals
    customer_modal = soup.find(id='customer-modal')
    contact_modal = soup.find(id='contact-modal')
    
    if customer_modal:
        print_test("customer-modal element exists", "PASS")
    else:
        print_test("customer-modal element NOT found", "FAIL")
        return False
    
    if contact_modal:
        print_test("contact-modal element exists", "PASS")
    else:
        print_test("contact-modal element NOT found", "FAIL")
        return False
    
    # Test for customers navigation link
    nav_items = soup.find_all(['div', 'a'], {'class': 'nav-item'})
    customers_nav_found = False
    for item in nav_items:
        if item.get('data-view') == 'customers':
            customers_nav_found = True
            break
    
    if customers_nav_found:
        print_test("Customers navigation item exists", "PASS")
    else:
        print_test("Customers navigation item NOT found", "FAIL")
        return False
    
    return True

def test_javascript_modules(html):
    """Test that JavaScript modules are correctly imported"""
    print("\n=== TEST 3: JavaScript Modules ===")
    
    if not html:
        print_test("No HTML to test", "FAIL")
        return False
    
    soup = BeautifulSoup(html, 'html.parser')
    scripts = soup.find_all('script')
    
    # Look for main.js import
    main_js_found = False
    for script in scripts:
        src = script.get('src', '')
        if 'main.js' in src and script.get('type') == 'module':
            main_js_found = True
            break
    
    if main_js_found:
        print_test("main.js module import found", "PASS")
    else:
        print_test("main.js module import NOT found", "FAIL")
        return False
    
    # Check if customers.js file exists
    try:
        response = requests.get(f"{BASE_URL}/static/js/modules/customers.js")
        if response.status_code == 200:
            print_test("customers.js module exists and loads", "PASS")
            
            # Check for key functions in customers.js
            content = response.text
            if 'export function initCustomers' in content:
                print_test("initCustomers function exists", "PASS")
            else:
                print_test("initCustomers function NOT found", "FAIL")
                return False
            
            if 'export async function loadCustomers' in content:
                print_test("loadCustomers function exists", "PASS")
            else:
                print_test("loadCustomers function NOT found", "FAIL")
                return False
        else:
            print_test(f"customers.js returned status {response.status_code}", "FAIL")
            return False
    except Exception as e:
        print_test(f"Error loading customers.js: {e}", "FAIL")
        return False
    
    return True

def test_css_styles():
    """Test that CSS file loads and contains customer styles"""
    print("\n=== TEST 4: CSS Styles ===")
    
    try:
        response = requests.get(f"{BASE_URL}/static/css/main.css")
        if response.status_code == 200:
            print_test("main.css loads successfully", "PASS")
            
            content = response.text
            
            # Check for customer view styles
            required_classes = [
                '.page-view',
                '.data-table',
                '.customer-details',
                '.modal',
                '.button.primary'
            ]
            
            all_found = True
            for css_class in required_classes:
                if css_class in content:
                    print_test(f"  {css_class} style exists", "PASS")
                else:
                    print_test(f"  {css_class} style NOT found", "FAIL")
                    all_found = False
            
            return all_found
        else:
            print_test(f"main.css returned status {response.status_code}", "FAIL")
            return False
    except Exception as e:
        print_test(f"Error loading main.css: {e}", "FAIL")
        return False

def test_api_endpoints_reachable():
    """Test that new API endpoints are reachable"""
    print("\n=== TEST 5: API Endpoints Reachable ===")
    
    try:
        # Test GET /api/customers
        response = requests.get(f"{BASE_URL}/api/customers")
        if response.status_code == 200:
            print_test("GET /api/customers is reachable", "PASS")
        else:
            print_test(f"GET /api/customers returned {response.status_code}", "FAIL")
            return False
        
        return True
    except Exception as e:
        print_test(f"Error reaching API endpoints: {e}", "FAIL")
        return False

def main():
    print("\n" + "=" * 70)
    print("  FRONTEND INTEGRATION TEST - Customers Feature")
    print("  Phase 5.6 - Verify UI loads correctly")
    print("=" * 70)
    
    print("\n[INFO] Testing frontend at http://localhost:5000")
    print("[INFO] Make sure Flask server is running: python app.py\n")
    
    results = []
    
    # Test 1: Load frontend
    html = test_frontend_loads()
    results.append(html is not None)
    
    if html:
        # Test 2: Check HTML elements
        results.append(test_html_elements(html))
        
        # Test 3: Check JavaScript modules
        results.append(test_javascript_modules(html))
    else:
        results.extend([False, False])
    
    # Test 4: Check CSS
    results.append(test_css_styles())
    
    # Test 5: Check API endpoints
    results.append(test_api_endpoints_reachable())
    
    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n  Passed: {passed}/{total} tests")
    
    if passed == total:
        print("\n  [SUCCESS] All frontend integration tests passed!")
        print("  [NEXT] Open browser and manually test:")
        print("    1. Navigate to http://localhost:5000")
        print("    2. Click 'Customers' in sidebar")
        print("    3. Verify customer list loads")
        print("    4. Test add/edit/delete operations")
        return 0
    else:
        print("\n  [FAIL] Some tests failed. Fix issues before proceeding.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

