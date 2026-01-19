---
doc_id: quarantine_features_list
doc_type: context
status: quarantined
version: 1.0
date: 2026-01-18
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [quarantine]
---

Source: Cutter Layers/FEATURES_LIST.md

# The Cutter - Complete Features List

**Generated:** January 13, 2026  
**System Version:** Phase 5 (Local-First ERP for Machine Shops)

---

## 1. CORE QUOTING ENGINE

### 1.1 File Mode (3D Upload)
- **3D File Processing**: Upload STL/STEP files for automatic geometry analysis
- **Unit Detection**: Multi-factor heuristic to detect inches vs millimeters from dimensionless STL files
- **Unit Confirmation**: Explicit user confirmation of detected units before pricing
- **Genesis Hash Generation**: SHA-256 hash of volume + dimensions for global part identification
- **Volume Calculation**: Automatic extraction of part volume from 3D mesh
- **Bounding Box Analysis**: Automatic calculation of X/Y/Z dimensions
- **Material Selection**: Material picker with cost database lookup
- **Quantity Input**: Support for single or batch quantities

### 1.2 Napkin Mode (Manual Entry)
- **Parametric Shapes**: Pre-configured shapes (Block, Cylinder, Plate, L-Bracket, Tube)
- **Manual Dimension Entry**: Direct input of dimensions for quick quotes
- **Volume Calculation**: Automatic volume calculation from parametric inputs
- **Genesis Hash Generation**: Consistent hash generation for manual entries
- **Same Pricing Engine**: Identical pricing logic as File Mode

### 1.3 Physics-Based Pricing ("The Anchor")
- **Material Cost Calculation**: Stock volume × material cost per cubic inch × markup
- **Setup Scrap Logic**: Additional material allocation for low-quantity runs (<10 units)
- **Labor Cost Calculation**: (Setup + Per-Part Runtime + Handling) × Shop Rate
- **Runtime Estimation**: Machine time estimation based on geometry and material
- **Stock Suggestion**: Automatic recommended stock dimensions with waste factor
- **Process Routing**: Configurable manufacturing steps (mill, lathe, drill, tap, etc.)
- **Quantity Breaks**: Automatic price breaks at 1, 5, 25, 100, 250 quantities
- **Shop Rate Configuration**: Customizable hourly shop rate (stored in database)

### 1.4 Override System (Variance Attribution)
- **Manual Price Adjustment**: Override system anchor price with final quoted price
- **Weighted Variance Tags**: Explain price adjustments with categorized reasons
- **Custom Tags**: Create shop-specific variance tags (name, impact type, value, category)
- **Tag Persistence**: Transient (per-quote) or persistent tags
- **Tag Categories**: Organize tags by functional area (Material, Complexity, Customer, etc.)
- **Unexplained Variance Tracking**: System calculates delta between explained variance and total override
- **Exhaust Emission**: All overrides emit QUOTE_OVERRIDDEN events to Cutter Ledger

---

## 2. CUSTOMER & CONTACT MANAGEMENT (4-Table Identity Model)

### 2.1 Customer Resolution
- **Domain-Based Matching**: Resolve customer by email domain (@spacex.com → SpaceX)
- **Name-Based Fallback**: Match by company name if domain not provided
- **Automatic Creation**: Create new customer record if no match found
- **Duplicate Prevention**: Fuzzy matching to reduce duplicate customer records
- **Resolution Exhaust**: Emit CUSTOMER_RESOLVED or CUSTOMER_CREATED events

### 2.2 Contact Resolution (Roaming Buyer Detection)
- **Email-Based Matching**: Primary resolution by email address
- **Roaming Buyer Detection**: Detect when contact changes employers (email matches but different customer)
- **Customer Association Update**: Automatically update contact's current_customer_id on roaming
- **Placeholder Email Generation**: Generate `anon-{customer_id}-{uuid}@placeholder.com` if no email
- **Resolution Exhaust**: Emit CONTACT_RESOLVED, CONTACT_ROAMING_DETECTED, or CONTACT_CREATED events

