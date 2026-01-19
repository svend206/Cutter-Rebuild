---
doc_id: archive_docs_refactor_plan
doc_type: archive
status: archived
version: 1.0
date: 2026-01-18
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [archive, legacy]
---

# Documentation Refactor Plan - Context Window Optimization
**Date:** January 3, 2026  
**Analysis By:** Claude (Cursor AI)  
**Method:** Comprehensive audit of all 14 Docs files  
**Goal:** Minimize token load while preserving all critical information

---

## Executive Summary

Your documentation is **architecturally sound** but suffers from **high redundancy** (30-40% duplicate concepts) and **structural inefficiency** (information scattered across 14 files). Current estimated token load: **~65,000 tokens** for full doc set.

**Proposed refactor:** Consolidate to **7 core documents** (~35,000 tokens, 46% reduction) by:
1. Merging implementation logs into master docs
2. Creating a unified "System Behavior" specification
3. Establishing clear document hierarchy

**Result:** Longer AI runway, faster context loading, easier maintenance.

---

## Part 1: Current State Analysis

### Document Inventory (14 Files)

| File | Lines | Est. Tokens | Type | Priority |
|------|-------|-------------|------|----------|
| `database_schema.md` | 517 | 4,800 | **CORE** | Critical |
| `technical_spec.md` | 405 | 4,200 | **CORE** | Critical |
| `anchor_price_specification.md` | 887 | 8,500 | **CORE** | Critical |
| `project_charter.md` | 206 | 2,300 | **CORE** | High |
| `feature_roadmap.md` | 266 | 2,800 | **CORE** | High |
| `UI DESIGN CONSTRAINTS.md` | 294 | 2,500 | **CORE** | High |
| `AI Workflow Protocol.md` | 241 | 2,600 | **META** | High |
| `RFQ_FIRST_IMPLEMENTATION.md` | 270 | 2,800 | **IMPL** | Medium |
| `PARAMETRIC_CONFIGURATOR.md` | 447 | 4,200 | **IMPL** | Medium |
| `dashboard_cockpit_specification.md` | 338 | 3,400 | **DEFER** | Low |
| `UI_FLOW_SCHEMATIC.md` | 687 | 7,200 | **VISUAL** | Medium |
| `GENESIS_HASH_PATTERN_MATCHING.md` | 382 | 3,800 | **IMPL** | Medium |
| `COMPLEXITY_REMOVAL_RATIONALE.md` | 218 | 2,100 | **DECISION** | Medium |
| `PHASE_5_DOCUMENTATION_UPDATE.md` | 207 | 2,000 | **LOG** | Low |

**Total:** 5,365 lines, ~65,200 tokens

---

## Part 2: Redundancy Analysis

### High-Redundancy Concepts (30-50% duplication)

#### 1. **Genesis Hash** (80 mentions across 9 files)
**Current spread:**
- `technical_spec.md` - Definition + philosophy (15 mentions)
- `GENESIS_HASH_PATTERN_MATCHING_COMPLETE.md` - Implementation details (34 mentions)
- `database_schema.md` - Schema definition (5 mentions)
- `anchor_price_specification.md` - Usage in pricing (5 mentions)
- `project_charter.md` - Guild network context (6 mentions)

**Problem:** Core concept explained 5 different ways in 5 documents.

**Solution:** Consolidate into `technical_spec.md` Section 9 "The Genesis Hash Standard" (already exists but incomplete). Delete dedicated implementation doc after merge.

---

#### 2. **O-Score / Autonomy Score** (70 mentions across 9 files)
**Current spread:**
- `anchor_price_specification.md` - Deep dive with formulas (40 mentions)
- `project_charter.md` - Business value proposition (9 mentions)
- `dashboard_cockpit_specification.md` - Visualization concepts (4 mentions)
- `technical_spec.md` - Algorithm definition (4 mentions)

**Problem:** Same formulas and philosophy repeated in 4 places.

**Solution:** Create single authoritative section in `technical_spec.md` Section 6.2. Reference from other docs with single-line pointers.

