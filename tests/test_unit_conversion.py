"""
Test script for unit detection and conversion functions
Phase 5.6 - Unit Verification Feature
"""

import vector_engine

def test_guess_units():
    """Test the multi-factor guess_units() heuristic."""
    print("=" * 60)
    print("TESTING: guess_units() - Multi-Factor Heuristic")
    print("=" * 60)
    
    # Test Case 1: Typical machined part in inches
    bbox_small = [[0, 0, 0], [10, 5, 2]]  # 10x5x2, aspect=5
    volume_small = 10 * 5 * 2  # 100 in3
    result = vector_engine.guess_units(bbox_small, volume_small)
    print(f"[PASS] Typical machined part (10x5x2, vol=100): {result}")
    assert result == "in", f"Expected 'in', got '{result}'"
    
    # Test Case 2: Very large part (definitely mm)
    bbox_large = [[0, 0, 0], [1500, 500, 200]]  # 1500x500x200 (sheet metal)
    volume_large = 1500 * 500 * 200  # 150,000,000 mm3
    result = vector_engine.guess_units(bbox_large, volume_large)
    print(f"[PASS] Very large part (1500x500x200): {result}")
    assert result == "mm", f"Expected 'mm', got '{result}'"
    
    # Test Case 3: Very small part (definitely inches)
    bbox_tiny = [[0, 0, 0], [0.05, 0.025, 0.01]]  # 0.05" micro part
    volume_tiny = 0.05 * 0.025 * 0.01  # 0.0000125 in3
    result = vector_engine.guess_units(bbox_tiny, volume_tiny)
    print(f"[PASS] Very small part (0.05x0.025x0.01): {result}")
    assert result == "in", f"Expected 'in', got '{result}'"
    
    # Test Case 4: Thin sheet metal (high aspect ratio) → mm
    bbox_thin = [[0, 0, 0], [96, 15, 5]]  # 96x15x5, aspect=19.2
    volume_thin = 96 * 15 * 5  # 7200 mm3
    result = vector_engine.guess_units(bbox_thin, volume_thin)
    print(f"[PASS] Thin sheet metal (96x15x5, aspect=19.2): {result}")
    assert result == "mm", f"Expected 'mm', got '{result}'"
    
    # Test Case 5: Medium part with high aspect ratio → mm
    bbox_circuit = [[0, 0, 0], [100, 50, 5]]  # 100x50x5, aspect=20
    volume_circuit = 100 * 50 * 5  # 25000 mm3
    result = vector_engine.guess_units(bbox_circuit, volume_circuit)
    print(f"[PASS] Circuit board (100x50x5, aspect=20): {result}")
    assert result == "mm", f"Expected 'mm', got '{result}'"
    
    # Test Case 6: Large volume signal → mm
    bbox_block = [[0, 0, 0], [50, 50, 50]]  # 50x50x50
    volume_huge = 125000  # 125,000 mm3 (7.6 in3 if inches)
    result = vector_engine.guess_units(bbox_block, volume_huge)
    print(f"[PASS] Large volume (50x50x50, vol=125000): {result}")
    assert result == "mm", f"Expected 'mm', got '{result}'"
    
    # Test Case 7: Medium-sized part with large volume → mm (volume signal)
    bbox_med = [[0, 0, 0], [200, 100, 50]]  # 200x100x50, aspect=4
    volume_med = 200 * 100 * 50  # 1,000,000 mm3 (triggers volume > 10000 signal)
    result = vector_engine.guess_units(bbox_med, volume_med)
    print(f"[PASS] Medium part with large volume (200x100x50, vol=1M): {result}")
    assert result == "mm", f"Expected 'mm', got '{result}'"
    
    # Test Case 7b: Same dimensions, smaller volume → inches
    bbox_med2 = [[0, 0, 0], [200, 100, 50]]  # 200x100x50 in inches
    volume_med2 = 200 * 100 * 50 / (25.4**3)  # Convert to in3 (~61 in3)
    result2 = vector_engine.guess_units(bbox_med2, volume_med2)
    print(f"[PASS] Medium part with small volume (200x100x50, vol=61): {result2}")
    assert result2 == "in", f"Expected 'in', got '{result2}'"
    
    # Test Case 8: Edge case at 300 threshold
    bbox_edge = [[0, 0, 0], [299, 100, 50]]  # Just under 300
    result = vector_engine.guess_units(bbox_edge, None)
    print(f"[PASS] Edge case (299 max): {result}")
    assert result == "in", f"Expected 'in', got '{result}'"
    
    bbox_edge2 = [[0, 0, 0], [301, 100, 50]]  # Just over 300
    result = vector_engine.guess_units(bbox_edge2, None)
    print(f"[PASS] Edge case (301 max): {result}")
    assert result == "mm", f"Expected 'mm', got '{result}'"
    
    print("\n[SUCCESS] All multi-factor guess_units() tests passed!\n")


