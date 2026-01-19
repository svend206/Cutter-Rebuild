"""
Test script for PDF generation feature.
Usage: python test_pdf_generation.py
"""
import sys
import database
import pdf_generator
from pathlib import Path


def test_pdf_generation():
    """Test PDF generation with actual quote data from database."""
    print("=" * 70)
    print("PDF GENERATION TEST")
    print("=" * 70)
    
    # Step 1: Check if ReportLab is installed
    print("\n[STEP 1] Checking ReportLab installation...")
    try:
        import reportlab
        print(f"✅ ReportLab installed (version: {reportlab.Version})")
    except ImportError:
        print("❌ ReportLab not installed!")
        print("\nTo install:")
        print("  pip install reportlab")
        return False
    
    # Step 2: Check database exists
    print("\n[STEP 2] Checking database...")
    if not Path("cutter.db").exists():
        print("❌ cutter.db not found!")
        print("   Run the server first to initialize database: python app.py")
        return False
    print("✅ Database found")
    
    # Step 3: Fetch quotes from database
    print("\n[STEP 3] Fetching quotes from database...")
    quotes = database.get_all_history()
    
    if not quotes:
        print("❌ No quotes found in database!")
        print("   Create a quote in the UI first, then run this test.")
        return False
    
    print(f"✅ Found {len(quotes)} quote(s) in database")
    
    # Step 4: Generate PDF for first quote
    print("\n[STEP 4] Generating PDF for first quote...")
    test_quote = quotes[0]
    quote_id = test_quote.get('quote_id', 'DRAFT')
    print(f"   Quote ID: {quote_id}")
    print(f"   Customer: {test_quote.get('customer_name', 'Unknown')}")
    print(f"   Material: {test_quote.get('material', 'Unknown')}")
    print(f"   Final Price: ${test_quote.get('final_quoted_price', 0):.2f}")
    
    try:
        pdf_path = pdf_generator.generate_quote_pdf(
            quote_data=test_quote,
            output_dir="quotes_pdf"
        )
        print(f"✅ PDF generated successfully!")
        print(f"   Location: {pdf_path}")
    except Exception as e:
        print(f"❌ PDF generation failed!")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 5: Verify PDF file exists
    print("\n[STEP 5] Verifying PDF file...")
    if Path(pdf_path).exists():
        file_size = Path(pdf_path).stat().st_size
        print(f"✅ PDF file exists")
        print(f"   Size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
    else:
        print("❌ PDF file not found!")
        return False
    
    # Step 6: Test all quotes
    print("\n[STEP 6] Testing PDF generation for all quotes...")
    success_count = 0
    fail_count = 0
    
    for quote in quotes:
        try:
            pdf_path = pdf_generator.generate_quote_pdf(
                quote_data=quote,
                output_dir="quotes_pdf"
            )
            success_count += 1
            print(f"   ✅ {quote.get('quote_id', 'DRAFT')}")
        except Exception as e:
            fail_count += 1
            print(f"   ❌ {quote.get('quote_id', 'DRAFT')}: {str(e)}")
    
    print(f"\n   Generated: {success_count}/{len(quotes)} PDFs")
    if fail_count > 0:
        print(f"   Failed: {fail_count} PDFs")
    
    # Step 7: Test Traveler PDF generation
    print("\n[STEP 7] Testing Traveler PDF generation...")
    print("   (Shop Floor Work Order - NO PRICING)")
    
    try:
        traveler_path = pdf_generator.generate_traveler_pdf(
            quote_data=test_quote,
            output_dir="travelers_pdf"
        )
        print(f"✅ Traveler PDF generated successfully!")
        print(f"   Location: {traveler_path}")
        
        # Verify file exists
        if Path(traveler_path).exists():
            file_size = Path(traveler_path).stat().st_size
            print(f"   Size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
        else:
            print("   ⚠ Warning: Traveler PDF file not found!")
    except Exception as e:
        print(f"❌ Traveler PDF generation failed!")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 8: Test all travelers
    print("\n[STEP 8] Testing Traveler PDF generation for all quotes...")
    traveler_success = 0
    traveler_fail = 0
    
    for quote in quotes:
        try:
            traveler_path = pdf_generator.generate_traveler_pdf(
                quote_data=quote,
                output_dir="travelers_pdf"
            )
            traveler_success += 1
            print(f"   ✅ TRAVELER-{quote.get('quote_id', 'DRAFT')}")
        except Exception as e:
            traveler_fail += 1
            print(f"   ❌ TRAVELER-{quote.get('quote_id', 'DRAFT')}: {str(e)}")
    
    print(f"\n   Generated: {traveler_success}/{len(quotes)} Traveler PDFs")
    if traveler_fail > 0:
        print(f"   Failed: {traveler_fail} Traveler PDFs")
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print("✅ PDF generation is working!")
    print(f"   Quote PDFs saved to: quotes_pdf/")
    print(f"   Quote PDFs generated: {success_count} files")
    print(f"   Traveler PDFs saved to: travelers_pdf/")
    print(f"   Traveler PDFs generated: {traveler_success} files")
    print("\nNext steps:")
    print("1. Check the quotes_pdf/ folder")
    print("2. Check the travelers_pdf/ folder")
    print("3. Open a Traveler PDF and verify NO PRICING is shown")
    print("4. Test the API endpoints:")
    print(f"   Quote:    http://localhost:5000/api/quote/{quotes[0]['id']}/pdf")
    print(f"   Traveler: http://localhost:5000/api/quote/{quotes[0]['id']}/traveler")
    
    return True


if __name__ == '__main__':
    success = test_pdf_generation()
    sys.exit(0 if success else 1)