### 2.3 Customer CRUD
- **Customer Creation**: Explicit creation of new customer records
- **Customer Update**: Edit customer name and domain
- **Customer Deletion**: Hard delete with cascade to related tables
- **Customer Search**: Search customers by name or domain
- **Exhaust Emission**: CUSTOMER_CREATED, CUSTOMER_UPDATED, CUSTOMER_DELETED events

### 2.4 Contact CRUD
- **Contact Creation**: Create contacts associated with customers
- **Contact Update**: Edit contact name, email, phone
- **Contact Deletion**: Hard delete with NULL cascade to quotes
- **Contact Search**: Search contacts by name or email
- **Primary Contact Designation**: Mark one contact as primary per customer
- **Exhaust Emission**: CONTACT_CREATED, CONTACT_UPDATED, CONTACT_DELETED events

---

## 3. LOCAL PATTERN MATCHING (Historical Intelligence)

### 3.1 Genesis Hash Matching
- **Exact Geometry Matching**: Find historical quotes for identical parts
- **Price History**: View previous quoted prices for same geometry
- **Tag Frequency Analysis**: Detect tags consistently applied to same geometry
- **Local History Analysis**: Cluster statistics (median, range, sample size)
- **Variance Percentage**: Compare current price vs historical median

### 3.2 Customer Pattern Detection
- **Customer-Specific Tags**: Detect tags frequently applied to specific customers
- **Confidence Scoring**: Calculate confidence based on historical frequency
- **Rush Job Detection**: Identify customers with short lead times
- **Tag Suggestions**: Auto-suggest variance tags based on customer patterns

### 3.3 Material Pattern Detection
- **Material-Specific Tags**: Detect tags consistently applied to difficult materials
- **Exotic Material Handling**: Flag titanium, Inconel, etc.
- **Material Cost Lookup**: Database-driven material pricing

### 3.4 Quantity Pattern Detection
- **Prototype Detection**: Flag low-quantity orders (<5) as likely prototypes
- **Volume Production**: Detect high-quantity runs (>100)

---

## 4. PDF GENERATION & DOCUMENTATION

### 4.1 Customer Quote PDF
- **Branded Quote Document**: Professional PDF with shop branding
- **Price Breakdown**: Material, labor, setup costs (Glass Box pricing)
- **QR Code**: Embedded QR code linking to quote record
- **Multi-Page Support**: Handle complex quotes with multiple pages
- **Lead Time Display**: Show estimated completion date
- **Payment Terms**: Display payment terms and conditions
- **Constitutional Compliance**: No proprietary markers (customer-safe)

### 4.2 Shop Traveler PDF
- **Internal Work Order**: Shop-floor manufacturing instructions
- **Process Routing**: Step-by-step manufacturing operations
- **QR Code/NFC**: Traveler identifier for future Node 2 (Traffic Cop) integration
- **Material Specifications**: Stock dimensions and material details
- **Quality Notes**: Special handling or inspection requirements
- **Physics Snapshot**: Technical geometry data for machinist reference

---

## 5. WIN/LOSS DATA CAPTURE (Closed-Loop Learning)

### 5.1 Direct Outcome Capture
- **Simple 2-Step Flow**: Outcome type (WON/LOST/NO_DECISION) + optional details
- **Change Needed Flag**: Capture if customer requested changes
- **Price Value**: Capture customer's stated price point
- **Optional Notes**: Free-text field for additional context
- **Exhaust Emission**: QUOTE_OUTCOME_CAPTURED event

### 5.2 Wizard Outcome Capture
- **Progressive Auto-Save**: Multi-step wizard with automatic saving
- **Original vs Final Comparison**: Track price, lead time, terms changes
- **Price Negotiation Tracking**: Original price → final agreed price delta
- **Lead Time Flexibility**: Original lead time → final lead time delta
- **Payment Terms Tracking**: Original terms → final terms comparison
- **Wizard Step Tracking**: Record which step user reached
- **Exhaust Emission**: QUOTE_OUTCOME_WIZARD_SAVED event with presence flags (not raw PII)

