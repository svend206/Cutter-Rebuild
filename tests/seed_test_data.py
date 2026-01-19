"""
Test Data Seeder - Pattern Matching Validation
Phase 5.5 Testing

Creates realistic historical quotes for testing pattern matching algorithms:
1. Genesis Hash patterns (same geometry)
2. Customer patterns (same customer)
3. Material patterns (same material)
4. Quantity patterns (low qty = prototype)
5. Lead Time patterns (rush jobs)

Usage:
    python tests/seed_test_data.py --scenario all
    python tests/seed_test_data.py --scenario genesis
    python tests/seed_test_data.py --clean (removes test data)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import json
import argparse
from datetime import datetime, timedelta
import random
import genesis_hash


# Support isolated test database via environment variable
DB_PATH = os.environ.get("TEST_DB_PATH", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cutter.db'))


def get_connection():
    """Get database connection with WAL mode"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.row_factory = sqlite3.Row
    return conn


def clean_test_data():
    """Remove all test data (quotes, parts, customers created by this script)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    print("[CLEAN] Cleaning test data...")
    
    # Delete test quotes (those with reference starting with TEST_)
    cursor.execute("DELETE FROM ops__quotes WHERE id IN (SELECT id FROM ops__quotes WHERE quote_id LIKE 'TEST_%')")
    deleted_quotes = cursor.rowcount
    
    # Delete test parts (those with filename starting with TEST_)
    cursor.execute("DELETE FROM ops__parts WHERE filename LIKE 'TEST_%'")
    deleted_parts = cursor.rowcount
    
    # Delete test customers (those with domain = 'test.local')
    cursor.execute("DELETE FROM ops__contacts WHERE customer_id IN (SELECT id FROM ops__customers WHERE domain = 'test.local')")
    cursor.execute("DELETE FROM ops__customers WHERE domain = 'test.local'")
    deleted_customers = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    print(f"[SUCCESS] Cleaned: {deleted_quotes} quotes, {deleted_parts} parts, {deleted_customers} customers")


def seed_genesis_pattern():
    """
    Scenario: Same geometry quoted 5 times with "Rush Job" tag (80% confidence)
    Tests: Genesis Hash pattern matching
    """
    print("\n[SEED] Seeding Genesis Hash Pattern...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create a test customer for Genesis quotes
    cursor.execute("""
        INSERT OR IGNORE INTO ops__customers (name, domain)
        VALUES (?, ?)
    """, ('TEST_Genesis_Customer', 'test.local'))
    
    cursor.execute("SELECT id FROM ops__customers WHERE name = 'TEST_Genesis_Customer'")
    customer_id = cursor.fetchone()[0]
    
    # Create a test part with known Genesis Hash
    volume = 8.0
    dimensions = (4.0, 2.0, 1.0)
    test_hash = genesis_hash.generate_genesis_hash(volume, dimensions)
    
    # Upsert part
    cursor.execute("""
        INSERT OR IGNORE INTO ops__parts (genesis_hash, filename, fingerprint_json, volume, surface_area, dimensions_json)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        test_hash,
        'TEST_Block_4x2x1.stl',
        json.dumps([0.8, 1.0, 2.0, 4.0, 0.56]),  # Fingerprint
        volume,
        28.0,  # Surface area
        json.dumps({'x': 4.0, 'y': 2.0, 'z': 1.0})
    ))
    
    part_id = cursor.lastrowid
    if part_id == 0:
        # Part already exists, get its ID
        cursor.execute("SELECT id FROM ops__parts WHERE genesis_hash = ?", (test_hash,))
        part_id = cursor.fetchone()[0]
    
    # Create 5 quotes for this part, 4 with "Rush Job" tag
    for i in range(5):
        has_rush = i < 4  # First 4 have rush, last 1 doesn't
        
        pricing_tags = {}
        if has_rush:
            pricing_tags['Rush Job'] = 20.0  # 20% markup
        
        cursor.execute("""
            INSERT INTO ops__quotes (
                part_id, customer_id, quote_id, material, quantity, 
                system_price_anchor, final_quoted_price,
                pricing_tags_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            part_id,
            customer_id,
            f'TEST_GENESIS_{i+1}',
            'Aluminum 6061',
            10 + i,
            100.0,
            120.0 if has_rush else 100.0,
            json.dumps(pricing_tags),
            (datetime.now() - timedelta(days=30-i)).isoformat()
        ))
    
    conn.commit()
    conn.close()
    
    print(f"[SUCCESS] Created 5 quotes for Genesis Hash {test_hash[:16]}...")
    print(f"   4 quotes have 'Rush Job' tag (80% confidence)")
    print(f"   Pattern matching should suggest 'Rush Job' for this geometry")


def seed_customer_pattern():
    """
    Scenario: SpaceX customer gets "Rush Job" + "AS9102 Required" on 8/10 quotes (80% confidence)
    Tests: Customer pattern matching
    """
    print("\n[CUSTOMER] Seeding Customer Pattern...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create test customer
    cursor.execute("""
        INSERT OR IGNORE INTO ops__customers (name, domain)
        VALUES (?, ?)
    """, ('TEST_SpaceX', 'test.local'))
    
    customer_id = cursor.lastrowid
    if customer_id == 0:
        cursor.execute("SELECT id FROM ops__customers WHERE name = 'TEST_SpaceX'")
        customer_id = cursor.fetchone()[0]
    
    # Create 10 quotes, 8 with common tags
    for i in range(10):
        has_pattern = i < 8  # First 8 have the pattern
        
        # Create unique part for each quote
        volume = 10.0 + i
        dimensions = (5.0, 2.0, 1.0 + (i * 0.1))
        test_hash = genesis_hash.generate_genesis_hash(volume, dimensions)
        
        cursor.execute("""
            INSERT OR IGNORE INTO ops__parts (genesis_hash, filename, volume)
            VALUES (?, ?, ?)
        """, (test_hash, f'TEST_SpaceX_Part_{i+1}.stl', volume))
        
        cursor.execute("SELECT id FROM ops__parts WHERE genesis_hash = ?", (test_hash,))
        part_id = cursor.fetchone()[0]
        
        pricing_tags = {}
        if has_pattern:
            pricing_tags['Rush Job'] = 20.0
            pricing_tags['AS9102 Required'] = 15.0
        
        cursor.execute("""
            INSERT INTO ops__quotes (
                part_id, customer_id, quote_id, material, quantity,
                system_price_anchor, final_quoted_price,
                pricing_tags_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            part_id,
            customer_id,
            f'TEST_CUSTOMER_{i+1}',
            'Aluminum 7075',
            25,
            150.0,
            202.5 if has_pattern else 150.0,  # 35% markup if pattern
            json.dumps(pricing_tags),
            (datetime.now() - timedelta(days=60-i)).isoformat()
        ))
    
    conn.commit()
    conn.close()
    
    print(f"[SUCCESS] Created 10 quotes for customer 'TEST_SpaceX'")
    print(f"   8 quotes have 'Rush Job' + 'AS9102 Required' tags (80% confidence)")
    print(f"   Pattern matching should suggest these tags for new SpaceX quotes")


