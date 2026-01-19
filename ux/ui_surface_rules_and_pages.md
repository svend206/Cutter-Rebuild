---
doc_id: ui_surface_rules_and_pages
doc_type: spec
status: active
version: 1.3
date: 2026-01-18
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources:
  - constitution/ux/UX_INDEX.md
conflicts_with: []
tags: [ux, spec, pages]
---

# UI Surface Rules and Pages

This file defines permitted UI pages and their purpose.
It must not add constitutional doctrine or override constitutional UX boundaries.

## Global Invariants (Apply to Every Page)

### Layer Separation (Non-Negotiable)
- **Ops UI** may show only what is necessary to perform work.
- **Cutter Ledger UI** may show raw operational exhaust only (no meaning, no salience).
- **State Ledger UI** may show recognition ceremony data only (no Ops signals).
- **Guild UI** is a separate product surface requiring an explicit context switch.

### Forbidden Everywhere
- Market intelligence in Ops/Cutter/State pages
- Credits, incentives, contribution quality scoring in Ops/Cutter/State pages
- Recommendations (“do X”, “charge Y”, “prioritize Z”) anywhere outside human-authored notes

### Canonical UX Tests (Apply Everywhere)
- If a user can say: **“The system showed us this, so…”** → **FAIL**
- If a user can infer market conditions or competition from an Ops/Cutter/State page → **FAIL**
- If a page uses color/score/ranking to imply importance → **FAIL**

### Ops UX Constraints (Binding)
- RFQ-first gating: economics must remain hidden/disabled until Material + Quantity + Lead Time are entered
- Glass-box pricing: show system anchor + physics snapshot + variance attribution + final price
- Price lock: if user edits final price, the system must not overwrite it until explicit reset or new quote
- Variance attribution must sum to 100% before save
- Estimating judgment is desktop-only; mobile is intake-only

### UI Design Constraints (Binding)
- One primary action per screen
- Calm, restrained typography and spacing
- No “importance” signaling via color/score outside explicit validation feedback
- Empty/loading/error states must be explicit and non-blaming

---

## Pages

### Page: Home (Ops)

**Purpose**  
Provide a simple entry point to continue work without implying state, health, or priority.

**Audience**  
Owner, operator acting on owner’s behalf.

**Must Show**
- Plain navigation to perform work (create quote, view quotes, execute jobs)
- Only local operational counts if unavoidable (e.g., “Draft quotes”) — no trends, no judgments

**Must Not Show**
- Any “health” summary
- Any trends, thresholds, dashboards
- Any Guild signals or hints (“competition”, “density”, “market rate”)

**Leakage Tests**
- Can a user infer performance/health from this page? → MUST BE NO  
- Does it suggest what to work on next? → MUST BE NO

**Cursor Build Prompt**  
Build a minimal Home page with plain navigation and zero evaluative cues. No metrics that imply importance.

---

### Page: Create Quote (Ops)

**Purpose**  
Produce a quote by entering required inputs and generating a price and lead time—without market influence or hidden guidance.

**Audience**  
Quoter / owner.

**Must Show**
- Part intake inputs (geometry upload or part reference)
- Material selection (category-level)
- Quantity
- Lead time
- Process routing inputs (domain meaning lives here)
- RFQ-first gating on economics (disabled until Material + Quantity + Lead Time are present)
- Glass-box “price stack”:
  - System anchor (pure physics) + physics snapshot
  - Variance attribution (human-entered; must sum to 100% before save)
  - Final price (user editable; price-lock applies)
- Explicit override entry (if user changes computed anchor)

**Must Not Show**
- Guild intelligence of any kind
- “Recommended” price
- “Competitive” indicators
- Rankings or confidence color
- Estimating judgment controls on mobile (mobile is intake-only)

**Leakage Tests**
- Could this change how hard someone tries based on external signals? → MUST BE NO  
- Does it imply the “right” answer? → MUST BE NO

**Cursor Build Prompt**  
Implement RFQ-first gating and glass-box price stack with variance-sum validation and price-lock behavior. Mobile is intake-only. No market context. Any “helper” must be local, descriptive, and clearly labeled as local.

---

### Page: Quote Detail (Ops)

**Purpose**  
Allow a user to inspect and revise a quote operationally.

**Audience**  
Quoter / owner.

**Must Show**
- Quote fields (price, lead time, routing, assumptions)
- Revision history (operational changes only)
- Outcome recording controls (won/lost/expired/deferred)
- Export eligibility status (eligible/not eligible) as a binary operational flag
- RFQ-first gating preserved (economics hidden until Material + Quantity + Lead Time are present)
- Glass-box price stack preserved (anchor snapshot, variance attribution, final price)
- Price lock state visible when final price is user-edited

**Must Not Show**
- Any inferred meaning about why it’s eligible/ineligible beyond the explicit rule
- Any contribution quality or “value to Guild”
- Any competitive density signals

**Leakage Tests**
- Could someone infer “this is valuable to export” beyond eligibility rules? → MUST BE NO  
- Does revision UI pressure the user to conform? → MUST BE NO

**Cursor Build Prompt**  
Build a quote detail page with RFQ-first gating, glass-box pricing preserved, price-lock visible, and strict binary export eligibility only.

---

### Page: Quotes List (Ops)

**Purpose**  
Find and open quotes for operational work.

**Audience**  
Quoter / owner.

**Must Show**
- Search/filter by operational attributes (date, material category, status)
- List rows with neutral fields (created date, status, quote_id, internal label)

**Must Not Show**
- Any ordering that implies importance or urgency
- Any performance indicators
- Any market intelligence

**Leakage Tests**
- Does sorting imply priority? → MUST BE NO (default sort can be chronological only)
- Does it show trend summaries? → MUST BE NO

