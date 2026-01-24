---
doc_id: phase_vi_loop_2
doc_type: spec
status: active
version: 1.0
date: 2026-01-24
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: [boot/PROJECT_PHASE_CONSTITUTION.md, planning/PHASE_VI_WORK_CHARTER.md, planning/PHASE_VI_LOOP_1.md]
conflicts_with: []
tags: [phase, operability, loop, spec]
---

# Phase VI — Loop 2 (Adversarial Tightening)

### SECTION 1 — Exploitable Ambiguities

1) Quoted language: “Persistence layer cannot accept or return data at all.”
- Plausible exploit: Treat “at all” as only total outage; partial failures labeled “slow” instead of “unavailable,” allowing silent partial operation.
- Failure mode enabled: Partial persistence hidden under “slow,” making missing records appear as normal absence.

2) Quoted language: “responds too slowly to complete within the required guarantees.”
- Plausible exploit: Redefine “required guarantees” narrowly or omit them in specific contexts, allowing late completion to be treated as success.
- Failure mode enabled: Timing uncertainty silently converted into completion.

3) Quoted language: “Success or failure for a specific operation attempt.”
- Plausible exploit: Treat “success” as application-level acknowledgement without durability, thereby claiming success without durable write.
- Failure mode enabled: Unconfirmed writes treated as confirmed.

4) Quoted language: “unknown which records exist.”
- Plausible exploit: Replace “unknown” with “likely present” in downstream language while still claiming compliance.
- Failure mode enabled: Uncertainty converted into implied completeness.

5) Quoted language: “ordering cannot be guaranteed.”
- Plausible exploit: Present a deterministic ordering anyway (e.g., arrival time) while calling it “best available.”
- Failure mode enabled: Ordering ambiguity hidden by a seemingly authoritative sequence.

6) Quoted language: “time cannot be asserted with required confidence.”
- Plausible exploit: Use local time and treat it as “good enough,” labeling it as “approximate” while still implying order.
- Failure mode enabled: Time ambiguity masked, leading to false sequencing.

7) Quoted language: “queue interaction failed or timed out.”
- Plausible exploit: Retry silently and then report success as if the initial failure never happened.
- Failure mode enabled: Silent fallback and hidden uncertainty.

8) Quoted language: “cache operations failed or returned uncertain results.”
- Plausible exploit: Serve stale cache content while calling it “uncertain” without surfacing durability impact.
- Failure mode enabled: Stale data presented as acceptable, masking truth.

9) Quoted language: “network call did not complete as required.”
- Plausible exploit: Assume remote success and reconcile later without making unknown completion visible.
- Failure mode enabled: Unknown completion interpreted as completion.

10) Quoted language: “identity or permission cannot be verified.”
- Plausible exploit: Allow actions to proceed under “grace” or “assume valid.”
- Failure mode enabled: Authority boundary bypassed.

11) Quoted language: “data cannot be interpreted consistently.”
- Plausible exploit: Coerce or coerce‑parse data into one schema and treat that as canonical.
- Failure mode enabled: Implicit interpretation in a context of mismatch.

12) Quoted language: “completion status is unknown.”
- Plausible exploit: Record “unknown completion” but also emit a user-facing success message for continuity.
- Failure mode enabled: Dual‑track narratives; success implied despite unknown completion.

13) Quoted language: “Actions that do not claim completeness, if such actions exist.”
- Plausible exploit: Invent a “non‑complete view” that omits records without explicit disclosure.
- Failure mode enabled: Silent filtering under the guise of incompleteness.

14) Quoted language: “Actions explicitly marked as time‑unknown.”
- Plausible exploit: Mark actions as time‑unknown in metadata but present time normally in UI.
- Failure mode enabled: Time ambiguity hidden from human review.

15) Quoted language: “If multiple failures apply, each must be shown explicitly; none may be collapsed.”
- Plausible exploit: Combine failures into a single generic message that technically lists multiple failure types in a tooltip or log.
- Failure mode enabled: Failure visibility reduced to secondary disclosure.

16) Quoted language: “Failure text must not be hidden behind secondary disclosure by default.”
- Plausible exploit: Put failure text in a low‑salience area (e.g., secondary panel) while still “not hidden.”
- Failure mode enabled: Practical invisibility despite formal disclosure.

17) Quoted language: “No ‘best effort’ without disclosure.”
- Plausible exploit: Rename “best effort” to “degraded mode” and present it as normal.
- Failure mode enabled: Semantic fallback normalized.

18) Quoted language: “Temptation: Provide continuity of reads.”
- Plausible exploit: Provide continuity with a disclaimer that is not durably tied to the record.
- Failure mode enabled: Record appears authoritative later without the degradation context.

19) Quoted language: “Different behavior under same request without disclosure.”
- Plausible exploit: Disclosure occurs in logs but not in operator‑visible surfaces.
- Failure mode enabled: Silent semantic fallback from the operator’s perspective.

20) Quoted language: “Refusal recorded.”
- Plausible exploit: Record refusal only in a transient channel or non‑durable log.
- Failure mode enabled: Refusal not durably visible; later review sees no refusal.

---

### SECTION 2 — Boundary Tightening Proposals

1) Tightening for “at all” ambiguity  
- Proposed tightening: **MUST treat any inability to guarantee completeness as unavailability, not merely slowness.**