---

#### 3. **Pattern Matching / Ted View** (61 mentions across 10 files)
**Current spread:**
- `GENESIS_HASH_PATTERN_MATCHING_COMPLETE.md` - Testing guide (20 mentions)
- `RFQ_FIRST_IMPLEMENTATION.md` - User workflow (5 mentions)
- `technical_spec.md` - Algorithm specs (1 mention - incomplete)
- `UI_FLOW_SCHEMATIC.md` - UI integration (9 mentions)
- `PHASE_5_DOCUMENTATION_UPDATE.md` - Change log (7 mentions)

**Problem:** Algorithm scattered across implementation logs instead of centralized spec.

**Solution:** Consolidate 5 algorithms into `technical_spec.md` Section 6.4 (expand existing stub). Archive implementation logs.

---

#### 4. **Price Stack / Glass Box / Variance** (100 mentions across 12 files)
**Current spread:**
- `anchor_price_specification.md` - Complete specification (37 mentions)
- `UI_FLOW_SCHEMATIC.md` - Visual diagrams (18 mentions)
- `COMPLEXITY_REMOVAL_RATIONALE.md` - Philosophy (14 mentions)
- `technical_spec.md` - Algorithm (10 mentions)
- `project_charter.md` - Business context (10 mentions)

**Problem:** Core pricing logic explained in 5 documents with overlapping information.

**Solution:** `anchor_price_specification.md` is already canonical. Add single-line references in other docs: "See `anchor_price_specification.md` Section X for complete formula."

---

### Medium-Redundancy Concepts (15-30% duplication)

#### 5. **RFQ-First Workflow**
- Explained in `RFQ_FIRST_IMPLEMENTATION.md` (implementation guide)
- Explained in `UI_FLOW_SCHEMATIC.md` (Phase 5 section)
- Explained in `anchor_price_specification.md` (Section 16)
- Explained in `PHASE_5_DOCUMENTATION_UPDATE.md` (change log)

**Solution:** Keep `RFQ_FIRST_IMPLEMENTATION.md` as standalone feature guide (good for onboarding). Remove redundant sections from UI_FLOW_SCHEMATIC (replace with reference). Archive `PHASE_5_DOCUMENTATION_UPDATE.md`.

---

#### 6. **Database Schema Updates**
- Phase 5 fields documented in `database_schema.md`
- Phase 5 fields re-documented in `RFQ_FIRST_IMPLEMENTATION.md`
- Phase 5 fields change log in `PHASE_5_DOCUMENTATION_UPDATE.md`

**Solution:** `database_schema.md` is source of truth. Remove duplicates from implementation guides (just reference the schema doc).

---

## Part 3: Structural Inefficiencies

### Problem 1: **Implementation Logs as Permanent Docs**

**Files that should be archived:**
- `PHASE_5_DOCUMENTATION_UPDATE.md` (change log, not spec)
- `GENESIS_HASH_PATTERN_MATCHING_COMPLETE.md` (testing checklist, not spec)

**Reason:** These are **session handoff documents** (per your AI Workflow Protocol Section 8), NOT canonical specifications. They served their purpose (continuity between sessions) but now create noise.

**Action:** Move to `Docs/_archive/implementation_logs/` folder.

---

### Problem 2: **Missing Unified "System Behavior" Document**

**Current state:** Algorithm definitions scattered across:
- `technical_spec.md` (partial)
- `anchor_price_specification.md` (pricing only)
- Individual feature guides (RFQ, Parametric, etc.)

**Gap:** No single document answers: "How does the system behave when X happens?"

**Proposal:** Create `Docs/SYSTEM_BEHAVIOR_SPEC.md` (NEW) that consolidates:
- All pricing algorithms (from `anchor_price_specification.md` Sections 13-16)
- Pattern matching algorithms (from scattered impl docs)
- O-Score calculation (from multiple sources)
- Gating logic (from UI flow docs)

**Result:** AI can load ONE file to understand all behavioral rules.