**Cursor Build Prompt**  
Implement a plain searchable list. Chronological default. No highlights, no “attention,” no scoring.

---

### Page: Job Execution (Ops)

**Purpose**  
Track and complete work for won quotes until shipping.

**Audience**  
Operator / owner.

**Must Show**
- Job status fields needed for execution
- Required actuals capture (material cost, runtime, ship date)
- Deviations capture as raw reason text (if applicable)

**Must Not Show**
- Interpretive labels (“problem”, “good”, “bad”)
- Any dashboards or performance summaries
- Any Guild intelligence

**Leakage Tests**
- Can someone infer “how we’re doing” overall? → MUST BE NO  
- Does it highlight “problem jobs”? → MUST BE NO

**Cursor Build Prompt**  
Build an execution tracking page that captures required exhaust and completion milestones without scoring or flags beyond factual status.

---

### Page: Export to Guild (Ops Admin)

**Purpose**  
Perform explicit, manual export of eligible records to the Guild—without showing Guild economics or intelligence.

**Audience**  
Owner/admin only.

**Must Show**
- Eligible/not-eligible list (binary)
- Explicit export button requiring human action
- Export timestamp audit trail (requested_at, completed_at)
- Clear statement: “Export is manual and explicit”

**Must Not Show**
- Credits, incentives, contribution quality
- “Recommended exports”
- Any preview of Guild outputs
- Any market-wide context

**Leakage Tests**
- Does it create motivation loops (“export this to earn more”)? → MUST BE NO  
- Could it be mistaken as automatic? → MUST BE NO

**Cursor Build Prompt**  
Build an admin-only export screen with strict manual action and audit timestamps. No Guild value signals.

---

### Page: Cutter Ledger Viewer (Cutter Ledger UX)

**Purpose**  
Make demonstrated operational reality undeniable over time via raw events.

**Audience**  
Owner, auditor.

**Must Show**
- Raw events
- Timestamps
- Repetition
- Absence where applicable
- Provenance (who/what emitted)

**Must Not Show**
- Importance ranking
- Topic surfacing
- Aggregated “insights”
- Color coding, severity, thresholds, nudges

**Leakage Tests**
- Can user walk away with “so we should…” from the UI itself? → MUST BE NO  
- Does it highlight “most important events”? → MUST BE NO

**Cursor Build Prompt**  
Implement a raw event log viewer with filtering only by factual fields (time, type). No scoring, no highlighting, no summaries.

---

### Page: State Ledger Ceremony (State Ledger UX)

**Purpose**  
Record explicit human recognition of current state as a ceremonial act.

**Audience**  
Recognition owner.

**Must Show**
- Entity name
- Recognition owner (single)
- Cadence
- Last declared statement (verbatim)
- Time since last declaration
- Controls: reaffirm / reclassify with typed statement

**Must Not Show**
- Ops signals
- Cutter Ledger event lists
- Counts, trends, thresholds
- Dashboards, health indicators

**Leakage Tests**
- Is recognition being auto-suggested? → MUST BE NO  
- Could the user derive “what to say” from system metrics? → MUST BE NO

**Cursor Build Prompt**  
Build a ceremony page that requires typed declarations. No checkboxes. No automated suggestions. Show only recognition fields and time.

---

### Page: State Ledger History (State Ledger UX)

**Purpose**  
Review prior declarations as an immutable record of recognition over time.

**Audience**  
Owner, auditor.

**Must Show**
- Chronological list of declarations (verbatim)
- Timestamp and recognition owner at time of declaration
- Time-in-state between declarations

**Must Not Show**
- Any operational evidence or ledger events
- Any explanation, causality, or scoring

**Leakage Tests**
- Does it pull in Ops metrics? → MUST BE NO  
- Does it imply correctness? → MUST BE NO

**Cursor Build Prompt**  
Implement a plain immutable history list. No links to Ops metrics. No overlays. No interpretations.

---

### Page: Guild Portal Entry (Context Switch Gate)

**Purpose**  
Force an explicit context switch to the Guild product surface.

**Audience**  
Owner/admin (or shop-side user with Guild access).

**Must Show**
- Clear boundary statement: “You are leaving Cutter and entering the Guild.”
- Explicit consent action (“Enter Guild”)

**Must Not Show**
- Any Guild intelligence on the Cutter side of the boundary
- Any embedded widgets of Guild signals

**Leakage Tests**
- Is any Guild output visible before the switch? → MUST BE NO  
- Could a screenshot of Ops pages reveal market signals? → MUST BE NO

**Cursor Build Prompt**  
Build a hard boundary gate page requiring explicit action to enter Guild. Do not render any Guild data on this page.

---

### Page: Guild Intelligence (Guild Product Surface)

**Purpose**  
Provide shop-only market intelligence, including real-time signals keyed by genesis_hash, without prescriptions.

**Audience**  
Shop-side user.

**Must Show**
- Real-time or historical distributions/counts keyed by genesis_hash
- “No observations” explicit states where applicable
- Provenance discipline (what is observed vs unknown)

**Must Not Show**
- Prescriptive recommendations (“charge X”, “prioritize Y”)
- Shop identities (if prohibited by Guild rules)
- Anything rendered inside Ops/Cutter/State UX

**Leakage Tests**
- Does it tell the user what to do? → MUST BE NO  
- Does it leak into Ops? → MUST BE NO (must only exist after context switch)

**Cursor Build Prompt**  
Build Guild intelligence views that disclose market facts without prescriptions. Ensure strict separation from Cutter surfaces.

---

# Implementation Rule (Build Gate)

Cursor may implement a page ONLY if:
- It exists in this spec, and
- It passes “Must Not Show” + Leakage Tests without exceptions.

If a needed page is missing, stop and request an owner addition to this spec.