### 5.3 Status Update Workflow
- **Quick Status Change**: Update quote status (Draft → Sent → Won/Lost)
- **Win Notes**: Capture reason for winning (price, lead time, relationship, etc.)
- **Loss Attribution**: Multi-select reasons for losing (price, lead time, scope, etc.)
- **Final Price Capture**: Record final agreed price on win
- **Status Exhaust**: QUOTE_STATUS_CHANGED event
- **Price Finalization**: QUOTE_PRICE_FINALIZED event when final price differs

### 5.4 Unclosed Quotes View
- **Missing Outcomes**: List quotes without win/loss data
- **Age Tracking**: Show days since quote created
- **No-Response Handling**: Separate category for quotes with NO_RESPONSE outcome

---

## 6. CUTTER LEDGER (Operational Exhaust)

### 6.1 Event Emission
- **Single Write Path**: All events pass through `emit_cutter_event()` boundary
- **Append-Only Storage**: Events cannot be edited or deleted (DB triggers enforce)
- **Constitutional Event Types**: Descriptive, non-evaluative event vocabulary
- **Deterministic Provenance**: Git SHA + service ID for every event
- **Factual Payloads**: No interpretation, opinions, or recommendations

### 6.2 Quote Lifecycle Events
- **QUOTE_CREATED**: Quote saved with initial parameters
- **QUOTE_OVERRIDDEN**: Price differs from anchor (includes variance_json, arithmetic deltas)
- **QUOTE_STATUS_CHANGED**: Status transitions (Draft/Sent/Won/Lost)
- **QUOTE_DELETED**: Soft deletion timestamp
- **QUOTE_PRICE_FINALIZED**: Final price updated on win

### 6.3 Identity Resolution Events
- **CUSTOMER_CREATED**: New customer record created
- **CUSTOMER_RESOLVED**: Customer matched by domain or name
- **CONTACT_CREATED**: New contact record created
- **CONTACT_RESOLVED**: Contact matched by email
- **CONTACT_ROAMING_DETECTED**: Contact changed employers

### 6.4 CRUD Operation Events
- **CUSTOMER_UPDATED**: Customer info changed
- **CUSTOMER_DELETED**: Customer hard deleted (with cascade counts)
- **CONTACT_UPDATED**: Contact info changed
- **CONTACT_DELETED**: Contact hard deleted (with affected quote count)
- **CUSTOM_TAG_CREATED**: New variance tag created
- **CUSTOM_TAG_UPDATED**: Tag definition changed
- **CUSTOM_TAG_DELETED**: Tag removed (with approximate affected quotes count)

### 6.5 Outcome Capture Events
- **QUOTE_OUTCOME_CAPTURED**: Direct outcome saved
- **QUOTE_OUTCOME_WIZARD_SAVED**: Wizard outcome with progressive data

### 6.6 Query Interface
- **Event Query API**: Read events by type, subject_ref, date range
- **Constitutional Read-Only**: Query CLI refuses writes (enforced)
- **JSON Export**: Export events for external analysis

---

## 7. STATE LEDGER (Human Recognition)

### 7.1 Entity Registration
- **Guild-Safe References**: Register entities with org:{domain}/entity:{type}:{id} format
- **Cadence Configuration**: Set expected reaffirmation frequency (days)
- **Entity Labeling**: Human-readable labels for entities

### 7.2 Recognition Ownership
- **Owner Assignment**: Assign human owner (actor_ref) to entities
- **Ownership Transitions**: Transfer ownership between actors
- **Unassignment**: Explicitly remove owner (makes entity unowned)
- **Single Current Owner**: Only one owner per entity at a time (DB enforces)

### 7.3 State Declarations
- **REAFFIRMATION**: Owner confirms unchanged state
- **RECLASSIFICATION**: Owner declares changed state
- **Append-Only**: Declarations never edited or deleted
- **Supersession Tracking**: Link reclassifications to superseded declarations
- **Cutter Evidence**: Optional reference to cutter__events as evidence