---

### Problem 3: **Visual Diagrams Embedded in Text**

**Issue:** `UI_FLOW_SCHEMATIC.md` is 687 lines, mostly ASCII art diagrams that consume tokens but provide limited semantic value to AI.

**Example:**
```
╔═══════════════════════════════════════════════════════════════╗
║  SECTION 1: CONTEXT (The "Who")                              ║
║  Container ID: quote-metadata                                 ║
... (50 more lines of box drawing)
```

**AI Reality:** Doesn't "see" diagrams. Extracts text, but box characters waste tokens.

**Solution:** 
- Keep high-level ASCII flow (first 100 lines)
- Replace detailed box diagrams with structured lists:
  ```
  **Context Section:**
  - Customer Input (ID: customer-input, Type: Autocomplete)
  - Contact Input (ID: contact-input, Disabled until customer selected)
  ```
- Move detailed UI layout to separate `UI_LAYOUT_REFERENCE.md` (load only when doing UI work)

---

### Problem 4: **Deferred Feature Specification Loaded Always**

**File:** `dashboard_cockpit_specification.md` (338 lines)

**Status:** Marked as `[DEFERRED - Implement After Node 2/3]` (Phase 7, months away)

**Problem:** Loads into context window on every session even though it's not actionable yet.

**Solution:** Move to `Docs/_future/dashboard_cockpit_specification.md`. Add pointer in `feature_roadmap.md`: "Phase 7 specs in `_future/` folder."

---

## Part 4: Proposed Document Structure

### NEW Hierarchy (7 Core + 3 Reference)

#### **TIER 1: Constitutional Documents** (Load Always)
1. **`project_charter.md`** - Vision, business model, Guild network (KEEP AS-IS)
2. **`technical_spec.md`** - Architecture, Three Nodes, PWA strategy
   - **EXPAND:** Absorb Genesis Hash details, O-Score details, Pattern Matching algorithms
   - **NEW SECTIONS:**
     - 6.5 Genesis Hash Deep Dive (from `technical_spec.md` Section 9 + impl docs)
     - 6.6 O-Score Calculation (consolidate from multiple sources)
     - 10. Testing Strategy (reference `AI Workflow Protocol.md` Section 5)
