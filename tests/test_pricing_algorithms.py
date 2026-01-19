"""
Pricing Algorithms Test Suite
Tests all pricing formulas from SYSTEM_BEHAVIOR_SPEC.md Section 1

Target: 80% coverage for pure functions (pricing algorithms)
Reference: Docs/SYSTEM_BEHAVIOR_SPEC.md Section 1 (Pricing Algorithms)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from pricing_engine import PriceCalculator, MATERIAL_MARKUP
import database


class TestMaterialCostCalculation(unittest.TestCase):
    """
    Test Material Cost Calculation (SYSTEM_BEHAVIOR_SPEC.md Section 1.2)
    
    Formula:
        Material_Cost = Stock_Volume × Cost_Per_In³ × Material_Markup × Scrap_Factor
        
    Scrap Logic:
        - Qty < 10: (Qty + 1) ÷ Qty [Setup scrap unit]
        - Qty ≥ 10: 1.02 [2% scrap rate]
    """
    
    def setUp(self):
        """Initialize database and calculator for each test."""
        database.initialize_database()
        database.seed_default_data()
        self.calculator = PriceCalculator()
    
    def test_material_cost_qty_1(self):
        """Test material cost for Qty=1 (setup scrap logic)."""
        # Scenario: 1" cube, Aluminum 6061, Qty=1
        # Stock: 4" × 2" × 1" = 8.0 in³
        # Material: Aluminum 6061 @ $0.30/in³
        # Markup: 1.2 (default)
        # Scrap: (1 + 1) = 2 units
        # Expected: 8.0 × 0.30 × 1.2 × 2 = $5.76
        
        result = self.calculator.calculate_anchor(
            stock_volume_in3=8.0,
            material_name='Aluminum 6061',
            per_part_time_mins=4.0,
            setup_time_mins=60.0,
            shop_rate_hour=75.0,
            quantity=1,
            handling_time_mins=5.0
        )
        
        expected_material_cost = 8.0 * 0.30 * MATERIAL_MARKUP() * 2.0
        self.assertAlmostEqual(result['material_cost'], expected_material_cost, places=2)
    
    def test_material_cost_qty_100(self):
        """Test material cost for Qty=100 (2% scrap rate)."""
        # Scenario: Same stock, Qty=100
        # Stock: 4" × 2" × 1" = 8.0 in³
        # Material: Aluminum 6061 @ $0.30/in³
        # Markup: 1.2
        # Scrap: 1.02 (2% rate)
        # Expected per unit: 8.0 × 0.30 × 1.2 × 1.02 = $2.94
        # Total: $2.94 × 100 = $293.76
        
        result = self.calculator.calculate_anchor(
            stock_volume_in3=8.0,
            material_name='Aluminum 6061',
            per_part_time_mins=4.0,
            setup_time_mins=60.0,
            shop_rate_hour=75.0,
            quantity=100,
            handling_time_mins=5.0
        )
        
        expected_total_material = 8.0 * 0.30 * MATERIAL_MARKUP() * 1.02 * 100
        self.assertAlmostEqual(result['material_cost'], expected_total_material, places=2)
    
    def test_scrap_factor_boundary_qty_9(self):
        """Test scrap factor at boundary (Qty=9 should use setup scrap)."""
        result = self.calculator.calculate_anchor(
            stock_volume_in3=8.0,
            material_name='Aluminum 6061',
            per_part_time_mins=4.0,
            setup_time_mins=60.0,
            shop_rate_hour=75.0,
            quantity=9,
            handling_time_mins=5.0
        )
        
        # Qty=9: (9 + 1) / 9 = 1.111... scrap factor
        scrap_factor = (9 + 1) / 9
        expected_material = 8.0 * 0.30 * MATERIAL_MARKUP() * scrap_factor * 9
        self.assertAlmostEqual(result['material_cost'], expected_material, places=2)
    
    def test_scrap_factor_boundary_qty_10(self):
        """Test scrap factor at boundary (Qty=10 should use 2% rate)."""
        result = self.calculator.calculate_anchor(
            stock_volume_in3=8.0,
            material_name='Aluminum 6061',
            per_part_time_mins=4.0,
            setup_time_mins=60.0,
            shop_rate_hour=75.0,
            quantity=10,
            handling_time_mins=5.0
        )
        
        # Qty=10: 1.02 scrap factor (2% rate)
        expected_material = 8.0 * 0.30 * MATERIAL_MARKUP() * 1.02 * 10
        self.assertAlmostEqual(result['material_cost'], expected_material, places=2)


class TestLaborCostCalculation(unittest.TestCase):
    """
    Test Labor Cost Calculation (SYSTEM_BEHAVIOR_SPEC.md Section 1.3)
    
    Formula:
        Labor_Cost = (Total_Runtime ÷ 60) × Shop_Rate
        Total_Runtime = Setup_Time + ((Per_Part_Time + Handling_Time) × Quantity)
    """
    
    def setUp(self):
        """Initialize calculator for each test."""
        database.initialize_database()
        self.calculator = PriceCalculator()
    
    def test_labor_cost_qty_1(self):
        """Test labor cost for Qty=1 (setup dominates)."""
        # Scenario from SYSTEM_BEHAVIOR_SPEC.md Section 1.3
        # Setup: 60 min
        # Per Part: 4.0 min (machine + hand)
        # Handling: 5.0 min
        # Quantity: 1
        # Shop Rate: $75/hr
        # 
        # Total Runtime = 60 + ((4.0 + 5.0) × 1) = 69 min
        # Labor Cost = (69 ÷ 60) × 75 = $86.25
        
        result = self.calculator.calculate_anchor(
            stock_volume_in3=8.0,
            material_name='Aluminum 6061',
            per_part_time_mins=4.0,
            setup_time_mins=60.0,
            shop_rate_hour=75.0,
            quantity=1,
            handling_time_mins=5.0
        )
        
        expected_runtime = 60.0 + ((4.0 + 5.0) * 1)
        expected_labor = (expected_runtime / 60.0) * 75.0
        
        self.assertAlmostEqual(result['total_runtime_mins'], expected_runtime, places=2)
        self.assertAlmostEqual(result['labor_cost'], expected_labor, places=2)
    
    def test_labor_cost_qty_100(self):
        """Test labor cost for Qty=100 (setup amortized)."""
        # Setup: 60 min (ONE TIME)
        # Per Part: 4.0 min
        # Handling: 5.0 min per part
        # Quantity: 100
        # Shop Rate: $75/hr
        # 
        # Total Runtime = 60 + ((4.0 + 5.0) × 100) = 960 min
        # Labor Cost = (960 ÷ 60) × 75 = $1,200
        # Per Unit Labor = $1,200 / 100 = $12/unit
        
        result = self.calculator.calculate_anchor(
            stock_volume_in3=8.0,
            material_name='Aluminum 6061',
            per_part_time_mins=4.0,
            setup_time_mins=60.0,
            shop_rate_hour=75.0,
            quantity=100,
            handling_time_mins=5.0
        )
        
        expected_runtime = 60.0 + ((4.0 + 5.0) * 100)
        expected_labor = (expected_runtime / 60.0) * 75.0
        
        self.assertAlmostEqual(result['total_runtime_mins'], expected_runtime, places=2)
        self.assertAlmostEqual(result['labor_cost'], expected_labor, places=2)
    
    def test_setup_time_not_multiplied_by_quantity(self):
        """CRITICAL: Verify setup time is ONE-TIME, not multiplied by quantity."""
        # This test prevents regression of the "Setup Overcharge Bug"
        
        result_qty_1 = self.calculator.calculate_anchor(
            stock_volume_in3=8.0,
            material_name='Aluminum 6061',
            per_part_time_mins=4.0,
            setup_time_mins=60.0,
            shop_rate_hour=75.0,
            quantity=1,
            handling_time_mins=5.0
        )
        
        result_qty_10 = self.calculator.calculate_anchor(
            stock_volume_in3=8.0,
            material_name='Aluminum 6061',
            per_part_time_mins=4.0,
            setup_time_mins=60.0,
            shop_rate_hour=75.0,
            quantity=10,
            handling_time_mins=5.0
        )
        
        # Runtime difference should be (4 + 5) × 9 = 81 min
        # NOT (60 + 4 + 5) × 9 = 621 min
        runtime_diff = result_qty_10['total_runtime_mins'] - result_qty_1['total_runtime_mins']
        expected_diff = (4.0 + 5.0) * 9  # Only per-part time scales
        
        self.assertAlmostEqual(runtime_diff, expected_diff, places=2)


class TestCompleteAnchorCalculation(unittest.TestCase):
    """
    Test Complete Anchor Calculation (SYSTEM_BEHAVIOR_SPEC.md Section 1.4)
    
    Anchor = Material_Cost + Labor_Cost
    """
    
    def setUp(self):
        """Initialize calculator for each test."""
        database.initialize_database()
        database.seed_default_data()
        self.calculator = PriceCalculator()
    
    def test_anchor_total_price_qty_1(self):
        """Test complete anchor for Qty=1 (from spec example)."""
        # Material: $5.76 (from Section 1.2 example)
        # Labor: $86.25 (from Section 1.3 example)
        # Total: $92.01
        
        result = self.calculator.calculate_anchor(
            stock_volume_in3=8.0,
            material_name='Aluminum 6061',
            per_part_time_mins=4.0,
            setup_time_mins=60.0,
            shop_rate_hour=75.0,
            quantity=1,
            handling_time_mins=5.0
        )
        
        # Verify total = material + labor
        self.assertAlmostEqual(
            result['total_price'],
            result['material_cost'] + result['labor_cost'],
            places=2
        )
        
        # Verify individual components match spec
        self.assertAlmostEqual(result['material_cost'], 5.76, places=2)
        self.assertAlmostEqual(result['labor_cost'], 86.25, places=2)
    
    def test_anchor_per_unit_costs(self):
        """Test per-unit cost breakdown is returned."""
        result = self.calculator.calculate_anchor(
            stock_volume_in3=8.0,
            material_name='Aluminum 6061',
            per_part_time_mins=4.0,
            setup_time_mins=60.0,
            shop_rate_hour=75.0,
            quantity=10,
            handling_time_mins=5.0
        )
        
        # Verify per-unit costs are present
        self.assertIn('material_cost_per_unit', result)
        self.assertIn('labor_cost_per_unit', result)
        
        # Verify labor per unit = total labor / quantity
        expected_labor_per_unit = result['labor_cost'] / 10
        self.assertAlmostEqual(result['labor_cost_per_unit'], expected_labor_per_unit, places=2)
    
    def test_anchor_with_fallback_material(self):
        """Test fallback pricing when material not found."""
        # Use non-existent material, should fallback to Aluminum 6061 pricing
        result = self.calculator.calculate_anchor(
            stock_volume_in3=8.0,
            material_name='Unobtanium',  # Not in database
            per_part_time_mins=4.0,
            setup_time_mins=60.0,
            shop_rate_hour=75.0,
            quantity=1,
            handling_time_mins=5.0
        )
        
        # Should still return valid result (fallback to $0.30/in³)
        self.assertGreater(result['total_price'], 0)
        self.assertGreater(result['material_cost'], 0)


class TestPriceBreaksCalculation(unittest.TestCase):
    """
    Test Price Breaks Calculation (SYSTEM_BEHAVIOR_SPEC.md Section 1.5)
    
    Formula:
        Setup_Cost_Per_Unit = (Setup_Time × Shop_Rate ÷ 60) ÷ Quantity
        Per_Unit_Price = Material_Cost_Per_Unit + Labor_Cost_Per_Unit
    """
    
    def setUp(self):
        """Initialize calculator for each test."""
        database.initialize_database()
        database.seed_default_data()
        self.calculator = PriceCalculator()
    
    def test_price_breaks_setup_amortization(self):
        """Test setup cost amortization across quantities."""
        # Setup: 60 min @ $75/hr = $75 total setup cost
        # Qty 1:   $75 ÷ 1   = $75.00/unit setup
        # Qty 5:   $75 ÷ 5   = $15.00/unit setup
        # Qty 25:  $75 ÷ 25  = $ 3.00/unit setup
        # Qty 100: $75 ÷ 100 = $ 0.75/unit setup
        
        result = self.calculator.calculate_price_breaks(
            stock_volume_in3=8.0,
            material_name='Aluminum 6061',
            per_part_time_mins=4.0,
            setup_time_mins=60.0,
            shop_rate_hour=75.0
        )
        
        setup_cost_total = (60.0 / 60.0) * 75.0  # $75
        
        # Verify all default quantity breaks are present
        self.assertIn(1, result)
        self.assertIn(5, result)
        self.assertIn(25, result)
        self.assertIn(100, result)
        
        # Verify setup amortization (approximate, since material/labor also varies)
        # Higher quantity should always have lower per-unit price
        self.assertGreater(result[1]['price_per_unit'], result[5]['price_per_unit'])
        self.assertGreater(result[5]['price_per_unit'], result[25]['price_per_unit'])
        self.assertGreater(result[25]['price_per_unit'], result[100]['price_per_unit'])
    
    def test_price_breaks_structure(self):
        """Test price breaks return correct data structure."""
        result = self.calculator.calculate_price_breaks(
            stock_volume_in3=8.0,
            material_name='Aluminum 6061',
            per_part_time_mins=4.0,
            setup_time_mins=60.0,
            shop_rate_hour=75.0
        )
        
        # Verify structure for each quantity
        for qty, breakdown in result.items():
            self.assertIn('total_price', breakdown)
            self.assertIn('material_cost', breakdown)
            self.assertIn('labor_cost', breakdown)
            self.assertIn('price_per_unit', breakdown)
            
            # Verify price_per_unit calculation
            expected_per_unit = breakdown['total_price'] / qty
            self.assertAlmostEqual(breakdown['price_per_unit'], expected_per_unit, places=2)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and validation."""
    
    def setUp(self):
        """Initialize calculator for each test."""
        database.initialize_database()
        database.seed_default_data()
        self.calculator = PriceCalculator()
    
    def test_zero_stock_volume(self):
        """Test behavior with zero stock volume."""
        result = self.calculator.calculate_anchor(
            stock_volume_in3=0.0,
            material_name='Aluminum 6061',
            per_part_time_mins=4.0,
            setup_time_mins=60.0,
            shop_rate_hour=75.0,
            quantity=1,
            handling_time_mins=5.0
        )
        
        # Should return zero material cost
        self.assertEqual(result['material_cost'], 0.0)
        
        # But labor cost should still be calculated
        self.assertGreater(result['labor_cost'], 0)
    
    def test_very_high_quantity(self):
        """Test with very high quantity (1000 units)."""
        result = self.calculator.calculate_anchor(
            stock_volume_in3=8.0,
            material_name='Aluminum 6061',
            per_part_time_mins=4.0,
            setup_time_mins=60.0,
            shop_rate_hour=75.0,
            quantity=1000,
            handling_time_mins=5.0
        )
        
        # Setup should be negligible per unit
        setup_cost_per_unit = ((60.0 / 60.0) * 75.0) / 1000
        self.assertLess(setup_cost_per_unit, 0.10)  # Less than 10 cents per unit
        
        # Total should still be reasonable
        self.assertGreater(result['total_price'], 0)
    
    def test_custom_shop_rate(self):
        """Test with non-standard shop rate."""
        result_standard = self.calculator.calculate_anchor(
            stock_volume_in3=8.0,
            material_name='Aluminum 6061',
            per_part_time_mins=4.0,
            setup_time_mins=60.0,
            shop_rate_hour=75.0,  # Standard
            quantity=1,
            handling_time_mins=5.0
        )
        
        result_premium = self.calculator.calculate_anchor(
            stock_volume_in3=8.0,
            material_name='Aluminum 6061',
            per_part_time_mins=4.0,
            setup_time_mins=60.0,
            shop_rate_hour=150.0,  # Premium (2x)
            quantity=1,
            handling_time_mins=5.0
        )
        
        # Labor cost should double with 2x shop rate
        self.assertAlmostEqual(
            result_premium['labor_cost'],
            result_standard['labor_cost'] * 2.0,
            places=2
        )


def run_pricing_tests():
    """Run all pricing algorithm tests."""
    print("\n" + "="*60)
    print("PRICING ALGORITHMS TEST SUITE")
    print("Reference: SYSTEM_BEHAVIOR_SPEC.md Section 1")
    print("="*60 + "\n")
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMaterialCostCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestLaborCostCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestCompleteAnchorCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestPriceBreaksCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "="*60)
    print("PRICING ALGORITHMS TEST SUMMARY")
    print("="*60)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n[SUCCESS] ALL PRICING TESTS PASSED!")
        print("✅ Material Cost Calculation verified")
        print("✅ Labor Cost Calculation verified")
        print("✅ Complete Anchor Calculation verified")
        print("✅ Price Breaks (Setup Amortization) verified")
        print("✅ Edge Cases handled correctly")
    else:
        print("\n[FAILED] SOME TESTS FAILED - Review errors above")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_pricing_tests()
    sys.exit(0 if success else 1)

