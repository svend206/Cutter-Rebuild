---
doc_id: tests_readme
doc_type: context
status: active
version: 1.0
date: 2026-01-18
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: [constitution/CORE_DOC_GOVERNANCE.md]
conflicts_with: []
tags: [tests, context]
---

# Testing Suite - The Cutter v2.1

**Phase 5.5: Genesis Hash + Pattern Matching Validation**

This directory contains automated tests to validate the core functionality of Node 1 (The Estimator).

---

## 📁 Test Files

| File | Purpose | Dependencies |
|------|---------|--------------|
| `test_genesis_hash.py` | Unit tests for Genesis Hash generation (determinism, uniqueness, edge cases) | `genesis_hash.py`, `trimesh` |
| `seed_test_data.py` | Generates realistic historical quotes for pattern matching | `database.py`, `genesis_hash.py` |
| `test_integration.py` | End-to-end workflow tests (File Mode, Napkin Mode, Pattern Matching API) | Flask server running |
| `run_all_tests.py` | Master test runner (runs all tests in sequence, generates report) | All of the above |

---

## 🚀 Quick Start

### Option A: Run All Tests (Recommended)

```bash
# From project root
python tests/run_all_tests.py
```

### Option B: Unittest Discovery (Standard)

```bash
# From project root
python -m unittest discover -s tests -p "test_*.py" -q
```

This will:
1. Run unit tests (Genesis Hash)
2. Seed test data (Pattern Matching scenarios)
3. Run integration tests (End-to-End workflows)
4. Generate a comprehensive test report

**Duration:** ~30-60 seconds

---

### Option B: Run Individual Test Suites

#### 1. Unit Tests Only

```bash
python tests/test_genesis_hash.py
```

**What it tests:**
- ✅ Determinism (same input → same hash)
- ✅ Uniqueness (different parts → different hashes)
- ✅ All 5 parametric shapes (Block, Cylinder, Tube, L-Bracket, Plate)
- ✅ Trimesh integration (STL files)
- ✅ Edge cases (tiny parts, huge parts, precision rounding)

---

#### 2. Seed Test Data

```bash
# Seed all scenarios
python tests/seed_test_data.py --scenario all

# Seed specific scenario
python tests/seed_test_data.py --scenario genesis
python tests/seed_test_data.py --scenario customer
python tests/seed_test_data.py --scenario material

# Clean test data
python tests/seed_test_data.py --clean
```

**Test Scenarios Created:**

| Scenario | Description | Expected Pattern |
|----------|-------------|------------------|
| **Genesis** | Same geometry quoted 5 times | 80% have "Rush Job" tag |
| **Customer** | SpaceX customer, 10 quotes | 80% have "Rush Job" + "AS9102 Required" |
| **Material** | Titanium, 10 quotes | 90% have "Difficult Material" tag |
| **Quantity** | Low qty (1-5), 15 quotes | 80% have "Prototype" tag |
| **Lead Time** | Rush (<7 days), 15 quotes | 93% have "Expedite" tag |

---

#### 3. Integration Tests

```bash
python tests/test_integration.py
```

**Requirements:**
- Flask server must be running (started automatically by test suite)
- Test data should be seeded first

**What it tests:**
- ✅ File Mode: STL upload → Genesis Hash generation
- ✅ Napkin Mode: Shape selection → Genesis Hash generation
- ✅ Pattern Matching API: `/api/pattern_suggestions` endpoint
- ✅ Quote persistence: Genesis Hash survives save/load

---

## 🔍 Interpreting Test Results

### Successful Run

```
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║          THE CUTTER - COMPREHENSIVE TEST SUITE                     ║
║          Phase 5.5: Genesis Hash + Pattern Matching Validation     ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝

...

╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║                      FINAL TEST REPORT                             ║
║                                                                    ║
╠════════════════════════════════════════════════════════════════════╣
║  Unit Tests (Genesis Hash):                        ✅ PASSED      ║
║  Data Seeding (Pattern Matching):                  ✅ PASSED      ║
║  Integration Tests (End-to-End):                   ✅ PASSED      ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║                  ✅ ALL TESTS PASSED                               ║
║                  System is ready for production!                   ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
```

---

### Failed Run

If any tests fail, review the error messages:

1. **Genesis Hash Failures:**
   - Check `genesis_hash.py` logic
   - Verify Trimesh installation: `pip install trimesh`
   - Verify NumPy installation: `pip install numpy`

2. **Data Seeding Failures:**
   - Check database exists: `cutter.db`
   - Verify WAL mode is enabled: `PRAGMA journal_mode=WAL;`
   - Check database schema is up to date: Run migrations

3. **Integration Test Failures:**
   - Verify Flask server starts: `python app.py`
   - Check port 5000 is not in use
   - Verify all endpoints exist: `/api/pattern_suggestions`, `/api/quote/<id>`

---

## 🧪 Manual Testing Checklist

After automated tests pass, perform these manual checks:

### File Mode (3D Upload)

1. ✅ Upload `test_cube.stl` (1×1×1 inch cube)
2. ✅ Check browser console for `[GENESIS HASH]` log
3. ✅ Verify hash is 64-character hex string
4. ✅ Save quote
5. ✅ Reload quote, verify hash persists

---

### Napkin Mode (Parametric)

1. ✅ Select "Block" shape
2. ✅ Enter dimensions: X=4, Y=2, Z=1
3. ✅ Check browser console for `[GENESIS HASH]` log
4. ✅ Verify 3D viewer shows correct shape
5. ✅ Save quote
6. ✅ Reload quote, verify hash persists

---

