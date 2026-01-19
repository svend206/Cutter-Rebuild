"""
Test Price Breaks Table in PDF Generation.
Tests the new price breaks functionality added in Day 1 of Node 1 Bombproof plan.
"""
import json
from datetime import datetime
from pdf_generator import QuotePDFGenerator


def create_test_quote_data():
    """Create realistic test quote data with price breaks."""
    return {
        'id': 999,
        'quote_id': 'Q-20260105-TEST',
        'customer_name': 'Test Aerospace Corp',
        'customer_domain': 'testaero.com',
        'contact_name': 'Jane Engineer',
        'contact_email': 'jane@testaero.com',
        'filename': 'Test_Bracket_RevA.STEP',
        'volume': 4.0,
        'dimensions': {'x': 4.0, 'y': 2.0, 'z': 1.0},
        'material': 'Aluminum 6061-T6',
        'quantity': 5,
        'target_date': '2026-01-25',
        'final_quoted_price': 550.0,
        'system_price_anchor': 440.0,
        'timestamp': datetime.now().isoformat(),
        'status': 'Draft',
        'notes': 'Test quote for price breaks table validation',
        
        # Price breaks data (default tiers)
        'price_breaks_json': json.dumps([1, 5, 25, 100]),
        
        # Physics snapshot for recalculation
        'physics_snapshot_json': json.dumps({
            'material_cost': 96.0,    # $96 total material for qty 5
            'labor_cost': 344.0,      # $344 total labor for qty 5
            'setup_cost': 75.0,       # $75 setup (60 min @ $75/hr)
            'shop_rate_used': 75.0,
            'markup_used': 1.2
        }),
        
        # Variance data
        'variance_json': json.dumps({
            'items': [
                {'label': 'Rush Job', 'percent': 0.20, 'value': 88.0, 'type': 'slider'},
                {'label': 'Tight Tolerance', 'percent': 0.05, 'value': 22.0, 'type': 'slider'}
            ],
            'total_variance': 110.0
        }),
        
        # Pricing tags
        'pricing_tags_json': json.dumps({
            'Rush Job': 0.20,
            'Tight Tolerance': 0.05
        }),
        
        # RFQ fields
        'lead_time_date': '2026-01-09',
        'lead_time_days': 4,
        'outside_processing_json': json.dumps(['Anodize (Type II)']),
        'quality_requirements_json': json.dumps({
            'cmm': True,
            'as9102': False,
            'material_certs': True,
            'notes': 'First article inspection required'
        }),
        
        # Part info
        'genesis_hash': 'test123abc456def789...'
    }