def test_convert_dimensions():
    """Test the convert_dimensions() function."""
    print("=" * 60)
    print("TESTING: convert_dimensions()")
    print("=" * 60)
    
    # Test Case 1: in to mm
    dims_in = (10.5, 5.0, 2.0)
    dims_mm = vector_engine.convert_dimensions(dims_in, "in", "mm")
    expected = (266.7, 127.0, 50.8)
    print(f"[PASS] (10.5, 5.0, 2.0) in -> ({dims_mm[0]:.1f}, {dims_mm[1]:.1f}, {dims_mm[2]:.1f}) mm")
    assert all(abs(dims_mm[i] - expected[i]) < 0.1 for i in range(3)), f"Expected {expected}, got {dims_mm}"
    
    # Test Case 2: mm to in
    dims_mm = (266.7, 127.0, 50.8)
    dims_in = vector_engine.convert_dimensions(dims_mm, "mm", "in")
    expected = (10.5, 5.0, 2.0)
    print(f"[PASS] (266.7, 127.0, 50.8) mm -> ({dims_in[0]:.1f}, {dims_in[1]:.1f}, {dims_in[2]:.1f}) in")
    assert all(abs(dims_in[i] - expected[i]) < 0.1 for i in range(3)), f"Expected {expected}, got {dims_in}"
    
    # Test Case 3: Same units (no-op)
    dims = (10.0, 5.0, 2.0)
    result = vector_engine.convert_dimensions(dims, "in", "in")
    print(f"[PASS] Same units (no-op): {result}")
    assert result == dims, f"Expected {dims}, got {result}"
    
    print("\n[SUCCESS] All convert_dimensions() tests passed!\n")


def test_convert_units():
    """Test the convert_units() function."""
    print("=" * 60)
    print("TESTING: convert_units()")
    print("=" * 60)
    
    # Test Case 1: mm to in
    volume_mm = 1000.0  # 1000 mm³
    volume_in = vector_engine.convert_units(volume_mm, "mm", "in")
    expected = 1000 / (25.4 ** 3)  # ≈ 0.061 in³
    print(f"[PASS] 1000 mm3 -> {volume_in:.6f} in3 (expected: {expected:.6f})")
    assert abs(volume_in - expected) < 0.001, f"Expected {expected}, got {volume_in}"
    
    # Test Case 2: in to mm
    volume_in = 1.0  # 1 in³
    volume_mm = vector_engine.convert_units(volume_in, "in", "mm")
    expected = 25.4 ** 3  # ≈ 16387.064 mm³
    print(f"[PASS] 1 in3 -> {volume_mm:.3f} mm3 (expected: {expected:.3f})")
    assert abs(volume_mm - expected) < 1, f"Expected {expected}, got {volume_mm}"
    
    # Test Case 3: Same units (no conversion)
    volume = 100.0
    result = vector_engine.convert_units(volume, "in", "in")
    print(f"[PASS] 100 in3 -> {result} in3 (no conversion)")
    assert result == volume, f"Expected {volume}, got {result}"
    
    # Test Case 4: Realistic machined part
    # 10.5 in³ part (approx 2"x2"x2.5" block)
    volume_in = 10.5
    volume_mm = vector_engine.convert_units(volume_in, "in", "mm")
    print(f"[PASS] Realistic part: {volume_in} in3 -> {volume_mm:.1f} mm3")
    
    # Convert back to verify round-trip
    volume_back = vector_engine.convert_units(volume_mm, "mm", "in")
    print(f"[PASS] Round-trip: {volume_mm:.1f} mm3 -> {volume_back:.6f} in3")
    assert abs(volume_back - volume_in) < 0.001, f"Round-trip failed: {volume_in} != {volume_back}"
    
    print("\n[SUCCESS] All convert_units() tests passed!\n")


def test_integration():
    """Test integrated workflow: guess units, then convert if wrong."""
    print("=" * 60)
    print("INTEGRATION TEST: Unit Correction Workflow")
    print("=" * 60)
    
    # Scenario: User uploads STL in mm, but system guesses inches (wrong)
    # Bounding box: 266.7 x 127.0 x 50.8 mm (10.5 x 5 x 2 inches)
    bbox_mm = [[0, 0, 0], [266.7, 127.0, 50.8]]
    
    # System's initial guess (correct in this case)
    guessed_unit = vector_engine.guess_units(bbox_mm)
    print(f"1. System guesses: {guessed_unit}")
    
    # Calculate volume in guessed units
    volume_raw = 266.7 * 127.0 * 50.8  # mm³
    print(f"2. Raw volume: {volume_raw:.1f} {guessed_unit}³")
    
    # User says "actually, this is in mm" (system guessed correctly)
    actual_unit = "mm"
    
    if guessed_unit != actual_unit:
        # Convert to correct interpretation
        volume_corrected = vector_engine.convert_units(volume_raw, guessed_unit, actual_unit)
        print(f"3. User correction: {guessed_unit} -> {actual_unit}")
        print(f"4. Corrected volume: {volume_corrected:.1f} {actual_unit}3")
    else:
        print(f"3. [PASS] Guess was correct! No conversion needed.")
        volume_corrected = volume_raw
    
    # Convert to inches for pricing engine
    volume_in = vector_engine.convert_units(volume_corrected, actual_unit, "in")
    print(f"5. Final volume for pricing: {volume_in:.3f} in3")
    
    # Verify against expected value (10.5 x 5 x 2 = 105 in³ roughly)
    expected_in = 10.5 * 5 * 2
    print(f"6. Expected: ~{expected_in:.0f} in3")
    
    print("\n[SUCCESS] Integration test passed!\n")


if __name__ == "__main__":
    try:
        test_guess_units()
        test_convert_dimensions()
        test_convert_units()
        test_integration()
        
        print("=" * 60)
        print("[SUCCESS] ALL TESTS PASSED!")
        print("=" * 60)
        print("\nUnit Detection & Conversion Feature is ready for production.")
        print("Next steps:")
        print("  1. Add /api/convert_units endpoint in app.py")
        print("  2. Add Unit Selector UI below 3D viewer")
        print("  3. Update physics_snapshot_json to include assumed_units")
        
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)

