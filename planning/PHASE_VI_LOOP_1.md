---
doc_id: phase_vi_loop_1
doc_type: spec
status: active
version: 1.0
date: 2026-01-24
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: [boot/PROJECT_PHASE_CONSTITUTION.md, planning/PHASE_VI_WORK_CHARTER.md]
conflicts_with: []
tags: [phase, operability, loop, spec]
---

# Phase VI — Loop 1 (Enumeration Only)

## SECTION 1 — Runtime Failure-Mode Catalog

### 1) Storage unavailable
- **What failed (descriptive)**: Persistence layer cannot accept or return data at all.
- **What the system can know**: An operation attempted to reach storage and did not complete successfully.
- **What the system cannot know**: Whether any intended write was durably recorded; whether any read would have succeeded.

### 2) Storage slow / stalled
- **What failed (descriptive)**: Persistence layer responds too slowly to complete within the required guarantees.
- **What the system can know**: A request exceeded the time window required for a guaranteed result.
- **What the system cannot know**: Whether the operation eventually completed; whether late completion preserved ordering.

### 3) Storage partial availability
- **What failed (descriptive)**: Some storage operations succeed while others fail within the same period.
- **What the system can know**: Success or failure for a specific operation attempt.
- **What the system cannot know**: Completeness of the dataset; whether missing writes occurred elsewhere.

### 4) Write path failure
- **What failed (descriptive)**: The pathway that accepts and persists writes does not complete a write request.
- **What the system can know**: A write attempt did not complete with a confirmed durable result.
- **What the system cannot know**: Whether the write partially applied; whether ordering relative to other writes was preserved.

### 5) Read path failure
- **What failed (descriptive)**: The pathway that retrieves records does not return requested data.
- **What the system can know**: A read attempt did not complete with a valid response.
- **What the system cannot know**: Whether requested records exist; whether returned data would have been complete.

### 6) Partial persistence
- **What failed (descriptive)**: Some records in a logical group are persisted while others are not.
- **What the system can know**: That at least one related write did not confirm durability.
- **What the system cannot know**: Which records are missing; whether the set is complete.

### 7) Ordering ambiguity
- **What failed (descriptive)**: The system cannot guarantee the ordering of related records.
- **What the system can know**: The ordering guarantee is not met for the affected set.
- **What the system cannot know**: The true sequence of events.

### 8) Clock / time-source ambiguity
- **What failed (descriptive)**: Time source is unavailable, inconsistent, or not trustworthy.
- **What the system can know**: Time cannot be asserted with required confidence.
- **What the system cannot know**: Accurate timestamps; correct duration or sequence derived from time.

### 9) Dependency failure — queue
- **What failed (descriptive)**: Message or job queue is unavailable, delayed, or inconsistent.
- **What the system can know**: A queue interaction failed or timed out.
- **What the system cannot know**: Whether queued work was accepted, processed, or lost.

### 10) Dependency failure — cache
- **What failed (descriptive)**: Cache layer is unavailable or returns inconsistent data.
- **What the system can know**: Cache operations failed or returned uncertain results.
- **What the system cannot know**: Freshness or correctness of cached data.

### 11) Dependency failure — network
- **What failed (descriptive)**: Network connectivity is absent, intermittent, or partitioned.
- **What the system can know**: A network call did not complete as required.
- **What the system cannot know**: Remote system state; whether the remote completed any action.

### 12) Dependency failure — auth/identity
- **What failed (descriptive)**: Authentication or authorization dependency is unavailable or inconsistent.
- **What the system can know**: Identity or permission cannot be verified.
- **What the system cannot know**: Whether a request should be permitted.

### 13) Dependency failure — clock
- **What failed (descriptive)**: External or authoritative clock source is unreachable or inconsistent.
- **What the system can know**: Time source cannot be validated.
- **What the system cannot know**: True time ordering or accurate timestamps.

### 14) Corrupted or invalid inputs
- **What failed (descriptive)**: Inputs are malformed, corrupted, or fail validation.
- **What the system can know**: The input did not meet required validity conditions.
- **What the system cannot know**: The intended content; whether a correct input would have been provided.

### 15) Schema / format mismatch between components
- **What failed (descriptive)**: Components disagree on record structure or format.
- **What the system can know**: Data cannot be interpreted consistently.
- **What the system cannot know**: Correct interpretation; whether data is complete or accurate.

### 16) Unknown state (“cannot know whether X occurred”)
- **What failed (descriptive)**: The system cannot determine whether an action or record was completed.
- **What the system can know**: The completion status is unknown.
- **What the system cannot know**: Whether the action occurred; whether a record was durably written.

---