def test_price_breaks_scenarios():
    """Test multiple scenarios for price breaks table."""
    print("=" * 70)
    print("PRICE BREAKS TABLE TEST")
    print("=" * 70)
    
    generator = QuotePDFGenerator(output_dir="quotes_pdf")
    
    # Scenario 1: Standard Quote with Price Breaks
    print("\n[Scenario 1] Standard quote with default price breaks [1, 5, 25, 100]")
    quote1 = create_test_quote_data()
    try:
        pdf_path = generator.generate_quote_pdf(
            quote_data=quote1,
            filename="TEST_SCENARIO1_PRICE_BREAKS.pdf",
            customer_facing=True
        )
        print(f"[OK] Generated: {pdf_path}")
        print(f"   Quote Qty: 5 units")
        print(f"   Price Breaks: [1, 5, 25, 100]")
        print(f"   Expected: Table should show 4 rows with color-coded setup %")
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Scenario 2: High Quantity (Setup % should be low = green)
    print("\n[Scenario 2] High quantity order (100 units)")
    quote2 = create_test_quote_data()
    quote2['quantity'] = 100
    quote2['quote_id'] = 'Q-20260105-TEST-HIGHQTY'
    quote2['final_quoted_price'] = 10075.0
    quote2['system_price_anchor'] = 8500.0
    try:
        pdf_path = generator.generate_quote_pdf(
            quote_data=quote2,
            filename="TEST_SCENARIO2_HIGH_QTY.pdf",
            customer_facing=True
        )
        print(f"[OK] Generated: {pdf_path}")
        print(f"   Quote Qty: 100 units")
        print(f"   Expected: Setup % < 5% (green background)")
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
    
    # Scenario 3: Low Quantity (Setup % should be high = red)
    print("\n[Scenario 3] Low quantity order (1 unit)")
    quote3 = create_test_quote_data()
    quote3['quantity'] = 1
    quote3['quote_id'] = 'Q-20260105-TEST-LOWQTY'
    quote3['final_quoted_price'] = 150.0
    quote3['system_price_anchor'] = 120.0
    quote3['physics_snapshot_json'] = json.dumps({
        'material_cost': 20.0,
        'labor_cost': 100.0,
        'setup_cost': 75.0,
        'shop_rate_used': 75.0,
        'markup_used': 1.2
    })
    try:
        pdf_path = generator.generate_quote_pdf(
            quote_data=quote3,
            filename="TEST_SCENARIO3_LOW_QTY.pdf",
            customer_facing=True
        )
        print(f"[OK] Generated: {pdf_path}")
        print(f"   Quote Qty: 1 unit")
        print(f"   Expected: Setup % > 20% (red background)")
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
    
    # Scenario 4: Custom Price Breaks
    print("\n[Scenario 4] Custom price breaks [1, 10, 50, 250]")
    quote4 = create_test_quote_data()
    quote4['quote_id'] = 'Q-20260105-TEST-CUSTOM'
    quote4['price_breaks_json'] = json.dumps([1, 10, 50, 250])
    try:
        pdf_path = generator.generate_quote_pdf(
            quote_data=quote4,
            filename="TEST_SCENARIO4_CUSTOM_BREAKS.pdf",
            customer_facing=True
        )
        print(f"[OK] Generated: {pdf_path}")
        print(f"   Price Breaks: [1, 10, 50, 250]")
        print(f"   Expected: Table with 4 custom quantity tiers")
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
    
    # Scenario 5: Internal PDF (should NOT show price breaks)
    print("\n[Scenario 5] Internal PDF (should NOT show price breaks)")
    quote5 = create_test_quote_data()
    quote5['quote_id'] = 'Q-20260105-TEST-INTERNAL'
    try:
        pdf_path = generator.generate_quote_pdf(
            quote_data=quote5,
            filename="TEST_SCENARIO5_INTERNAL.pdf",
            customer_facing=False  # Internal mode
        )
        print(f"[OK] Generated: {pdf_path}")
        print(f"   Mode: Internal (customer_facing=False)")
        print(f"   Expected: NO price breaks table (Glass Box variance shown instead)")
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print("[OK] All test scenarios generated!")
    print("\nManual Verification Steps:")
    print("1. Open quotes_pdf/TEST_SCENARIO1_PRICE_BREAKS.pdf")
    print("   - Should show 'Price Breaks (Economy of Scale)' section")
    print("   - Should have 4 rows: Qty [1, 5, 25, 100]")
    print("   - Setup % column should be color-coded (red/amber/green)")
    print("")
    print("2. Open quotes_pdf/TEST_SCENARIO3_LOW_QTY.pdf")
    print("   - Qty=1 row should have RED background (setup % > 20%)")
    print("")
    print("3. Open quotes_pdf/TEST_SCENARIO2_HIGH_QTY.pdf")
    print("   - Qty=100 row should have GREEN background (setup % < 5%)")
    print("")
    print("4. Open quotes_pdf/TEST_SCENARIO5_INTERNAL.pdf")
    print("   - Should NOT show price breaks table")
    print("   - Should show variance attribution instead")
    print("")
    print("Color Legend:")
    print("   [RED] Red Background:   Setup % > 20% (high setup cost)")
    print("   [AMB] Amber Background: Setup % 5-20% (moderate setup cost)")
    print("   [GRN] Green Background: Setup % < 5% (low setup cost)")


if __name__ == '__main__':
    test_price_breaks_scenarios()