3. **`database_schema.md`** - Source of truth for all tables (KEEP AS-IS, it's perfect)

**Result:** Load these 3 files to understand the entire system architecture.

---

#### **TIER 2: Operational Specifications** (Load for Active Development)
4. **`SYSTEM_BEHAVIOR_SPEC.md`** (NEW - Consolidate scattered algorithms)
   - Pricing Algorithms (from `anchor_price_specification.md`)
   - Pattern Matching (5 algorithms with thresholds)
   - O-Score Convergence Logic
   - Gating Rules (RFQ-First, etc.)
   - Validation Rules (Part > Stock, etc.)
   
5. **`UI_DESIGN_SYSTEM.md`** (RENAME from `UI DESIGN CONSTRAINTS.md`)
   - Keep existing constraints (perfect as-is)
   - Add Section 16: Component Catalog (consolidated from UI_FLOW_SCHEMATIC)
   - Add Section 17: State Management Rules

6. **`feature_roadmap.md`** - Phase tracking, completion status (KEEP AS-IS)

7. **`AI Workflow Protocol.md`** - Agent behavior rules (KEEP AS-IS, excellent)

**Result:** Load based on task type (backend = #4, frontend = #5, planning = #6, meta = #7).

---

#### **TIER 3: Feature Deep-Dives** (Load Only When Working on Specific Feature)
8. **`RFQ_FIRST_IMPLEMENTATION.md`** - Complete feature guide (KEEP)
9. **`PARAMETRIC_CONFIGURATOR.md`** - Shape configurator details (KEEP)
10. **`COMPLEXITY_REMOVAL_RATIONALE.md`** - Architectural decision (KEEP - good ADR pattern)

**Result:** Load only when modifying that specific feature.

---

### Files to ARCHIVE (Move to `Docs/_archive/`)
- `PHASE_5_DOCUMENTATION_UPDATE.md` - Change log (served its purpose)
- `GENESIS_HASH_PATTERN_MATCHING_COMPLETE.md` - Testing checklist (merge into `SYSTEM_BEHAVIOR_SPEC.md` as appendix, then archive)
- `anchor_price_specification.md` - **CONTROVERSIAL:** This 887-line doc should be split:
  - Sections 1-12: Core pricing formulas → Move to `SYSTEM_BEHAVIOR_SPEC.md`
  - Sections 13-16: Advanced O-Score & Learning → Move to `technical_spec.md` Section 6
  - Keep as reference initially, mark as `[DEPRECATED - See SYSTEM_BEHAVIOR_SPEC.md]`

### Files to DEFER (Move to `Docs/_future/`)
- `dashboard_cockpit_specification.md` - Phase 7, not actionable yet

---

## Part 5: Token Load Comparison

### BEFORE Refactor
```
Constitutional: 3 files, ~11,300 tokens
Operational: 7 files, ~32,900 tokens (HIGH REDUNDANCY)
Implementation: 4 files, ~13,000 tokens (OVERLAP)
Deferred: 1 file, ~3,400 tokens (UNNECESSARY LOAD)
Meta: 1 file, ~2,600 tokens
───────────────────────────────────────
TOTAL: 14 files, ~65,200 tokens
```

### AFTER Refactor
```
Constitutional: 3 files, ~11,300 tokens (no change)
Operational: 4 files, ~18,500 tokens (consolidated, redundancy removed)
Feature Guides: 3 files, ~9,100 tokens (targeted loading)
Meta: 1 file, ~2,600 tokens (no change)
───────────────────────────────────────
TOTAL LOADED: 7-11 files, ~35,000-41,500 tokens (depending on task)

Archived (not loaded): 3 files, ~8,100 tokens
Deferred (not loaded): 1 file, ~3,400 tokens
```

**Token Savings:** 24,000-30,000 tokens (37-46% reduction)  
**Runway Extension:** 37-46% longer sessions before context exhaustion

---

## Part 6: Migration Strategy (Lossless)

### Phase 1: Create New Documents (No Deletion)
1. Create `Docs/SYSTEM_BEHAVIOR_SPEC.md` (NEW)
2. Consolidate pricing algorithms, pattern matching, O-Score
3. Add cross-references to source documents

### Phase 2: Archive Implementation Logs
1. Create `Docs/_archive/implementation_logs/` folder
2. Move `PHASE_5_DOCUMENTATION_UPDATE.md`
3. Move `GENESIS_HASH_PATTERN_MATCHING_COMPLETE.md`
4. Add `README.md` in archive explaining purpose

### Phase 3: Defer Future Specs
1. Create `Docs/_future/` folder
2. Move `dashboard_cockpit_specification.md`
3. Add pointer in `feature_roadmap.md` Phase 7 section

### Phase 4: Mark Redundant Sections
1. In `UI_FLOW_SCHEMATIC.md`: Add note at top:
   ```
   **NOTE:** Detailed behavioral specs moved to `SYSTEM_BEHAVIOR_SPEC.md`.
   This doc now focuses on UI structure and component layout.
   ```
2. In `anchor_price_specification.md`: Add note:
   ```
   **DEPRECATED in favor of `SYSTEM_BEHAVIOR_SPEC.md`**
   This file remains as historical reference but is no longer canonical.
   ```

### Phase 5: Update Cross-References
1. Update `technical_spec.md` to reference new structure
2. Update `AI Workflow Protocol.md` Section 4 (Schema Contract) to point to new docs
3. Update `.cursorrules` if it references old doc names

---

## Part 7: Specific Refactor Actions

### Action 1: Create `SYSTEM_BEHAVIOR_SPEC.md`
**Content to consolidate:**
- From `anchor_price_specification.md`:
  - Section 2: File Mode Anchor Calculation
  - Section 3: Napkin Mode Anchor Calculation
  - Section 15: Phase 4 Refactor (Price Stack)
  - Section 16: Phase 5 Refactor (Complexity Removal)
- From `GENESIS_HASH_PATTERN_MATCHING_COMPLETE.md`:
  - Pattern Matching Logic (5 algorithms)
- From `technical_spec.md`:
  - Section 6.4: Pattern Matching (expand)
- From scattered sources:
  - O-Score formula (canonical version)
  - Gating logic (RFQ-First)

**New structure:**
```markdown
# System Behavior Specification

## 1. Pricing Algorithms
### 1.1 File Mode Pricing
### 1.2 Napkin Mode Pricing
### 1.3 Material Cost Calculation
### 1.4 Labor Cost Calculation

## 2. Price Stack (The Glass Box)
### 2.1 Layer 1: Physics Ledger
### 2.2 Layer 2: Variance Engine (Bidirectional)
### 2.3 Layer 3: Commercial Decision

## 3. Pattern Matching Algorithms
### 3.1 Genesis Hash Match (50% threshold)
### 3.2 Customer Pattern Match (60% threshold)
### 3.3 Material Pattern Match (70% threshold)
### 3.4 Quantity Pattern Match (50% threshold)
### 3.5 Lead Time Pattern Match (60% threshold)

## 4. O-Score Calculation
### 4.1 Variance Measurement
### 4.2 Confidence Blending (Historical vs. Physics)
### 4.3 Filtered O-Score (Business vs. Estimation Variance)

## 5. Gating & Validation Rules
### 5.1 RFQ-First Gating (Material + Quantity + Lead Time)
### 5.2 Part Volume vs. Stock Volume
### 5.3 Slider Sum Validation (100% rule)
### 5.4 Price Lock Behavior

## 6. State Transitions
### 6.1 Quote Creation Flow
### 6.2 Price Lock/Unlock Conditions
### 6.3 Mode Switching (File ↔ Napkin)
```

**Estimated length:** 450-500 lines (~5,000 tokens)

---

### Action 2: Expand `technical_spec.md`
**Add to Section 9 (The Genesis Hash Standard):**
- Collision detection strategy (from impl doc)
- Privacy preservation details (from impl doc)
- Guild network effect examples (from impl doc)

**Expand Section 6.2 (The Autonomy Score):**
- Complete O-Score formula (from `anchor_price_specification.md` Section 14)
- Benchmarking logic (Guild O-Score)
- Filtered O-Score (business vs. estimation variance)

**Result:** `technical_spec.md` becomes complete architecture reference (~550 lines, 6,000 tokens).

---

### Action 3: Slim Down `UI_FLOW_SCHEMATIC.md`
**Keep:**
- High-level 4-stage flow diagram (first 200 lines)
- State transition table
- Component relationship map

**Remove/Consolidate:**
- Detailed ASCII box diagrams (250 lines) → Replace with structured lists
- Redundant Phase 5 explanations → Single paragraph + reference to `SYSTEM_BEHAVIOR_SPEC.md`

**Result:** Reduce from 687 lines to ~350 lines (5,000 tokens → 2,500 tokens).

---

### Action 4: Archive Implementation Logs
**Move to `Docs/_archive/implementation_logs/`:**
1. `PHASE_5_DOCUMENTATION_UPDATE.md`
2. `GENESIS_HASH_PATTERN_MATCHING_COMPLETE.md`

**Create `Docs/_archive/README.md`:**
```markdown
# Implementation Logs Archive

This folder contains **session handoff documents** from previous AI sessions.
These served as continuity checkpoints but are NOT canonical specifications.

For current specifications, see:
- `../SYSTEM_BEHAVIOR_SPEC.md` - Algorithms
- `../technical_spec.md` - Architecture
- `../database_schema.md` - Data structures
```

---

## Part 8: Validation Checklist

After refactor, verify:
- [ ] All algorithm definitions exist in ONE canonical location
- [ ] Cross-references use format: "See `filename.md` Section X"
- [ ] No document > 600 lines (for AI readability)
- [ ] TIER 1 docs (Constitutional) load to < 12,000 tokens
- [ ] TIER 2 docs (Operational) load to < 20,000 tokens
- [ ] Archived docs not referenced in `.cursorrules`
- [ ] `AI Workflow Protocol.md` Section 4 updated with new doc names
- [ ] Token load test: Load TIER 1 + TIER 2 = < 35,000 tokens

---

## Part 9: Alternative: "Do Nothing" Risk Assessment

**If you DON'T refactor:**
- ❌ AI will continue loading 65k tokens of redundant info
- ❌ Context exhaustion in ~15-18k lines of code discussion
- ❌ Slower session startup (AI must parse 14 files)
- ❌ Higher hallucination risk (conflicting info across docs)
- ❌ Harder maintenance (update same concept in 5 places)

**If you DO refactor:**
- ✅ 46% longer runway (24k token savings)
- ✅ Faster context loading (fewer files)
- ✅ Single source of truth for each concept
- ✅ Easier onboarding (clear doc hierarchy)
- ✅ Future-proof (scales to Phase 7+)

---

## Part 10: My Recommendation

**HYBRID APPROACH:**

### Immediate (Session 1 - Next 30 min)
1. Create `Docs/SYSTEM_BEHAVIOR_SPEC.md` (consolidate scattered algorithms)
2. Archive `PHASE_5_DOCUMENTATION_UPDATE.md` and `GENESIS_HASH_PATTERN_MATCHING_COMPLETE.md`
3. Move `dashboard_cockpit_specification.md` to `_future/`

**Impact:** ~12k token savings (18% reduction), 2 hours work

---

### Near-Term (Session 2-3 - Next week)
4. Expand `technical_spec.md` Section 6 & 9 (O-Score + Genesis Hash deep dives)
5. Slim down `UI_FLOW_SCHEMATIC.md` (remove ASCII art, add structured lists)
6. Mark `anchor_price_specification.md` as `[REFERENCE ONLY]` with pointer to new docs

**Impact:** +18k token savings (total 30k saved, 46% reduction), 4 hours work

---

### Long-Term (Optional - Phase 6+)
7. Create `UI_LAYOUT_REFERENCE.md` for detailed component specs
8. Split `anchor_price_specification.md` fully (archive after extraction)
9. Establish ADR (Architectural Decision Record) pattern for future changes

**Impact:** Maintenance velocity, easier AI collaboration

---

## Part 11: Next Steps

**Option A: I Execute the Refactor (Cursor as Scribe)**
- I create `SYSTEM_BEHAVIOR_SPEC.md` using surgical edits
- I move files to archive folders
- I update cross-references
- You review diffs before finalizing

**Option B: You + Gemini Design, I Execute**
- You paste this plan into Gemini
- Gemini proposes doc structure for `SYSTEM_BEHAVIOR_SPEC.md`
- You approve
- I execute with surgical precision

**Option C: Hybrid (My Recommendation)**
- I create `SYSTEM_BEHAVIOR_SPEC.md` draft (I know your codebase)
- You review in Gemini for "second opinion"
- I finalize based on feedback
- Generates audit trail for future reference

---

## Conclusion

Your documentation is **solid** but **redundant**. The refactor I'm proposing is:
- **Lossless** (archive, don't delete)
- **Surgical** (consolidate, don't rewrite)
- **High ROI** (46% token reduction for ~6 hours work)

**Bottom Line:** Do the immediate refactor (Action Items 1-3) NOW to extend your runway. Defer near-term items (4-6) until you hit context limits again.

**Your call:** Would you like me to start with Action 1 (create `SYSTEM_BEHAVIOR_SPEC.md`) or do you want Gemini's second opinion first?

---

**Analysis Complete ✅**  
**Estimated Refactor Time:** 6 hours (spread across 3 sessions)  
**Token Savings:** 24-30k tokens (37-46%)  
**Runway Extension:** 37-46% longer AI sessions