## SECTION 2 — Deterministic Refusal Semantics

For each failure mode, refusal is required whenever guarantees cannot be met. The refusal is the same for the same failure condition every time.

### 1) Storage unavailable
- **Actions that MUST be refused**: Any action requiring durable write or authoritative read.
- **Actions that MAY proceed (if any)**: None when durability or authoritative read is required.
- **What is recorded about the refusal**: Refused action, dependency unavailable, time of refusal, uncertainty that no durability guarantee can be made.
- **How “unknown completion” is represented**: “Unknown completion” is recorded as a durable uncertainty record tied to the refused action.

### 2) Storage slow / stalled
- **MUST be refused**: Any action requiring timely durability or ordering guarantees.
- **MAY proceed**: None if timing guarantees are a requirement of the action.
- **Recorded about refusal**: Required timing guarantee not met; outcome unknown.
- **Unknown completion**: Explicitly recorded as unknown; no implied eventual completion.

### 3) Storage partial availability
- **MUST be refused**: Any action requiring completeness across a set of records.
- **MAY proceed**: Actions that do not claim completeness, if such actions exist.
- **Recorded about refusal**: Partial availability detected; completeness cannot be guaranteed.
- **Unknown completion**: Recorded for the subset that cannot be confirmed.

### 4) Write path failure
- **MUST be refused**: Any write that claims durable persistence.
- **MAY proceed**: None for durable writes.
- **Recorded about refusal**: Write not durably confirmed; refusal reason noted.
- **Unknown completion**: “Unknown completion” recorded for the attempted write.

### 5) Read path failure
- **MUST be refused**: Any read that claims authoritative completeness.
- **MAY proceed**: None for authoritative reads.
- **Recorded about refusal**: Read unavailable; completeness cannot be asserted.
- **Unknown completion**: “Unknown completion” recorded for the attempted read.

### 6) Partial persistence
- **MUST be refused**: Any action that would treat a set as complete.
- **MAY proceed**: Actions that declare incompleteness explicitly, if such actions exist.
- **Recorded about refusal**: Partial persistence; unknown which records exist.
- **Unknown completion**: Explicit uncertainty recorded for missing records.

### 7) Ordering ambiguity
- **MUST be refused**: Any action requiring deterministic ordering or sequence claims.
- **MAY proceed**: Actions that explicitly declare ordering is unknown.
- **Recorded about refusal**: Ordering cannot be guaranteed.
- **Unknown completion**: “Unknown completion” recorded for sequence-dependent actions.

### 8) Clock / time-source ambiguity
- **MUST be refused**: Any action requiring authoritative timestamps or duration claims.
- **MAY proceed**: Actions that explicitly state time is unknown.
- **Recorded about refusal**: Time source unavailable or ambiguous.
- **Unknown completion**: Time uncertainty recorded with the attempted action.

### 9) Dependency failure — queue
- **MUST be refused**: Any action that depends on queued delivery or processing.
- **MAY proceed**: None if queue is required for completion.
- **Recorded about refusal**: Queue unavailable; delivery cannot be guaranteed.
- **Unknown completion**: “Unknown completion” recorded for queued action.

### 10) Dependency failure — cache
- **MUST be refused**: Any action that would treat cached data as authoritative.
- **MAY proceed**: Actions that explicitly deny cache authority.
- **Recorded about refusal**: Cache unusable for authoritative data.
- **Unknown completion**: Uncertainty recorded for cache-dependent reads.

### 11) Dependency failure — network
- **MUST be refused**: Any action requiring confirmed remote state or acknowledgment.
- **MAY proceed**: None where remote confirmation is required.
- **Recorded about refusal**: Network unavailable; remote state unknown.
- **Unknown completion**: “Unknown completion” recorded for remote actions.

### 12) Dependency failure — auth/identity
- **MUST be refused**: Any action requiring verified identity or authority.
- **MAY proceed**: None when authorization is required.
- **Recorded about refusal**: Identity/authority cannot be verified.
- **Unknown completion**: Not applicable; refusal is explicit due to unknown authority.

### 13) Dependency failure — clock
- **MUST be refused**: Any action requiring authoritative time or ordering.
- **MAY proceed**: Actions explicitly marked as time-unknown.
- **Recorded about refusal**: Time source cannot be validated.
- **Unknown completion**: Time uncertainty recorded for affected actions.

### 14) Corrupted or invalid inputs
- **MUST be refused**: Any action requiring valid input.
- **MAY proceed**: None when validation fails.
- **Recorded about refusal**: Input invalid or corrupted.
- **Unknown completion**: Not applicable; refusal occurs before action completion.