### 7.4 Derived State Queries
- **DS-1 (Persistent Continuity)**: Entities with 2+ consecutive reaffirmations
- **DS-2 (Unowned Recognition)**: Entities without current owner
- **DS-5 (Deferred Recognition)**: Entities past cadence window
- **Latest Declarations**: Most recent declaration per entity/scope

### 7.5 Constitutional Enforcement
- **No Auto-Generation**: Refuses to create declarations from other ledgers
- **Owner-Only Recognition**: Refuses proxy recognition
- **No Default State**: Refuses pre-filled or carried-forward state
- **No Interpretation**: Raw observation only, no meaning assigned

---

## 8. SYSTEM CONFIGURATION

### 8.1 Shop Configuration
- **Shop Rate**: Configurable hourly rate (stored in shop_config table)
- **Material Markup**: Configurable material markup percentage
- **Default Material**: Set default material for new quotes
- **Database-Driven Config**: All config stored in shop_config table

### 8.2 Material Database
- **Material Library**: Pre-seeded material costs per cubic inch
- **Material Lookup**: Retrieve cost by material name
- **Fallback Pricing**: Use Aluminum 6061 if material not found
- **Material Validation**: Fuzzy matching for material names

### 8.3 Database Management
- **SQLite with WAL Mode**: Write-Ahead Logging for concurrent access
- **Schema Migrations**: Versioned migrations for schema changes
- **Backup Support**: Database backup before destructive migrations
- **Foreign Key Enforcement**: ON DELETE SET NULL / RESTRICT constraints
- **Append-Only Triggers**: Prevent UPDATE/DELETE on ledger tables

---

## 9. DATA EXPORT & INTEGRATION

### 9.1 Closed-Loop Export
- **Export Guild Packet**: Manual export of anonymized closed-loop data
- **Export Contents**: Genesis Hash, prices, variance tags, outcomes
- **Pending Export Count**: Track quotes ready for export
- **Manual Export Only**: No automatic submission (explicit user action)
- **Neutral Filename**: `closed_loop_export_{date}_{uuid}.json`

### 9.2 Quote History
- **Historical Quotes View**: Browse all past quotes
- **Quote Search**: Find quotes by ID, customer, material
- **Quote Retrieval**: Fetch complete quote details by ID
- **Soft Delete Support**: Filter out deleted quotes

---

## 10. TESTING & VERIFICATION

### 10.1 Unit Tests
- **Genesis Hash Tests**: Determinism, uniqueness, collision detection
- **Pricing Algorithm Tests**: Anchor calculation accuracy
- **Unit Conversion Tests**: Inch/mm conversion accuracy
- **Identity Resolution Tests**: Customer/contact matching logic
- **Pattern Matching Tests**: Historical pattern detection

### 10.2 Integration Tests
- **Quote Lifecycle Tests**: End-to-end quote creation and status changes
- **Event Emission Tests**: Verify all exhaust events emitted correctly
- **Ledger Query Tests**: Read-only enforcement, query functionality
- **State Ledger Tests**: Entity registration, ownership, declarations
- **Weekly Ritual Tests**: DS-2, DS-5 derived state query accuracy

### 10.3 Smoke Tests
- **System Health Check**: `/health` and `/api/system/health` endpoints
- **Database Connectivity**: Verify database accessible
- **File Upload**: Test STL file upload and processing
- **PDF Generation**: Verify quote and traveler PDF creation

---

## 11. SCRIPTS & UTILITIES

### 11.1 Database Scripts
- **reset_db.py**: Initialize fresh database with schema
- **baseline_declarations.py**: Seed initial State Ledger declarations (idempotent)
- **inspect_state_schema.py**: Verify State Ledger schema integrity