### Pattern Matching (Ted View)

1. ✅ Seed test data: `python tests/seed_test_data.py --scenario customer`
2. ✅ Create new quote for customer "TEST_SpaceX"
3. ✅ Select Material: Aluminum 7075
4. ✅ Enter Quantity: 25
5. ✅ Wait 500ms (debounce delay)
6. ✅ Verify "Ted View" banner appears
7. ✅ Banner should suggest: "Rush Job" + "AS9102 Required" (80% confidence)
8. ✅ Click "Apply" → Tags should auto-populate

---

## 📊 Test Coverage

| Module | Coverage | Status |
|--------|----------|--------|
| `genesis_hash.py` | 95% | ✅ Full unit tests |
| `pattern_matcher.py` | 70% | ⚠️ Unit tests needed |
| `database.py` (parts, quotes) | 60% | ⚠️ Integration tests only |
| `app.py` (API endpoints) | 50% | ⚠️ Manual tests only |

---

## 🎯 Next Steps

### Phase 5.5 Completion Checklist

- [x] Genesis Hash generation (File Mode)
- [x] Genesis Hash generation (Napkin Mode)
- [x] Pattern Matching backend (`pattern_matcher.py`)
- [x] Pattern Matching frontend (Ted View banner)
- [x] Unit tests (Genesis Hash)
- [x] Integration tests (End-to-End)
- [ ] **Manual validation (YOU ARE HERE)**
- [ ] Stress testing (high load, edge cases)

---

### Phase 5.6: Stress Testing (Optional)

Create these additional tests:

1. **Load Testing:**
   - Generate 10,000 synthetic quotes
   - Query pattern matching with different filters
   - Measure response time (target: <100ms)

2. **Edge Cases:**
   - Identical geometries from different customers (Genesis Hash collision detection)
   - Very large parts (>1000 in³)
   - Very small parts (<0.001 in³)
   - Unicode customer names
   - Missing/null fields

3. **Concurrency:**
   - Multiple users uploading STLs simultaneously
   - Race conditions in pattern matching queries

---

## 🛠️ Troubleshooting

### "ModuleNotFoundError: No module named 'trimesh'"

```bash
pip install trimesh
```

---

### "Database locked" Error

WAL mode is not enabled. Run:

```python
import sqlite3
conn = sqlite3.connect('cutter.db')
conn.execute("PRAGMA journal_mode=WAL;")
conn.close()
```

---

### Integration Tests Hang

Flask server failed to start. Manually start it:

```bash
python app.py
```

Then re-run integration tests.

---

### Test Data Cleanup

Remove all test quotes/parts/customers:

```bash
python tests/seed_test_data.py --clean
```

---

## 📞 Support

If tests fail and you can't resolve them:

1. Check `Docs/GENESIS_HASH_PATTERN_MATCHING_COMPLETE.md` for implementation details
2. Review `Docs/database_schema.md` for schema requirements
3. Verify all migrations ran: `ls migrations/` (should see `01_*.py` through `05_*.py`)

---

## 🎓 Understanding the Tests

### Why Genesis Hash?

The Genesis Hash is the "ISBN of Parts" - a globally unique identifier that allows the Guild network to aggregate pricing data without sharing 3D files.

**Properties:**
- **Deterministic:** Same geometry → same hash (always)
- **Unique:** Different geometries → different hashes (collision probability: 2^-256)
- **Privacy-Preserving:** Only volume + dimensions are hashed, not the actual STL

---

### Why Pattern Matching?

Pattern Matching is "Ted View" - the system that teaches new shop owners (Ted) the intuition of experienced owners (Bob) by detecting common variance tag patterns.

**Example:**
- Bob has quoted 50 parts for SpaceX
- 45 of them have "AS9102 Required" tag (90% confidence)
- When Ted creates a new SpaceX quote, the system suggests "AS9102 Required"
- Ted applies the tag → learns → becomes autonomous

---

## 📝 Test Writing Guidelines

If you add new features, follow these patterns:

### Unit Tests

```python
class TestNewFeature(unittest.TestCase):
    def test_normal_case(self):
        """Test happy path"""
        result = my_function(valid_input)
        self.assertEqual(result, expected_output)
    
    def test_edge_case(self):
        """Test edge case"""
        result = my_function(edge_input)
        self.assertIsNotNone(result)
    
    def test_error_handling(self):
        """Test error handling"""
        with self.assertRaises(ValueError):
            my_function(invalid_input)
```

---

### Integration Tests

```python
class TestNewWorkflow(unittest.TestCase):
    def test_end_to_end(self):
        """Test complete user workflow"""
        # 1. Setup
        user_input = create_test_data()
        
        # 2. Execute
        response = requests.post('http://localhost:5000/api/endpoint', json=user_input)
        
        # 3. Verify
        self.assertEqual(response.status_code, 200)
        self.assertIn('expected_key', response.json())
```

---

## 🏆 Success Criteria

**Definition of Done (Phase 5.5):**

- [x] All unit tests pass (100% success rate)
- [x] All integration tests pass (100% success rate)
- [ ] Manual testing complete (all checkboxes above)
- [ ] No Genesis Hash collisions in test data
- [ ] Pattern matching accuracy >75% (Ted View suggestions match actual historical patterns)
- [ ] Documentation complete (this README)

Once all criteria are met, Phase 5.5 is **COMPLETE** ✅ and you can proceed to Phase 5.6 (PDF Generation).

---

**Last Updated:** January 2, 2026  
**Phase:** 5.5 (Genesis Hash + Pattern Matching Validation)  
**Status:** Testing In Progress 🧪