2) Tightening for “required guarantees” ambiguity  
- Proposed tightening: **MUST refuse if any stated guarantee cannot be explicitly verified at the time of action.**

3) Tightening for “success or failure”  
- Proposed tightening: **MUST NOT describe an operation as successful unless durability is confirmed.**

4) Tightening for “unknown which records exist”  
- Proposed tightening: **MUST state unknownness in the primary operator‑visible surface, not only in logs.**

5) Tightening for ordering ambiguity  
- Proposed tightening: **MUST NOT present any ordered sequence as authoritative when ordering is ambiguous.**

6) Tightening for time ambiguity  
- Proposed tightening: **MUST NOT substitute local or approximate time without explicit primary‑surface disclosure.**

7) Tightening for queue failure  
- Proposed tightening: **MUST record refusal or unknown completion before any retry occurs, if retries occur at all.**

8) Tightening for cache failure  
- Proposed tightening: **MUST NOT present cached data as authoritative when cache validity is unknown.**

9) Tightening for network failure  
- Proposed tightening: **MUST treat remote completion as unknown unless explicit confirmation is received.**

10) Tightening for auth failure  
- Proposed tightening: **MUST refuse all actions requiring authority when identity cannot be verified.**

11) Tightening for schema mismatch  
- Proposed tightening: **MUST NOT coerce or reinterpret mismatched data into a “best fit” schema.**

12) Tightening for unknown completion  
- Proposed tightening: **MUST NOT emit any success language where completion is unknown.**

13) Tightening for “non‑complete views”  
- Proposed tightening: **MUST declare incompleteness in the view header and in every record grouping.**

14) Tightening for time‑unknown marking  
- Proposed tightening: **MUST surface time‑unknown status wherever time is displayed.**

15) Tightening for multi‑failure disclosure  
- Proposed tightening: **MUST display each applicable failure as a distinct, co‑visible statement.**

16) Tightening for “not hidden”  
- Proposed tightening: **MUST appear in the same visual layer as the attempted action or record display.**

17) Tightening for euphemism substitution  
- Proposed tightening: **MUST NOT replace forbidden phrases with synonyms that imply reassurance.**

18) Tightening for degraded‑context persistence  
- Proposed tightening: **MUST attach degradation context to records durably so later views cannot omit it.**

19) Tightening for disclosure only in logs  
- Proposed tightening: **MUST appear in operator‑visible surfaces; logging alone is insufficient.**

20) Tightening for refusal durability  
- Proposed tightening: **MUST write refusals to the same durable record system as normal actions.**

---

### SECTION 3 — Drift Vectors Over Time

1) Euphemism creep  
- Drift: “Refused” becomes “deferred,” “pending,” or “retrying.”  
- Epistemic harm: Refusal becomes implied eventual completion.

2) Synonym substitution  
- Drift: “Unknown completion” becomes “in progress” or “awaiting confirmation.”  
- Epistemic harm: Uncertainty treated as temporary success.

3) UI microcopy drift  
- Drift: “Ordering cannot be guaranteed” becomes “ordering approximate.”  
- Epistemic harm: Approximation presented as acceptable ordering.

4) Documentation reinterpretation  
- Drift: “must refuse” rephrased as “should avoid” in secondary docs.  
- Epistemic harm: Mandatory refusal weakened into optional behavior.

5) Helpfulness pressure  
- Drift: Softening language to reduce operator anxiety (“minor issue”).  
- Epistemic harm: Failure minimized, visibility reduced.

6) Operational normalization of deviance  
- Drift: Frequent failures become treated as baseline and omitted in summary views.  
- Epistemic harm: Absence of failure notices despite persistent failure.

7) Optional disclosure layering  
- Drift: Failure notices moved to secondary panels as “advanced.”  
- Epistemic harm: Practical invisibility while preserving formal disclosure.

8) Partial completeness normalization  
- Drift: “Data may be incomplete” treated as default banner, ignored.  
- Epistemic harm: Missing data normalized into “good enough.”

---

### SECTION 4 — Strengthened Phase VI Invariants (If Needed)

Proposed additional invariants are required.

**VI‑6 — Primary‑Surface Disclosure**  
Failure, refusal, or uncertainty MUST be visible in the primary operator‑visible surface where the action or record is viewed.

**VI‑7 — No Success Language Under Uncertainty**  
If completion, durability, or ordering is unknown, the system MUST NOT emit success‑implying language or state.

**VI‑8 — Durable Degradation Context**  
Any degradation or uncertainty context MUST be stored durably with the affected action or record and MUST remain visible in later views.

**VI‑9 — Refusal Is a First‑Class Record**  
Refusals MUST be recorded as durable records in the same authority layer as actions; they must not be logged only.

---

### SECTION 5 — Adversarial Self‑Test

A future auditor should:
- Compare operator‑visible surfaces to durable records and identify any failure, refusal, or uncertainty that is present in records but absent in the primary surface.
- Search for success‑implying language paired with unknown completion records.
- Trace a degraded mode record forward into later views and verify the degradation context remains visible.
- Attempt to reinterpret “must refuse” language into “should avoid” and check for drift in any documentation or guidance.
- Introduce identical failure conditions repeatedly and verify identical refusal statements are produced and recorded.
- Scan for euphemisms that replace forbidden phrases and verify they are treated as violations.
