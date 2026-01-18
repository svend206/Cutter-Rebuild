---
doc_id: guild_allowed_questions_and_exhaust_map
doc_type: constitution
status: locked
version: 1.1
date: 2026-01-18
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources:
  - constitution/guild/GUILD_CONSTITUTION.md
conflicts_with: []
tags: [guild, exhaust, questions]
---

# Guild Allowed Questions & Ops Exhaust Map (Authoritative)

This document defines:
1. The **questions the Guild is constitutionally allowed to answer**
2. The **questions the Guild must never answer**
3. The **Ops exhaust required** to support each allowed question

This file is binding. It is designed to:
- Prevent future drift
- Constrain engineering and product decisions
- Preserve the Ops–Guild firewall

---

## 1. Guild Purpose
See `constitution/guild/GUILD_CONSTITUTION.md`.

---

## 2. Allowed Question Classes (What the Guild MAY Answer)

### 2.1 Capacity & Lead Time Reality
**Guild may answer:**
- What lead times are shops quoting in a region?
- How do quoted lead times compare to actual delivery?
- How does lead time change under demand pressure?
- How volatile are delivery outcomes by region or geometry class?

**Value:**
- Shops gain context about market stress
- API buyers gain capacity-pressure signals

---

### 2.2 Negotiated Material Pricing (Actuals, Not Lists)
**Guild may answer:**
- What shops actually paid for material (by category, region, time)?
- How far actual prices deviate from assumed or list prices?
- How quickly material price changes propagate into quotes?

**Important:**
- These are **actual paid prices**, not vendor list prices
- No supplier identification

---

### 2.3 Geometry-Indexed Price Distributions
**Guild may answer:**
- How often a geometry class is quoted
- Observed price ranges for that geometry
- Distribution overlap between won and lost quotes

**Not allowed:**
- Correct prices
- Recommended prices

---

### 2.4 Buyer Behavior & Decision Friction
**Guild may answer:**
- Time-to-decision after quote
- Frequency of silent losses vs explicit losses
- Rate of late customer reversals

**Insight:**
Reveals buyer-side behavior patterns without exposing buyers

---

### 2.5 Quote Effort vs Outcome
**Guild may answer:**
- How much effort is typically invested in quotes of different classes
- Whether increased effort correlates with better outcomes

**Note:**
Effort signals must be coarse (time buckets, revision counts)

---

### 2.6 Execution Variance & Risk
**Guild may answer:**
- Quoted vs actual runtime variance
- Promised vs delivered variance
- Where execution risk is highest

---

### 2.7 Market Temperature (Non-Prescriptive)
**Guild may answer:**
- Quote volume acceleration or deceleration
- Lead time stretch over rolling windows
- Shifts in dominant loss reasons

**Guild must not answer:**
- Whether shops should raise or lower prices

---

### 2.8 Data Quality & Confidence
**Guild may answer:**
- Completeness rates of closed-loop data
- Revision frequency
- Confidence intervals on all aggregates

---

### 2.9 Absence & Negative Space
**Guild may answer:**
- Where data is systematically missing
- Where reality cannot be reliably inferred

Honest ignorance is first-class output.

---

## 3. Forbidden Question Classes (What the Guild MUST NOT Answer)
The Guild must never:
- Recommend prices, lead times, or effort levels
- Rank or score shops
- Predict win probability
- Suggest how hard to pursue a job
- Compare one shop to another
- Act as neutral arbiter of "correctness"

---

## 4. Ops Exhaust → Guild Signal Mapping (Core)

### 4.1 Capacity & Lead Time
**Required Ops exhaust:**
- quoted_lead_time
- promised_delivery_date
- actual_ship_date
- region
- timestamp

---

### 4.2 Negotiated Material Pricing
**Required Ops exhaust:**
- material_category (normalized)
- assumed_material_cost (if used)
- actual_material_cost
- region
- timestamp

**Explicit exclusion:**
- Vendor identity
- Contract terms

---

### 4.3 Geometry Indexing
**Required Ops exhaust:**
- genesis_hash
- coarse geometry class features
- quote outcome

---

### 4.4 Buyer Behavior
**Required Ops exhaust:**
- quote_created_at
- outcome_recorded_at
- loss_reason (if known)
- reopen_events

---

### 4.5 Quote Effort
**Required Ops exhaust:**
- quoting_time_bucket
- revision_count
- engineering_touch_flag

---

### 4.6 Execution Variance
**Required Ops exhaust:**
- quoted_runtime
- actual_runtime
- deviations (if recorded)

---

## 5. Boundary Reminder (Non-Negotiable)
- Ops captures exhaust
- Ops gates export eligibility
- Guild computes aggregates and economics
- No Guild intelligence flows back into Ops

If a feature makes Ops behaviorally smarter, it is invalid.

---

## 6. Status
This document is **LOCKED**.
Changes require explicit owner approval and constitutional review.