### 11.2 Ledger Query CLI
- **ledger_query_cli.py**: Command-line interface for ledger queries
- **Read-Only Enforcement**: Refuses any write operations
- **Event Queries**: Query Cutter Ledger events
- **State Queries**: Query State Ledger declarations and entities
- **JSON Output**: All results in JSON format

### 11.3 Reporting Scripts
- **weekly_ritual.py**: Generate DS-2 and DS-5 reports (unowned/deferred recognition)
- **demo_end_to_end.py**: End-to-end smoke test with JSON output
- **query_override_events.py**: Query quote override patterns
- **verify_event_emission.py**: Verify exhaust emission coverage

---

## 12. CONSTITUTIONAL CONSTRAINTS

### 12.1 Local-First Architecture
- **Offline Operation**: Works indefinitely without internet
- **Data Sovereignty**: All data stored locally (SQLite)
- **Optional Network**: Export/backup features only (explicit opt-in)
- **No Cloud Dependencies**: Zero required external services

### 12.2 Glass Box Pricing
- **Visible Math**: All pricing calculations exposed to user
- **Override Transparency**: Requires explanation for price adjustments
- **No Black Boxes**: Every assumption editable by user

### 12.3 Outcome Agnosticism
- **Descriptive Events**: Event types never evaluative
- **No Implied Judgment**: System never labels outcomes as "good" or "bad"
- **Raw Observation**: Facts only, no interpretation

### 12.4 Irreversible Memory
- **Append-Only Ledgers**: Cutter and State Ledgers never edited
- **DB Trigger Enforcement**: Prevents UPDATE/DELETE on ledger tables
- **Provenance Tracking**: Git SHA + service ID on every event

### 12.5 Separation of Observation and Judgment
- **State Ledger**: Raw human recognition only
- **No Auto-Generation**: System never infers or creates declarations
- **No Pre-Filling**: No carried-forward or default state

---

## 13. FUTURE PLANNED FEATURES (Not Yet Implemented)

### 13.1 Node 2: Traffic Cop (Shop Floor)
- **Scan & Start**: QR/NFC traveler scanning
- **Cycle Time Capture**: Automatic runtime tracking
- **Mobile PWA**: Shop-floor mobile interface
- **Live Feed**: Real-time job status

### 13.2 Node 3: The Truth (QC & Inspection)
- **Snap-to-Pass**: Mobile inspection interface
- **Certificate Generation**: Auto-generate inspection reports
- **Yield/Scrap Tracking**: Capture actual vs estimated scrap

### 13.3 Dashboard (Phase 7)
- **Bento Grid HUD**: Dense, urgent-first layout
- **The Funnel**: Quotes sent vs won (sales health)
- **The Stuck List**: Jobs stalled between nodes
- **Node 2 Live Feed**: Active machine jobs
- **Node 3 Queue**: Parts awaiting inspection

### 13.4 The Guild (Separate Product)
- **Cross-Shop Intelligence**: Market pricing data by Genesis Hash
- **Capacity Referrals**: Find shops with available capacity
- **Material Trends**: Network-wide material cost tracking
- **Lead Time Data**: Observed completion times
- **Explicit Context Switch**: Guild is separate product, not Ops feature

---

## 14. API ENDPOINTS

### 14.1 Quote Operations
- `POST /quote` - Create quote from 3D file upload
- `POST /quote/confirm-units` - Confirm detected units before pricing
- `POST /recalculate` - Recalculate price with new parameters
- `POST /manual_quote` - Create quote from manual dimensions (Napkin Mode)
- `POST /save_quote` - Save completed quote to database
- `GET /api/quote/<id>` - Retrieve quote details
- `GET /api/quote/<id>/pdf` - Generate customer quote PDF
- `GET /api/quote/<id>/traveler` - Generate shop traveler PDF
- `POST /api/quote/<id>/mark_won` - Quick-mark quote as Won
- `POST /api/quote/<id>/update_status` - Update quote status with details

### 14.2 Outcome Capture
- `POST /api/quote/<id>/outcome` - Direct outcome capture (2-step)
- `POST /api/quote/<id>/outcome/wizard` - Wizard outcome capture (progressive)
- `GET /api/unclosed_quotes` - List quotes without outcomes

