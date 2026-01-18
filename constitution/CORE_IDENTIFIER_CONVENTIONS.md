---
doc_id: core_identifier_conventions
doc_type: constitution
status: locked
version: 1.0
date: 2026-01-18
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [identifiers, guild]
---

# Identifier Conventions (Guild-Safe)

**Applies To**: All layers (Ops, Cutter Ledger, State Ledger)

---

## Purpose
This document defines **Guild-safe identifier formats** for cross-organizational contexts where multiple independent entities (guilds, companies, shops) may operate within the same system without centralized authority.

**Key Principle**: Identifiers must prevent collisions and support multi-tenant scenarios without requiring a central registry or authentication system.

---

## Identifier Formats

### 1. Organization Reference (`org_ref`)
**Format**: `org:{domain}`

**Rules**:
- Domain must be a valid DNS-style identifier (lowercase, alphanumeric, hyphens, dots)
- Minimum 2 characters
- Maximum 253 characters (DNS limit)
- Examples:
  - `org:acme.com`
  - `org:shop-42`
  - `org:guild-a`

**Why**: DNS-style domains provide natural global uniqueness without central coordination. Organizations control their own namespace.

**Usage**: Prefix for all organizational entities to prevent cross-organization collisions.

---

### 2. Actor Reference (`actor_ref`)
**Format**: `{org_ref}/actor:{local_id}`

**Rules**:
- Must start with valid `org_ref` followed by `/actor:`
- Local ID: alphanumeric, hyphens, underscores, dots
- Minimum 1 character for local ID
- Maximum 100 characters for local ID
- Examples:
  - `org:acme.com/actor:alice`
  - `org:shop-42/actor:bob.smith`
  - `org:guild-a/actor:operator-7`

**Why**: Scoped actor identities prevent name collisions across organizations. Each org manages its own actor namespace.

**Usage**:
- State Ledger: `declared_by_actor_ref`, `assigned_by_actor_ref`
- State Ledger: `owner_actor_ref` in recognition assignments
- Any system tracking human or service actors

**Constitutional Compliance**: No inference of identity. Actor ref is an opaque string. The system does not authenticate, authorize, or interpret actor refs.

---

### 3. Entity Reference (`entity_ref`)
**Format**: `{org_ref}/entity:{type}:{local_id}`

**Rules**:
- Must start with valid `org_ref` followed by `/entity:`
- Type: single word (alphanumeric, hyphens), describes entity kind
- Local ID: alphanumeric, hyphens, underscores, dots, colons
- Type minimum 1 character, maximum 50 characters
- Local ID minimum 1 character, maximum 100 characters
- Examples:
  - `org:acme.com/entity:customer:cust-123`
  - `org:shop-42/entity:project:proj-alpha`
  - `org:guild-a/entity:dept:engineering`
  - `org:acme.com/entity:quote:Q-2026-001`

**Why**: Typed entity references make the system's scope explicit. The `type` segment prevents collisions between different entity kinds (customer vs project vs department).

**Usage**:
- State Ledger: `entity_ref` in entities table
- Any cross-organizational entity tracking

**Note**: The `type` is descriptive metadata, not enforced authority. The system does not interpret types; it only validates format.

---

### 4. Scope Reference (`scope_ref`)
**Format**: `{org_ref}/scope:{context}`

**Rules**:
- Must start with valid `org_ref` followed by `/scope:`
- Context: alphanumeric, hyphens, underscores, dots, colons
- Minimum 1 character for context
- Maximum 100 characters for context
- Examples:
  - `org:acme.com/scope:weekly-review`
  - `org:shop-42/scope:q1-2026`
  - `org:guild-a/scope:ops`
  - `org:acme.com/scope:dept:engineering`

**Why**: Recognition contexts are organization-specific. Scoped references prevent cross-org confusion about what "weekly" or "q1" means.

**Usage**:
- State Ledger: `scope_ref` in declarations
- Any time-bounded or context-specific recognition

---

## Why Guild-Safe Identifiers?

### Problem: Collision Risk in Multi-Tenant Systems
Without org-scoped identifiers:
- Actor `alice` from Org A collides with Actor `alice` from Org B
- Entity `customer:123` from Org A collides with Entity `customer:123` from Org B
- Scope `weekly` from Org A has different meaning than `weekly` from Org B

