"""
Test QR Code Generation in Traveler PDFs.
Tests the new QR code functionality added in Day 1 of Node 1 Bombproof plan.
"""
import json
from datetime import datetime
from pdf_generator import QuotePDFGenerator


def create_test_traveler_data():
    """Create realistic test data for Traveler PDF."""
    return {
        'id': 999,
        'quote_id': 'Q-20260105-QR-TEST',
        'customer_name': 'Test Aerospace Corp',
        'filename': 'Test_Part_QR.STEP',
        'volume': 4.0,
        'dimensions': {'x': 4.0, 'y': 2.0, 'z': 1.0},
        'material': 'Aluminum 6061-T6',
        'quantity': 25,
        'target_date': '2026-01-25',
        'timestamp': datetime.now().isoformat(),
        'status': 'Sent',
        'notes': 'Test traveler for QR code validation',
        
        # Process routing for traveler
        'process_routing': ['3-Axis Mill', 'Deburr', 'Wash'],
        
        # Outside processing
        'outside_processing_json': json.dumps(['Anodize (Type II)', 'Final Inspection']),
        
        # Quality requirements
        'quality_requirements_json': json.dumps({
            'cmm': True,
            'as9102': False,
            'material_certs': True,
            'notes': 'CMM inspection required for critical dimensions'
        }),
        
        # Part marking
        'part_marking_json': json.dumps({
            'type': 'Laser Etch',
            'content': 'P/N: TEST-999-A'
        })
    }


def test_qr_code_generation():
    """Test QR code generation in Traveler PDFs."""
    print("=" * 70)
    print("QR CODE GENERATION TEST")
    print("=" * 70)
    
    generator = QuotePDFGenerator(output_dir="travelers_pdf")
    
    # Test 1: Standard Traveler with QR Code
    print("\n[Test 1] Standard Traveler with QR Code")
    traveler1 = create_test_traveler_data()
    try:
        pdf_path = generator.generate_traveler_pdf(
            quote_data=traveler1,
            filename="TRAVELER-TEST-QR-STANDARD.pdf"
        )
        print(f"[OK] Generated: {pdf_path}")
        print(f"   Job ID: {traveler1['quote_id']}")
        print(f"   Expected: QR code should encode 'Q-20260105-QR-TEST'")
        print(f"   Verification: Scan QR code with phone - should display Job ID")
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Traveler with Complex Job ID
    print("\n[Test 2] Traveler with Complex Job ID")
    traveler2 = create_test_traveler_data()
    traveler2['quote_id'] = 'Q-20260105-COMPLEX-ID-WITH-DASHES-999'
    try:
        pdf_path = generator.generate_traveler_pdf(
            quote_data=traveler2,
            filename="TRAVELER-TEST-QR-COMPLEX.pdf"
        )
        print(f"[OK] Generated: {pdf_path}")
        print(f"   Job ID: {traveler2['quote_id']}")
        print(f"   Expected: QR code should handle long IDs correctly")
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
    
    # Test 3: Traveler with Minimal Data
    print("\n[Test 3] Traveler with Minimal Data (fallback test)")
    traveler3 = {
        'quote_id': 'Q-MINIMAL',
        'filename': 'Minimal.STEP',
        'material': 'Aluminum 6061',
        'quantity': 1,
        'volume': 1.0,
        'dimensions': {'x': 1.0, 'y': 1.0, 'z': 1.0},
        'process_routing': []
    }
    try:
        pdf_path = generator.generate_traveler_pdf(
            quote_data=traveler3,
            filename="TRAVELER-TEST-QR-MINIMAL.pdf"
        )
        print(f"[OK] Generated: {pdf_path}")
        print(f"   Job ID: {traveler3['quote_id']}")
        print(f"   Expected: QR code should work with minimal data")
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
    
    # Test 4: Verify NO PRICING in Traveler
    print("\n[Test 4] Verify NO PRICING in Traveler (security check)")
    traveler4 = create_test_traveler_data()
    traveler4['quote_id'] = 'Q-SECURITY-TEST'
    traveler4['final_quoted_price'] = 12345.67  # This should NOT appear
    traveler4['system_price_anchor'] = 10000.00  # This should NOT appear
    try:
        pdf_path = generator.generate_traveler_pdf(
            quote_data=traveler4,
            filename="TRAVELER-TEST-SECURITY.pdf"
        )
        print(f"[OK] Generated: {pdf_path}")
        print(f"   CRITICAL: Open PDF and verify NO pricing information is visible")
        print(f"   Final Price: ${traveler4['final_quoted_price']:.2f} (should NOT appear)")
        print(f"   Anchor Price: ${traveler4['system_price_anchor']:.2f} (should NOT appear)")
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print("[OK] QR code generation tests complete!")
    print("\nManual Verification Steps:")
    print("1. Open travelers_pdf/TRAVELER-TEST-QR-STANDARD.pdf")
    print("   - Should show shop branding header")
    print("   - Should show 'WORK ORDER: Q-20260105-QR-TEST'")
    print("   - Should show a scannable QR code (black and white)")
    print("")
    print("2. Scan QR code with phone camera:")
    print("   - Should decode to: 'Q-20260105-QR-TEST'")
    print("   - Verify it's readable (not blurry or malformed)")
    print("")
    print("3. Open travelers_pdf/TRAVELER-TEST-SECURITY.pdf")
    print("   - CRITICAL: Verify NO pricing information anywhere")
    print("   - Should only show: Part info, process routing, QC grid")
    print("")
    print("QR Code Spec:")
    print("   - Encoding: Job ID (quote_id)")
    print("   - Size: 1.5 inches x 1.5 inches")
    print("   - Error Correction: Low (L)")
    print("   - Format: PNG, black on white")


if __name__ == '__main__':
    test_qr_code_generation()