def seed_material_pattern():
    """
    Scenario: Titanium material gets "Difficult Material" tag on 9/10 quotes (90% confidence)
    Tests: Material pattern matching
    """
    print("\n[MATERIAL] Seeding Material Pattern...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create a test customer for Material quotes
    cursor.execute("""
        INSERT OR IGNORE INTO ops__customers (name, domain)
        VALUES (?, ?)
    """, ('TEST_Material_Customer', 'test.local'))
    
    cursor.execute("SELECT id FROM ops__customers WHERE name = 'TEST_Material_Customer'")
    customer_id = cursor.fetchone()[0]
    
    # Create 10 quotes with Titanium, 9 with "Difficult Material" tag
    for i in range(10):
        has_pattern = i < 9  # First 9 have the pattern
        
        # Create unique part
        volume = 5.0 + i
        dimensions = (3.0, 2.0, 1.0 + (i * 0.05))
        test_hash = genesis_hash.generate_genesis_hash(volume, dimensions)
        
        cursor.execute("""
            INSERT OR IGNORE INTO ops__parts (genesis_hash, filename, volume)
            VALUES (?, ?, ?)
        """, (test_hash, f'TEST_Titanium_Part_{i+1}.stl', volume))
        
        cursor.execute("SELECT id FROM ops__parts WHERE genesis_hash = ?", (test_hash,))
        part_id = cursor.fetchone()[0]
        
        pricing_tags = {}
        if has_pattern:
            pricing_tags['Difficult Material'] = 25.0
        
        cursor.execute("""
            INSERT INTO ops__quotes (
                part_id, customer_id, quote_id, material, quantity,
                system_price_anchor, final_quoted_price,
                pricing_tags_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            part_id,
            customer_id,
            f'TEST_MATERIAL_{i+1}',
            'Titanium',
            10,
            200.0,
            250.0 if has_pattern else 200.0,  # 25% markup if pattern
            json.dumps(pricing_tags),
            (datetime.now() - timedelta(days=90-i)).isoformat()
        ))
    
    conn.commit()
    conn.close()
    
    print(f"[SUCCESS] Created 10 quotes for Titanium material")
    print(f"   9 quotes have 'Difficult Material' tag (90% confidence)")
    print(f"   Pattern matching should suggest this tag for Titanium quotes")


def seed_quantity_pattern():
    """
    Scenario: Low quantity (1-5) gets "Prototype" tag on 12/15 quotes (80% confidence)
    Tests: Quantity pattern matching
    """
    print("\n[QUANTITY] Seeding Quantity Pattern...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create a test customer for Quantity quotes
    cursor.execute("""
        INSERT OR IGNORE INTO ops__customers (name, domain)
        VALUES (?, ?)
    """, ('TEST_Quantity_Customer', 'test.local'))
    
    cursor.execute("SELECT id FROM ops__customers WHERE name = 'TEST_Quantity_Customer'")
    customer_id = cursor.fetchone()[0]
    
    # Create 15 quotes with qty 1-5, 12 with "Prototype" tag
    for i in range(15):
        has_pattern = i < 12  # First 12 have the pattern
        qty = random.randint(1, 5)
        
        # Create unique part
        volume = 3.0 + i
        dimensions = (2.0, 1.5, 1.0 + (i * 0.03))
        test_hash = genesis_hash.generate_genesis_hash(volume, dimensions)
        
        cursor.execute("""
            INSERT OR IGNORE INTO ops__parts (genesis_hash, filename, volume)
            VALUES (?, ?, ?)
        """, (test_hash, f'TEST_Proto_Part_{i+1}.stl', volume))
        
        cursor.execute("SELECT id FROM ops__parts WHERE genesis_hash = ?", (test_hash,))
        part_id = cursor.fetchone()[0]
        
        pricing_tags = {}
        if has_pattern:
            pricing_tags['Prototype'] = 10.0
        
        cursor.execute("""
            INSERT INTO ops__quotes (
                part_id, customer_id, quote_id, material, quantity,
                system_price_anchor, final_quoted_price,
                pricing_tags_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            part_id,
            customer_id,
            f'TEST_QUANTITY_{i+1}',
            'Aluminum 6061',
            qty,
            50.0,
            55.0 if has_pattern else 50.0,  # 10% markup if pattern
            json.dumps(pricing_tags),
            (datetime.now() - timedelta(days=45-i)).isoformat()
        ))
    
    conn.commit()
    conn.close()
    
    print(f"[SUCCESS] Created 15 quotes with low quantities (1-5 units)")
    print(f"   12 quotes have 'Prototype' tag (80% confidence)")
    print(f"   Pattern matching should suggest this tag for low-qty quotes")


def seed_lead_time_pattern():
    """
    Scenario: Rush lead time (< 7 days) gets "Expedite" tag on 14/15 quotes (93% confidence)
    Tests: Lead time pattern matching
    """
    print("\n[LEADTIME] Seeding Lead Time Pattern...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create a test customer for Lead Time quotes
    cursor.execute("""
        INSERT OR IGNORE INTO ops__customers (name, domain)
        VALUES (?, ?)
    """, ('TEST_LeadTime_Customer', 'test.local'))
    
    cursor.execute("SELECT id FROM ops__customers WHERE name = 'TEST_LeadTime_Customer'")
    customer_id = cursor.fetchone()[0]
    
    # Create 15 quotes with lead time < 7 days, 14 with "Expedite" tag
    for i in range(15):
        has_pattern = i < 14  # First 14 have the pattern
        lead_days = random.randint(1, 6)
        
        # Create unique part
        volume = 4.0 + i
        dimensions = (2.5, 1.5, 1.0 + (i * 0.04))
        test_hash = genesis_hash.generate_genesis_hash(volume, dimensions)
        
        cursor.execute("""
            INSERT OR IGNORE INTO ops__parts (genesis_hash, filename, volume)
            VALUES (?, ?, ?)
        """, (test_hash, f'TEST_Rush_Part_{i+1}.stl', volume))
        
        cursor.execute("SELECT id FROM ops__parts WHERE genesis_hash = ?", (test_hash,))
        part_id = cursor.fetchone()[0]
        
        pricing_tags = {}
        if has_pattern:
            pricing_tags['Expedite'] = 30.0
        
        lead_time_date = (datetime.now() + timedelta(days=lead_days)).date().isoformat()
        
        cursor.execute("""
            INSERT INTO ops__quotes (
                part_id, customer_id, quote_id, material, quantity, lead_time_days, lead_time_date,
                system_price_anchor, final_quoted_price,
                pricing_tags_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            part_id,
            customer_id,
            f'TEST_LEADTIME_{i+1}',
            'Aluminum 6061',
            15,
            lead_days,
            lead_time_date,
            75.0,
            97.5 if has_pattern else 75.0,  # 30% markup if pattern
            json.dumps(pricing_tags),
            (datetime.now() - timedelta(days=20-i)).isoformat()
        ))
    
    conn.commit()
    conn.close()
    
    print(f"[SUCCESS] Created 15 quotes with rush lead times (< 7 days)")
    print(f"   14 quotes have 'Expedite' tag (93% confidence)")
    print(f"   Pattern matching should suggest this tag for rush quotes")


def main():
    parser = argparse.ArgumentParser(description='Seed test data for pattern matching')
    parser.add_argument('--scenario', choices=['all', 'genesis', 'customer', 'material', 'quantity', 'leadtime', 'clean'], 
                       default='all', help='Which test scenario to seed')
    
    args = parser.parse_args()
    
    print("="*60)
    print("PATTERN MATCHING TEST DATA SEEDER")
    print("="*60)
    
    if args.scenario == 'clean':
        clean_test_data()
        return
    
    scenarios = {
        'genesis': seed_genesis_pattern,
        'customer': seed_customer_pattern,
        'material': seed_material_pattern,
        'quantity': seed_quantity_pattern,
        'leadtime': seed_lead_time_pattern
    }
    
    if args.scenario == 'all':
        for name, func in scenarios.items():
            func()
    else:
        scenarios[args.scenario]()
    
    print("\n" + "="*60)
    print("[SUCCESS] TEST DATA SEEDED SUCCESSFULLY")
    print("="*60)
    print("\nNext Steps:")
    print("1. Start the server: python app.py")
    print("2. Open browser to http://localhost:5000")
    print("3. Create a new quote with matching criteria")
    print("4. Verify Ted View banner appears with suggestions")
    print("\nTo clean test data later:")
    print("  python tests/seed_test_data.py --clean")


if __name__ == '__main__':
    main()