### 14.3 Customer & Contact Management
- `GET /api/customers` - List all customers
- `GET /api/customers/search` - Search customers by name/domain
- `GET /api/customer/<id>` - Get customer details
- `POST /api/customer` - Create new customer
- `PUT /api/customer/<id>` - Update customer
- `DELETE /api/customer/<id>` - Delete customer
- `GET /api/contacts/search` - Search contacts by name/email
- `POST /api/customer/<id>/contact` - Create contact for customer
- `PUT /api/contact/<id>` - Update contact
- `DELETE /api/contact/<id>` - Delete contact

### 14.4 Variance Tags
- `GET /tags` or `GET /api/tags` - List all custom tags
- `POST /tags/new` - Create new custom tag
- `PUT /tags/<id>` - Update custom tag
- `DELETE /tags/<id>` - Delete custom tag

### 14.5 Utilities
- `POST /api/convert_units` - Convert dimensions between units
- `POST /api/pattern_suggestions` - Get variance tag suggestions
- `GET /materials` - List available materials
- `GET /check_quote_id/<id>` - Check if quote ID available
- `GET /history` - List historical quotes
- `POST /delete_quote/<id>` - Soft delete quote

### 14.6 System Health
- `GET /health` - Basic health check
- `GET /api/system/health` - Detailed system health with uptime

### 14.7 Export
- `GET /export_guild_packet` - Export closed-loop data
- `GET /pending_exports` - Count quotes ready for export

---

## 15. KEY TECHNICAL SPECIFICATIONS

### 15.1 Genesis Hash Standard
- **Algorithm**: SHA-256
- **Inputs**: Volume (6 decimal places) + Sorted Dimensions (4 decimal places)
- **Units**: Cubic inches for volume, inches for dimensions
- **Format**: 64-character hex string
- **Determinism**: Identical parts always produce identical hashes

### 15.2 Database Schema
- **Engine**: SQLite 3
- **Journal Mode**: WAL (Write-Ahead Logging)
- **Tables**: ops__quotes, ops__parts, ops__customers, ops__contacts, ops__custom_tags, ops__quote_outcome_events, cutter__events, state__entities, state__recognition_owners, state__declarations
- **Foreign Keys**: Enabled with ON DELETE constraints
- **Indexes**: Optimized for common query patterns

### 15.3 Identifier Conventions
- **Quote IDs**: User-defined alphanumeric (e.g., Q-2026-001)
- **Subject References**: `{type}:{id}` (e.g., quote:1, customer:5)
- **Entity References**: `org:{domain}/entity:{type}:{id}` (Guild-safe)
- **Actor References**: `actor:human:{name}` or `actor:machine:{id}`
- **Scope References**: `scope:process:{name}` or `scope:customer:{id}`

### 15.4 File Support
- **3D Formats**: STL (binary/ASCII), STEP
- **Upload Location**: `C:\cutter_assets\` (configurable)
- **Secure Filenames**: werkzeug.secure_filename for sanitization
- **Max File Size**: Configurable (default: reasonable for typical CAD files)

---

## ARCHITECTURAL PRINCIPLES

1. **Local-First**: Works offline indefinitely, no cloud dependencies
2. **Glass Box**: All calculations visible and editable
3. **Append-Only Ledgers**: History never erased or rewritten
4. **Constitutional Enforcement**: Code enforces architectural rules
5. **Outcome Agnosticism**: System observes, never judges
6. **Data Sovereignty**: User owns all data, stored locally
7. **Demonstrated Reality Only**: No inference, prediction, or auto-generation
8. **Separation of Concerns**: Ops/Cutter/State ledgers isolated
9. **Single Authorized Paths**: Boundary modules enforce write discipline
10. **Guild Firewall**: Guild is separate product, not Ops feature

---

**Document Maintenance**: This list should be updated whenever new features are added or existing features are substantially modified.