### 15) Schema / format mismatch
- **MUST be refused**: Any action requiring consistent interpretation.
- **MAY proceed**: None if interpretation is required.
- **Recorded about refusal**: Schema/format mismatch; interpretation unknown.
- **Unknown completion**: “Unknown completion” recorded for interpretation-dependent actions.

### 16) Unknown state
- **MUST be refused**: Any action that would assert completion or durability.
- **MAY proceed**: None where completion status is required.
- **Recorded about refusal**: Completion status unknown.
- **Unknown completion**: Explicit “unknown completion” record for the attempted action.

---

## SECTION 3 — Operator-Visible Failure Language Rules

### Permitted phrases (descriptive only)
- “storage unavailable”
- “storage response incomplete”
- “write could not be confirmed durable”
- “read could not be completed”
- “partial persistence detected”
- “ordering cannot be guaranteed”
- “time source unavailable”
- “time source ambiguous”
- “network unavailable”
- “dependency unavailable: queue”
- “dependency unavailable: cache”
- “dependency unavailable: auth”
- “input invalid”
- “input corrupted”
- “schema mismatch”
- “format mismatch”
- “completion status unknown”
- “record durability unknown”
- “data may be incomplete”
- “system cannot know whether X occurred”
- “refusal recorded”
- “action refused due to unmet guarantees”

### Forbidden phrases (non-exhaustive)
- “healthy”
- “safe”
- “ok”
- “green / yellow / red”
- “degraded but operational”
- “best effort”
- “likely”
- “probably”
- “mostly fine”
- “recovering”
- “temporary”
- “minor issue”
- “acceptable”
- “no problem”
- “all good”
- “trustworthy”
- “correct”
- “complete”

### Placement rules (visibility)
- Failure text must appear at the point where the action is attempted or the record is viewed.
- Failure text must be co-located with any refused action outcome.
- Failure text must not be hidden behind secondary disclosure by default.
- If multiple failures apply, each must be shown explicitly; none may be collapsed.

---

## SECTION 4 — Silent Fallback Prohibition Map

### 1) Serving cached data when storage is unavailable
- **Temptation**: Provide continuity of reads.
- **Semantic change**: Cached data presented as authoritative.
- **Why forbidden**: Hides loss of durability and completeness; violates fail-loudly and preserve-uncertainty invariants.

### 2) Queueing writes for later without disclosure
- **Temptation**: Preserve user flow during outage.
- **Semantic change**: Write appears durable when it is not.
- **Why forbidden**: Converts uncertainty into implied completion.

### 3) Reordering events when ordering is ambiguous
- **Temptation**: Present a coherent timeline.
- **Semantic change**: Imposes ordering not guaranteed.
- **Why forbidden**: Introduces implied correctness and narrative.

### 4) Filling missing timestamps from local time
- **Temptation**: Provide complete records.
- **Semantic change**: Time becomes asserted rather than unknown.
- **Why forbidden**: Masks time ambiguity.

### 5) Dropping invalid records silently
- **Temptation**: Keep processing pipeline clean.
- **Semantic change**: Absence of records appears as non-existence.
- **Why forbidden**: Hides refusal and loss of evidence.

### 6) Returning partial reads without disclosure
- **Temptation**: “Best effort” data.
- **Semantic change**: Partial dataset treated as complete.
- **Why forbidden**: Collapses uncertainty.

### 7) Auto-retry with altered semantics
- **Temptation**: Make actions appear successful.
- **Semantic change**: Different behavior under same request without disclosure.
- **Why forbidden**: Violates deterministic refusal and explicit mode change.

### 8) Substituting alternate dependencies without disclosure
- **Temptation**: Maintain availability.
- **Semantic change**: Meaning of records changes without notice.
- **Why forbidden**: Introduces hidden semantic fallback.

---

## SECTION 5 — Adversarial Operability Audit Surface

### Hidden failure
- Attempt to provoke component failure while observing whether failure remains visible at the point of use.
- Attempt to locate any path where a failed dependency yields no explicit failure disclosure.

### Hidden partial persistence
- Attempt to trigger partial writes and then observe whether any view implies completeness.
- Attempt to compare expected versus visible records under partial persistence.

### Silent semantic fallback
- Attempt to force fallback paths (cache, queue, alternate storage) and observe whether the mode change is visible.
- Attempt to detect any implicit substitution of data sources without disclosure.

### Implied completeness under uncertainty
- Attempt to force unknown completion states and observe whether any output suggests success.
- Attempt to find wording that implies completion despite stated uncertainty.

### Inconsistent refusal under identical conditions
- Repeat identical failure conditions and compare refusal behavior and wording.
- Attempt to find variability across retries that implies nondeterministic refusal.