### Solution: DNS-Style Namespacing
By prefixing with `org:{domain}`:
- Each organization controls its own namespace
- No central authority required
- Natural global uniqueness via DNS semantics
- Clear ownership boundaries

### Multi-Tenant Without Central Auth
**Guild-safe identifiers enable**:
- Multiple independent organizations in one database
- No shared actor registry
- No central org table (optional, not required)
- Each org self-manages its namespace

**What the system does NOT do**:
- Authenticate org ownership of domains
- Enforce org isolation (application-layer concern)
- Interpret or compare org domains
- Auto-assign org prefixes

**Enforcement Surface**: Format validation only. The system refuses malformed identifiers but does not verify organizational authority.

---

## Validation Rules (Summary)
| Identifier | Pattern | Max Length | Case Sensitive |
|------------|---------|------------|----------------|
| `org_ref` | `org:{domain}` | 257 chars | No (lowercase enforced) |
| `actor_ref` | `{org_ref}/actor:{local_id}` | ~360 chars | No (lowercase enforced) |
| `entity_ref` | `{org_ref}/entity:{type}:{local_id}` | ~410 chars | No (lowercase enforced) |
| `scope_ref` | `{org_ref}/scope:{context}` | ~360 chars | No (lowercase enforced) |

**Enforcement**: State Ledger boundary module validates all refs. Malformed refs are refused with clear error messages.

---

## Examples: Multi-Guild Scenario

**Guild A** (small shop):
- Org: `org:shop-alpha`
- Actor: `org:shop-alpha/actor:owner`
- Entity: `org:shop-alpha/entity:customer:acme-inc`
- Scope: `org:shop-alpha/scope:monthly`

**Guild B** (contract manufacturer):
- Org: `org:cm-beta.com`
- Actor: `org:cm-beta.com/actor:qc-lead`
- Entity: `org:cm-beta.com/entity:project:proj-777`
- Scope: `org:cm-beta.com/scope:q1-review`

**No collisions**: Even if both have a customer named "acme-inc", their entity refs are distinct.

---

## Implementation Notes

### State Ledger Integration
The State Ledger boundary module validates all identifier formats:
- `emit_state_declaration()` validates `entity_ref`, `actor_ref`, `scope_ref`
- `assign_owner()` validates `entity_ref`, `actor_ref`

**Refusal behavior**: If any ref is malformed, the operation is refused with a clear error message specifying which ref failed validation and why.

### No Schema Changes
Identifier conventions are **format rules**, not schema constraints. Existing TEXT columns in `state__entities`, `state__recognition_owners`, and `state__declarations` remain unchanged.

Validation happens at the **boundary**, not the database.

### Validation Module
A dedicated `state_ledger/validation.py` module provides:
- `validate_org_ref(org_ref: str) -> tuple[bool, str]`
- `validate_actor_ref(actor_ref: str) -> tuple[bool, str]`
- `validate_entity_ref(entity_ref: str) -> tuple[bool, str]`
- `validate_scope_ref(scope_ref: str) -> tuple[bool, str]`

**Returns**: `(is_valid: bool, error_message: str)`

**Behavior**: Validators accept or refuse. They do NOT "correct" inputs.

---

## Constitutional Compliance
✅ **No Interpretation**: Identifiers are opaque strings. The system does not interpret org domains, actor names, entity types, or scope contexts.  
✅ **No Inference**: Format validation is mechanical. No guessing, no auto-completion, no suggestions.  
✅ **Refusal on Violation**: Malformed identifiers are refused immediately at the boundary.  
✅ **No Central Authority**: Organizations self-manage namespaces. No org registry, no auth system, no coordination.  
✅ **Append-Only Memory**: Identifier validation does not alter historical records. Once written, refs persist as-is.

---

## Future Considerations (Not Implemented)

### Optional: Org Table (Phase N)
If needed in the future, an `organizations` table could:
- Track known orgs (for UI autocomplete, not enforcement)
- Store org metadata (display name, contact, etc.)
- Provide a "registry" for convenience

**Critical**: Even with an org table, the system must NOT enforce org membership. Identifier validation remains format-only.

### Optional: Actor Directory (Phase N)
An actor directory could:
- List known actors per org (for UI, not enforcement)
- Store actor display names, roles, contact info

**Critical**: No authentication, no authorization, no identity verification. The directory is informational only.

---

**Identifier conventions establish Guild-safe namespacing without central coordination.**

**Next steps**: Wire validators into State Ledger boundary, add tests, verify format compliance.
