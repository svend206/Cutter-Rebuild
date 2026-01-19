"""
Database module for materials storage.
Uses SQLite for local storage.
"""
import json
import os
import sqlite3
import sys
from typing import Optional, Tuple, List, Dict, Any
from pathlib import Path
from datetime import datetime

# Support isolated test database via environment variable
REPO_ROOT = Path(__file__).parent
PROD_DB_PATH = (REPO_ROOT / "cutter.db").resolve()


def _is_running_pytest() -> bool:
    return bool(os.environ.get("PYTEST_CURRENT_TEST")) or any("pytest" in arg for arg in sys.argv)


def _is_running_unittest() -> bool:
    return any("unittest" in arg for arg in sys.argv)


def _is_valid_test_path(path: Path) -> bool:
    path_str = str(path).lower()
    return ("test" in path_str) or ("tests" in path.parts)


def validate_db_mode() -> Path:
    test_db_env = os.environ.get("TEST_DB_PATH")
    if test_db_env:
        resolved = Path(test_db_env).resolve()
        if resolved == PROD_DB_PATH:
            print("[DB MODE ERROR] TEST_DB_PATH resolves to production cutter.db.")
            print(f"  TEST_DB_PATH: {resolved}")
            print("  Fix: set TEST_DB_PATH to a non-prod test database path.")
            raise SystemExit(1)
        if not _is_valid_test_path(resolved):
            print("[DB MODE ERROR] TEST_DB_PATH does not look like a test path.")
            print(f"  TEST_DB_PATH: {resolved}")
            print("  Fix: use a path containing 'test' or under a tests/ directory.")
            raise SystemExit(1)
        print(f"[DB MODE] TEST -> {resolved}")
        return resolved

    if _is_running_pytest():
        print("[DB MODE ERROR] pytest detected but TEST_DB_PATH is unset.")
        print("  Fix: set TEST_DB_PATH to an isolated test database path.")
        raise SystemExit(1)

    if not _is_running_unittest():
        print(f"[DB MODE] PROD -> {PROD_DB_PATH}")
    return PROD_DB_PATH


def require_test_db(reason: str) -> Path:
    test_db_path = os.environ.get("TEST_DB_PATH")
    if not test_db_path:
        raise RuntimeError(f"TEST_DB_PATH is required for {reason}.")
    path = Path(test_db_path).resolve()
    path_str = str(path).lower()
    if ("test" not in path_str) and ("tests" not in path.parts):
        raise RuntimeError(f"TEST_DB_PATH must point to a test database path for {reason} (include 'test').")
    return path


DB_PATH = validate_db_mode()

def resolve_db_path() -> Path:
    test_db_env = os.environ.get("TEST_DB_PATH")
    if test_db_env:
        return Path(test_db_env)
    return DB_PATH

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")  # CRITICAL: Constitution Rule #2
    return conn

def initialize_database() -> None:
    conn = get_connection()
    cursor = conn.cursor()
    
    # --- PHASE 1-3 LEGACY TABLES ---
    
    # 1. Materials
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ops__materials (
            name TEXT PRIMARY KEY,
            cost_per_cubic_inch REAL NOT NULL,
            machinability_score REAL NOT NULL
        )
    """)
    
    # 2. Shop Configuration
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ops__shop_config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            description TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 3. Quote History (Legacy Flat Table)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ops__quote_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            fingerprint TEXT,
            anchor_price REAL,
            final_price REAL,
            setup_time INTEGER,
            user_feedback_tags TEXT,
            tag_weights TEXT,
            status TEXT DEFAULT 'Draft',
            actual_runtime REAL,
            is_guild_submission INTEGER DEFAULT 0,
            -- guild_credit_earned removed (PHASE 1: Guild economics in Ops DB violates firewall)
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            loss_reason TEXT,
            win_notes TEXT,
            closed_at TEXT
        )
    ''')

    # --- PHASE 4: IDENTITY MODEL (4-TABLES) ---

    # 4. Customers (The Bill-To)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ops__customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            domain TEXT NOT NULL,
            corporate_tags_json TEXT DEFAULT '[]',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 5. Contacts (The Decision-Maker)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ops__contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            current_customer_id INTEGER,
            behavior_tags_json TEXT DEFAULT '[]',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(current_customer_id) REFERENCES ops__customers(id)
        )
    """)

    # 6. Parts (The Geometry)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ops__parts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            genesis_hash TEXT UNIQUE NOT NULL,
            filename TEXT,
            fingerprint_json TEXT,
            volume REAL,
            surface_area REAL,
            dimensions_json TEXT,
            process_routing_json TEXT DEFAULT '[]',
            features_json TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 7. Quotes (The Transaction)
    # Includes "Deal Closer" fields: win_notes, loss_reason, closed_at
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ops__quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote_id TEXT UNIQUE NOT NULL,
            part_id INTEGER NOT NULL,
            customer_id INTEGER NOT NULL,
            contact_id INTEGER,
            user_id INTEGER,
            
            material TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            target_date TEXT,
            payment_terms_days INTEGER DEFAULT 30,
            
            system_price_anchor REAL NOT NULL,
            final_quoted_price REAL NOT NULL,
            
            variance_json TEXT,
            pricing_tags_json TEXT,
            physics_snapshot_json TEXT,
            
            status TEXT DEFAULT 'Draft',
            notes TEXT,
            
            -- RFQ First Fields
            lead_time_date TEXT,
            lead_time_days INTEGER,
            target_price_per_unit REAL,
            price_breaks_json TEXT,
            outside_processing_json TEXT,
            quality_requirements_json TEXT,
            part_marking_json TEXT,
            
            -- Deal Closer Fields
            win_notes TEXT,
            loss_reason TEXT,
            closed_at TEXT,
            
            -- Structured Win/Loss Attribution (Per quote outcome modal spec)
            win_attribution_json TEXT,
            loss_attribution_json TEXT,
            
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY(part_id) REFERENCES ops__parts(id) ON DELETE CASCADE,
            FOREIGN KEY(customer_id) REFERENCES ops__customers(id) ON DELETE RESTRICT,
            FOREIGN KEY(contact_id) REFERENCES ops__contacts(id) ON DELETE SET NULL
        )
    """)
    
    # 8. Quote Outcome Events (Append-Only Truth Ledger + Wizard Data)
    # Per wizard spec: Progressive auto-save with original vs final values
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ops__quote_outcome_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote_id INTEGER NOT NULL,
            outcome_type TEXT NOT NULL,
            actor_user_id INTEGER,
            saved_at TEXT DEFAULT CURRENT_TIMESTAMP,
            
            -- Wizard: Price tracking (original vs final)
            original_price REAL,
            final_price REAL,
            price_changed BOOLEAN DEFAULT FALSE,
            
            -- Wizard: Lead time tracking
            original_leadtime_days INTEGER,
            final_leadtime_days INTEGER,
            leadtime_changed BOOLEAN DEFAULT FALSE,
            
            -- Wizard: Payment terms tracking
            original_terms_days INTEGER,
            final_terms_days INTEGER,
            terms_changed BOOLEAN DEFAULT FALSE,
            
            -- Wizard: Other notes
            other_notes TEXT,
            
            -- Wizard completion tracking
            wizard_completed BOOLEAN DEFAULT FALSE,
            wizard_step_reached INTEGER DEFAULT 0,
            
            FOREIGN KEY(quote_id) REFERENCES ops__quotes(id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_outcome_events_quote ON ops__quote_outcome_events (quote_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_outcome_events_actor ON ops__quote_outcome_events (actor_user_id)")
    
    # 9. Custom Tags (Guild Ledger removed - PHASE 1 REMEDIATION)
    # ops__guild_ledger deleted: Guild economics belong in Guild product

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ops__custom_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            impact_type TEXT, 
            impact_value REAL,
            persistence_type TEXT DEFAULT 'transient',
            category TEXT DEFAULT 'General'
        )
    ''')
    
    # --- MIGRATIONS (Ensure columns exist on legacy/existing DBs) ---
    
    # Helper to safe-add columns
    def add_column_safe(table, col_name, col_type):
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass # Column exists

    # Migrate Quotes table (Deal Closer fields)
    add_column_safe('ops__quotes', 'win_notes', 'TEXT')
    add_column_safe('ops__quotes', 'loss_reason', 'TEXT')
    add_column_safe('ops__quotes', 'closed_at', 'TEXT')
    add_column_safe('ops__quotes', 'win_attribution_json', 'TEXT')
    add_column_safe('ops__quotes', 'loss_attribution_json', 'TEXT')
    add_column_safe('ops__quotes', 'payment_terms_days', 'INTEGER')
    
    # Migrate Quote Outcome Events table (Wizard fields)
    add_column_safe('ops__quote_outcome_events', 'original_price', 'REAL')
    add_column_safe('ops__quote_outcome_events', 'final_price', 'REAL')
    add_column_safe('ops__quote_outcome_events', 'price_changed', 'BOOLEAN')
    add_column_safe('ops__quote_outcome_events', 'original_leadtime_days', 'INTEGER')
    add_column_safe('ops__quote_outcome_events', 'final_leadtime_days', 'INTEGER')
    add_column_safe('ops__quote_outcome_events', 'leadtime_changed', 'BOOLEAN')
    add_column_safe('ops__quote_outcome_events', 'original_terms_days', 'INTEGER')
    add_column_safe('ops__quote_outcome_events', 'final_terms_days', 'INTEGER')
    add_column_safe('ops__quote_outcome_events', 'terms_changed', 'BOOLEAN')
    add_column_safe('ops__quote_outcome_events', 'other_notes', 'TEXT')
    add_column_safe('ops__quote_outcome_events', 'wizard_completed', 'BOOLEAN')
    add_column_safe('ops__quote_outcome_events', 'wizard_step_reached', 'INTEGER')
    
    # Migrate Quote History (Legacy compatibility)
    add_column_safe('ops__quote_history', 'tag_weights', 'TEXT')
    add_column_safe('ops__quote_history', 'user_feedback_tags', 'TEXT')
    add_column_safe('ops__quote_history', 'status', 'TEXT')
    add_column_safe('ops__quote_history', 'actual_runtime', 'REAL')
    add_column_safe('ops__quote_history', 'is_guild_submission', 'INTEGER')
    # guild_credit_earned migration removed (PHASE 1: Guild economics in Ops violates firewall)
    add_column_safe('ops__quote_history', 'submission_date', 'TEXT')
    add_column_safe('ops__quote_history', 'loss_reason', 'TEXT')
    add_column_safe('ops__quote_history', 'exported_at', 'TEXT')
    add_column_safe('ops__quote_history', 'material', 'TEXT')
    add_column_safe('ops__quote_history', 'is_compliant', 'INTEGER')
    add_column_safe('ops__quote_history', 'genesis_hash', 'TEXT')
    add_column_safe('ops__quote_history', 'process_routing', 'TEXT')
    add_column_safe('ops__quote_history', 'source_type', 'TEXT')
    add_column_safe('ops__quote_history', 'reference_image', 'TEXT')
    add_column_safe('ops__quote_history', 'quote_id', 'TEXT')
    add_column_safe('ops__quote_history', 'is_deleted', 'INTEGER')
    add_column_safe('ops__quote_history', 'handling_time', 'REAL')
    add_column_safe('ops__quote_history', 'win_notes', 'TEXT')
    add_column_safe('ops__quote_history', 'closed_at', 'TEXT')

    conn.commit()
    conn.close()
    
    init_default_tags()
    seed_default_data()
    seed_shop_config()

def init_default_tags() -> None:
    conn = get_connection()
    cursor = conn.cursor()
    defaults = [
        ('Rush Job', 'price_markup_percent', 1.50, 'transient', 'Market'),
        ('Expedite', 'price_markup_percent', 1.25, 'transient', 'Market'),
        ('Risk: Scrap High', 'price_markup_percent', 1.10, 'structural', 'Risk'),
        ('Friends / Family', 'price_markup_percent', 0.90, 'transient', 'Market'),
        ('Tight Tol', 'add_setup_minutes', 60.0, 'structural', 'Geometry'),
        ('Complex Fixture', 'add_setup_minutes', 120.0, 'structural', 'Geometry'),
        ('Heavy Deburr', 'add_setup_minutes', 30.0, 'structural', 'Finish'),
        ('Proto', 'set_shop_rate', 150.0, 'transient', 'Market'),
        ('Cust. Material', 'set_material_mult', 0.0, 'transient', 'Material'),
        ('Price Rounding', 'none', 0.0, 'transient', 'Strategy')
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO ops__custom_tags 
        (name, impact_type, impact_value, persistence_type, category) 
        VALUES (?, ?, ?, ?, ?)
    ''', defaults)
    conn.commit()
    conn.close()

def generate_default_quote_id() -> str:
    from datetime import datetime
    today = datetime.now().strftime('%Y%m%d')
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check quotes table first (primary truth)
    cursor.execute('''
        SELECT quote_id FROM ops__quotes 
        WHERE quote_id LIKE ? 
        ORDER BY quote_id DESC 
        LIMIT 1
    ''', (f'Q-{today}-%',))
    
    result = cursor.fetchone()
    if result and result[0]:
        try:
            last_seq = int(result[0].split('-')[-1])
            new_seq = last_seq + 1
        except (ValueError, IndexError):
            new_seq = 1
    else:
        new_seq = 1
    
    conn.close()
    return f'Q-{today}-{new_seq:03d}'


def upsert_part(
    genesis_hash: str,
    filename: str,
    fingerprint_json: str,
    volume: float,
    surface_area: float,
    dimensions_json: str,
    process_routing_json: str
) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM ops__parts WHERE genesis_hash = ?", (genesis_hash,))
    result = cursor.fetchone()
    
    if result:
        part_id = result[0]
        conn.close()
        return part_id
    else:
        cursor.execute("""
            INSERT INTO ops__parts (
                genesis_hash, filename, fingerprint_json, volume, 
                surface_area, dimensions_json, process_routing_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            genesis_hash, filename, fingerprint_json, volume,
            surface_area, dimensions_json, process_routing_json
        ))
        conn.commit()
        part_id = cursor.lastrowid
        conn.close()
        return part_id


def resolve_customer(name: str, email_domain: Optional[str]) -> tuple:
    """
    Resolve customer by domain or name, creating if necessary.
    
    Returns:
        (customer_id, metadata) where metadata contains:
        - resolution_action: "matched_domain" | "matched_name" | "created"
        - input_domain_present: bool
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    normalized_name = name.strip().title() if name else "Unknown Customer"
    input_domain_present = bool(email_domain)
    
    # Try domain match first
    if email_domain:
        cursor.execute("SELECT id FROM ops__customers WHERE domain = ? LIMIT 1", (email_domain,))
        result = cursor.fetchone()
        if result:
            conn.close()
            return (result[0], {
                'resolution_action': 'matched_domain',
                'input_domain_present': input_domain_present
            })
    
    # Try name match
    cursor.execute("SELECT id FROM ops__customers WHERE name = ? LIMIT 1", (normalized_name,))
    result = cursor.fetchone()
    if result:
        conn.close()
        return (result[0], {
            'resolution_action': 'matched_name',
            'input_domain_present': input_domain_present
        })
    
    # Create new customer
    cursor.execute("""
        INSERT INTO ops__customers (name, domain, corporate_tags_json)
        VALUES (?, ?, ?)
    """, (normalized_name, email_domain if email_domain else "unknown", "[]"))
    
    customer_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return (customer_id, {
        'resolution_action': 'created',
        'input_domain_present': input_domain_present
    })


def resolve_contact(name: str, email: str, customer_id: int, phone: Optional[str] = None) -> tuple:
    """
    Smart Contact Resolution.
    1. If Email provided: Match by Email.
    2. If NO Email: Match by Name + CustomerID.
    3. If No Match: Create new.
    
    Returns:
        (contact_id, metadata) where metadata contains:
        - resolution_action: "matched_email" | "matched_name_customer" | "created"
        - roaming: bool (True if email matched but customer changed)
        - old_customer_id: int | None (if roaming)
        - placeholder_email: bool (True if generated placeholder)
    """
    import uuid
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Normalize inputs
    normalized_name = name.strip().title() if name else "Unknown Contact"
    normalized_email = email.strip().lower() if email else ""
    
    # Strategy 1: Match by Email (Strongest Signal)
    if normalized_email:
        cursor.execute(
            "SELECT id, current_customer_id FROM ops__contacts WHERE email = ? LIMIT 1",
            (normalized_email,)
        )
        result = cursor.fetchone()
        
        if result:
            contact_id = result[0]
            old_customer_id = result[1]
            
            # Handle "Roaming Buyer" (changed jobs)
            roaming = (old_customer_id != customer_id)
            if roaming:
                cursor.execute(
                    "UPDATE ops__contacts SET current_customer_id = ?, name = ?, phone = ? WHERE id = ?",
                    (customer_id, normalized_name, phone, contact_id)
                )
                conn.commit()
            
            conn.close()
            return (contact_id, {
                'resolution_action': 'matched_email',
                'roaming': roaming,
                'old_customer_id': old_customer_id if roaming else None,
                'placeholder_email': False
            })

    # Strategy 2: Match by Name + Customer ID (Weak Signal, but necessary for no-email contacts)
    # This prevents "Alice" and "Bob" at the same company from merging into one "Anonymous" record
    cursor.execute(
        "SELECT id FROM ops__contacts WHERE name = ? AND current_customer_id = ? LIMIT 1",
        (normalized_name, customer_id)
    )
    result = cursor.fetchone()
    
    if result:
        contact_id = result[0]
        # Update phone if provided and currently empty
        if phone:
            cursor.execute("UPDATE ops__contacts SET phone = ? WHERE id = ? AND phone IS NULL", (phone, contact_id))
            conn.commit()
        conn.close()
        return (contact_id, {
            'resolution_action': 'matched_name_customer',
            'roaming': False,
            'old_customer_id': None,
            'placeholder_email': False
        })
    
    # Strategy 3: Create New Contact
    # If no email, generate a TRULY unique placeholder to prevent future lookup collisions
    placeholder_generated = False
    if not normalized_email:
        # Format: anon-{customer_id}-{uuid}@placeholder.com
        # Includes UUID to ensure Alice and Bob get different emails
        unique_suffix = str(uuid.uuid4())[:8]
        final_email = f"anon-{customer_id}-{unique_suffix}@placeholder.com"
        placeholder_generated = True
    else:
        final_email = normalized_email

    cursor.execute("""
        INSERT INTO ops__contacts (name, email, phone, behavior_tags_json, current_customer_id)
        VALUES (?, ?, ?, ?, ?)
    """, (
        normalized_name,
        final_email,
        phone,
        "[]",  # Empty tags
        customer_id
    ))
    
    contact_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return (contact_id, {
        'resolution_action': 'created',
        'roaming': False,
        'old_customer_id': None,
        'placeholder_email': placeholder_generated
    })


def create_quote(
    part_id: int,
    customer_id: int,
    contact_id: Optional[int],
    quote_id: str,
    user_id: Optional[int],
    material: str,
    system_price_anchor: float,
    final_quoted_price: float,
    quantity: int = 1,
    target_date: Optional[str] = None,
    notes: Optional[str] = None,
    variance_json: Optional[str] = None,
    pricing_tags_json: Optional[str] = None,
    physics_snapshot_json: Optional[str] = None,
    lead_time_date: Optional[str] = None,
    lead_time_days: Optional[int] = None,
    payment_terms_days: Optional[int] = 30,
    target_price_per_unit: Optional[float] = None,
    price_breaks_json: Optional[str] = None,
    outside_processing_json: Optional[str] = None,
    quality_requirements_json: Optional[str] = None,
    part_marking_json: Optional[str] = None,
    status: str = 'Draft'
) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    
    normalized_material, is_compliant = validate_material(material if material else 'Unknown')
    if not quote_id or not quote_id.strip():
        quote_id = generate_default_quote_id()
    
    cursor.execute("""
        INSERT INTO ops__quotes (
            part_id, customer_id, contact_id, user_id, quote_id, material,
            system_price_anchor, final_quoted_price, quantity, target_date, notes,
            variance_json, pricing_tags_json, physics_snapshot_json,
            lead_time_date, lead_time_days, payment_terms_days, target_price_per_unit,
            price_breaks_json, outside_processing_json, quality_requirements_json,
            part_marking_json, status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        part_id, customer_id, contact_id, user_id, quote_id, normalized_material,
        system_price_anchor, final_quoted_price, quantity, target_date, notes,
        variance_json, pricing_tags_json, physics_snapshot_json,
        lead_time_date, lead_time_days, payment_terms_days, target_price_per_unit,
        price_breaks_json, outside_processing_json, quality_requirements_json,
        part_marking_json, status
    ))
    
    quote_record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return quote_record_id


def get_unclosed_quotes() -> List[Dict[str, Any]]:
    """
    Get all quotes with unclosed outcomes.
    
    Per wizard spec: Unclosed = no outcome event OR outcome_type='NO_RESPONSE'
    Sort oldest → newest (by created_at).
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Find quotes WITHOUT any outcome events OR with NO_RESPONSE (stays on exception list)
        cursor.execute("""
            SELECT 
                id,
                quote_id,
                final_quoted_price,
                lead_time_days,
                payment_terms_days,
                status,
                created_at,
                customer_name,
                age_days
            FROM view_ops_unclosed_quotes
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        unclosed = []
        for row in rows:
            unclosed.append({
                'id': row['id'],
                'quote_id': row['quote_id'],
                'final_quoted_price': row['final_quoted_price'],
                'lead_time_days': row['lead_time_days'] or 0,
                'payment_terms_days': row['payment_terms_days'] or 30,
                'status': row['status'],
                'age_days': row['age_days'],
                'customer_name': row['customer_name'] or 'Unknown'
            })
        
        return unclosed
        
    except Exception as e:
        conn.close()
        return []


def save_quote_outcome_wizard(
    quote_id: int,
    outcome_type: str,
    actor_user_id: Optional[int] = None,
    original_price: Optional[float] = None,
    final_price: Optional[float] = None,
    original_leadtime: Optional[int] = None,
    final_leadtime: Optional[int] = None,
    original_terms: Optional[int] = None,
    final_terms: Optional[int] = None,
    other_notes: Optional[str] = None,
    wizard_step: int = 0
) -> int:
    """
    Save/update outcome event with wizard data (progressive auto-save).
    
    Per wizard spec: Auto-saves after every response, stores original vs final values.
    Returns event_id for progressive updates.
    
    Args:
        quote_id: Quote ID
        outcome_type: 'WON' | 'LOST' | 'NO_RESPONSE'
        wizard_step: Current step reached (0=initial, 1=price, 2=leadtime, 3=terms, 4=other)
    
    Returns:
        event_id if saved, 0 on error
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if event already exists for this quote (progressive update)
        cursor.execute("""
            SELECT id FROM ops__quote_outcome_events 
            WHERE quote_id = ? 
            ORDER BY saved_at DESC 
            LIMIT 1
        """, (quote_id,))
        existing = cursor.fetchone()
        
        if existing:
            # UPDATE existing event (progressive auto-save)
            event_id = existing[0]
            
            updates = ["saved_at = ?"]
            params = [datetime.now().isoformat()]
            
            if final_price is not None:
                updates.append("final_price = ?")
                updates.append("price_changed = ?")
                params.append(final_price)
                params.append(original_price != final_price if original_price else False)
            
            if final_leadtime is not None:
                updates.append("final_leadtime_days = ?")
                updates.append("leadtime_changed = ?")
                params.append(final_leadtime)
                params.append(original_leadtime != final_leadtime if original_leadtime else False)
            
            if final_terms is not None:
                updates.append("final_terms_days = ?")
                updates.append("terms_changed = ?")
                params.append(final_terms)
                params.append(original_terms != final_terms if original_terms else False)
            
            if other_notes is not None:
                updates.append("other_notes = ?")
                params.append(other_notes)
            
            updates.append("wizard_step_reached = ?")
            params.append(wizard_step)
            
            if wizard_step >= 4:  # Completed all steps
                updates.append("wizard_completed = ?")
                params.append(True)
            
            params.append(event_id)
            
            cursor.execute(f"""
                UPDATE ops__quote_outcome_events 
                SET {', '.join(updates)}
                WHERE id = ?
            """, params)
            
        else:
            # INSERT new event (first save)
            cursor.execute("""
                INSERT INTO ops__quote_outcome_events (
                    quote_id, outcome_type, actor_user_id, saved_at,
                    original_price, final_price, price_changed,
                    original_leadtime_days, final_leadtime_days, leadtime_changed,
                    original_terms_days, final_terms_days, terms_changed,
                    other_notes, wizard_step_reached, wizard_completed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                quote_id, outcome_type, actor_user_id, datetime.now().isoformat(),
                original_price, final_price, 
                (original_price != final_price) if (original_price and final_price) else False,
                original_leadtime, final_leadtime,
                (original_leadtime != final_leadtime) if (original_leadtime and final_leadtime) else False,
                original_terms, final_terms,
                (original_terms != final_terms) if (original_terms and final_terms) else False,
                other_notes, wizard_step, wizard_step >= 4
            ))
            
            event_id = cursor.lastrowid
        
        # Update quotes.status for legacy compatibility (except NO_RESPONSE)
        if outcome_type == 'WON':
            new_status = 'Won'
            cursor.execute("""
                UPDATE ops__quotes 
                SET status = ?, closed_at = ?
                WHERE id = ?
            """, (new_status, datetime.now().isoformat(), quote_id))
        elif outcome_type == 'LOST':
            new_status = 'Lost'
            cursor.execute("""
                UPDATE ops__quotes 
                SET status = ?, closed_at = ?
                WHERE id = ?
            """, (new_status, datetime.now().isoformat(), quote_id))
        # NO_RESPONSE: Don't update status, stays on exception list
        
        conn.commit()
        conn.close()
        return event_id
        
    except Exception as e:
        print(f"[ERROR] Failed to save wizard outcome: {e}")
        conn.rollback()
        conn.close()
        return 0


def update_quote_status_simple(
    quote_id: int, 
    status: str,
    win_notes: Optional[str] = None,
    loss_reason: Optional[str] = None,
    win_attribution: Optional[Dict[str, Any]] = None,
    loss_attribution: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Updates quote status in the 'quotes' table (4-Table Identity Model).
    Handles Deal Closer fields + structured attribution.
    
    Args:
        quote_id: Quote ID to update
        status: New status ('Draft', 'Sent', 'Won', 'Lost')
        win_notes: Optional free-form win notes
        loss_reason: Optional free-form loss reason
        win_attribution: Structured win data (what changed, why won)
        loss_attribution: Structured loss data (loss reasons, competitor info)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM ops__quotes WHERE id = ?", (quote_id,))
        if not cursor.fetchone():
            conn.close()
            return False
        
        updates = ["status = ?", "updated_at = ?"]
        params = [status, datetime.now().isoformat()]
        
        if status in ('Won', 'Lost'):
            updates.append("closed_at = ?")
            params.append(datetime.now().isoformat())
        else:
            # Revert to Draft/Sent: clear closure data
            updates.append("closed_at = NULL")
            updates.append("win_notes = NULL")
            updates.append("loss_reason = NULL")
            updates.append("win_attribution_json = NULL")
            updates.append("loss_attribution_json = NULL")
        
        if win_notes and status == 'Won':
            updates.append("win_notes = ?")
            params.append(win_notes)
        
        if loss_reason and status == 'Lost':
            updates.append("loss_reason = ?")
            params.append(loss_reason)
        
        # Structured attribution (new)
        if win_attribution and status == 'Won':
            import json
            updates.append("win_attribution_json = ?")
            params.append(json.dumps(win_attribution))
        
        if loss_attribution and status == 'Lost':
            import json
            updates.append("loss_attribution_json = ?")
            params.append(json.dumps(loss_attribution))
        
        params.append(quote_id)
        
        query = f"UPDATE ops__quotes SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to update quote status: {e}")
        conn.rollback()
        conn.close()
        return False


def get_all_history() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    
    # Join quotes with parts, customers, and contacts
    cursor.execute("""
        SELECT 
            q.id, q.quote_id, q.material, q.system_price_anchor, q.final_quoted_price,
            q.variance_json, q.pricing_tags_json, q.status, q.created_at, q.user_id,
            q.quantity, q.target_date, q.notes,
            p.id as part_id, p.genesis_hash, p.filename, p.fingerprint_json, 
            p.volume, p.surface_area, p.dimensions_json, p.process_routing_json,
            cu.id as customer_id, cu.name as customer_name, cu.domain as customer_domain,
            co.id as contact_id, co.name as contact_name, co.email as contact_email
        FROM ops__quotes q
        JOIN ops__parts p ON q.part_id = p.id
        LEFT JOIN ops__customers cu ON q.customer_id = cu.id
        LEFT JOIN ops__contacts co ON q.contact_id = co.id
        ORDER BY q.created_at DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    records = []
    for row in rows:
        record = {
            'id': row['id'],
            'quote_id': row['quote_id'],
            'material': row['material'],
            'system_price_anchor': row['system_price_anchor'],
            'final_quoted_price': row['final_quoted_price'],
            'variance_json': json.loads(row['variance_json']) if row['variance_json'] else None,
            'pricing_tags_json': json.loads(row['pricing_tags_json']) if row['pricing_tags_json'] else {},
            'status': row['status'],
            'timestamp': row['created_at'],
            'user_id': row['user_id'],
            'quantity': row['quantity'],
            'target_date': row['target_date'],
            'notes': row['notes'],
            'part_id': row['part_id'],
            'genesis_hash': row['genesis_hash'],
            'filename': row['filename'],
            'fingerprint': json.loads(row['fingerprint_json']) if row['fingerprint_json'] else [],
            'volume': row['volume'],
            'surface_area': row['surface_area'],
            'dimensions': json.loads(row['dimensions_json']) if row['dimensions_json'] else {},
            'process_routing': json.loads(row['process_routing_json']) if row['process_routing_json'] else [],
            'customer_id': row['customer_id'],
            'customer_name': row['customer_name'],
            'customer_domain': row['customer_domain'],
            'contact_id': row['contact_id'],
            'contact_name': row['contact_name'],
            'contact_email': row['contact_email'],
            # Legacy mapping
            'final_price': row['final_quoted_price'],
            'anchor_price': row['system_price_anchor'],
            'tag_weights': json.loads(row['pricing_tags_json']) if row['pricing_tags_json'] else {}
        }
        records.append(record)
    
    return records

def get_all_tags() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, impact_type, impact_value, persistence_type, category FROM ops__custom_tags ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    tags = []
    for row in rows:
        tag_dict = dict(row)
        tag_dict['is_active'] = True
        tag_dict['default_markup'] = tag_dict.get('impact_value', 0) if tag_dict.get('impact_type') == 'price_markup_percent' else 0
        tags.append(tag_dict)
    return tags

def create_custom_tag(name: str, impact_type: str, impact_value: float, persistence_type: str = 'transient', category: str = 'General') -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ops__custom_tags (name, impact_type, impact_value, persistence_type, category) VALUES (?, ?, ?, ?, ?)", 
                   (name, impact_type, impact_value, persistence_type, category))
    rowid = cursor.lastrowid
    conn.commit()
    conn.close()
    return rowid

def delete_custom_tag(tag_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM ops__custom_tags WHERE id = ?", (tag_id,))
    conn.commit()
    conn.close()

def update_custom_tag(tag_id: int, name: str, impact_type: str, impact_value: float, category: str) -> None:
    conn = get_connection()
    conn.execute("UPDATE ops__custom_tags SET name=?, impact_type=?, impact_value=?, category=? WHERE id=?", 
                 (name, impact_type, impact_value, category, tag_id))
    conn.commit()
    conn.close()

def update_quote_status(quote_id: int, status: str, actual_runtime: Optional[float] = None, is_guild_submission: bool = False, loss_reason: Optional[str] = None) -> Tuple[float, bool]:
    """
    Legacy function for quote_history table (Partner Mode credit logic).
    The new Deal Closer logic uses update_quote_status_simple.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # PHASE 1 REMEDIATION: guild_credit_earned check removed (field deleted)
    
    updates = ["status = ?"]
    params = [status]
    
    if actual_runtime is not None:
        updates.append("actual_runtime = ?")
        params.append(actual_runtime)
    
    if loss_reason is not None:
        loss_json = json.dumps(loss_reason) if isinstance(loss_reason, list) else json.dumps([str(loss_reason)])
        updates.append("loss_reason = ?")
        params.append(loss_json)
        
    # PHASE 1 REMEDIATION: Guild credit calculation removed
    # Credits/caps are Guild economics - Ops must not compute them
    # Ops only tracks export intent (is_guild_submission field retained for Phase 2 refactor)
    
    updates.append("is_guild_submission = ?")
    params.append(1 if is_guild_submission else 0)
    # guild_credit_earned field removed - violates firewall
    
    if is_guild_submission and status in ('Won', 'Lost'):
        updates.append("submission_date = ?")
        params.append(datetime.now().isoformat())
        
    params.append(quote_id)
    cursor.execute(f"UPDATE ops__quote_history SET {', '.join(updates)} WHERE id = ?", params)
    
    # Also sync status to the main quotes table
    try:
        cursor.execute("UPDATE ops__quotes SET status = ?, updated_at = ? WHERE id = ?", (status, datetime.now().isoformat(), quote_id))
    except:
        pass
        
    conn.commit()
    conn.close()
    # PHASE 1: Return dummy values (credits removed from Ops, computed by Guild)
    return (0.0, False)

def get_pending_export_count() -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM ops__quote_history 
        WHERE is_guild_submission = 1 AND status IN ('Won', 'Lost') 
        AND exported_at IS NULL AND is_compliant = 1 AND is_deleted = 0
    """)
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_pending_exports() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, status, final_price, anchor_price, actual_runtime, 
               setup_time, loss_reason, tag_weights, timestamp, material, genesis_hash, process_routing
        FROM ops__quote_history 
        WHERE is_guild_submission = 1 AND status IN ('Won', 'Lost')
        AND exported_at IS NULL AND is_compliant = 1 AND is_deleted = 0
        ORDER BY id ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    records = []
    for row in rows:
        tag_weights = json.loads(row['tag_weights']) if row['tag_weights'] else {}
        loss_reason = json.loads(row['loss_reason']) if row['loss_reason'] else row['loss_reason']
        process_routing = json.loads(row['process_routing']) if row['process_routing'] else []
        
        records.append({
            'id': row['id'],
            'status': row['status'],
            'final_price': row['final_price'],
            'anchor_price': row['anchor_price'],
            'actual_runtime': row['actual_runtime'],
            'setup_time': row['setup_time'],
            'loss_reason': loss_reason,
            'tag_weights': tag_weights,
            'timestamp': row['timestamp'],
            'material': row['material'] if row['material'] else 'Unknown',
            'genesis_hash': row['genesis_hash'],
            'process_routing': process_routing
        })
    return records

def mark_as_exported(quote_ids: List[int]) -> None:
    if not quote_ids: return
    conn = get_connection()
    placeholders = ','.join(['?'] * len(quote_ids))
    conn.execute(f"UPDATE ops__quote_history SET exported_at = ? WHERE id IN ({placeholders})", 
                 [datetime.now().isoformat()] + quote_ids)
    conn.commit()
    conn.close()

# get_monthly_ledger() removed - PHASE 1 REMEDIATION
# Guild credit retrieval violates firewall (Guild economics belong in Guild product)

def validate_material(input_name: str) -> Tuple[str, bool]:
    if not input_name or not input_name.strip():
        return ('Unknown', False)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM ops__materials")
    valid_materials = [row[0] for row in cursor.fetchall()]
    conn.close()
    input_normalized = input_name.strip()
    for valid_name in valid_materials:
        if input_normalized.lower() == valid_name.lower():
            return (valid_name, True)
    return (input_normalized, False)

def update_quote_material(quote_id: int, new_material: str) -> bool:
    normalized, is_compliant = validate_material(new_material)
    if not is_compliant: return False
    conn = get_connection()
    conn.execute("UPDATE ops__quote_history SET material = ?, is_compliant = 1 WHERE id = ?", (normalized, quote_id))
    # Also update main quotes table
    conn.execute("UPDATE ops__quotes SET material = ? WHERE id = ?", (normalized, quote_id))
    conn.commit()
    conn.close()
    return True

def get_material_cost(name: str) -> Optional[float]:
    """Get the cost per cubic inch for a material."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT cost_per_cubic_inch FROM ops__materials WHERE name=?", (name,))
    res = cur.fetchone()
    conn.close()
    return res[0] if res else None

def get_material_score(name: str) -> float:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT machinability_score FROM ops__materials WHERE name=?", (name,))
    res = cur.fetchone()
    conn.close()
    return res[0] if res else 1.0

def get_all_materials() -> List[str]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM ops__materials ORDER BY name")
    materials = [row[0] for row in cursor.fetchall()]
    conn.close()
    return materials

def fix_quote_compliance(quote_id: int, new_material: str) -> Tuple[bool, str]:
    normalized, is_compliant = validate_material(new_material)
    if not is_compliant: return (False, "Material is still non-compliant")
    conn = get_connection()
    conn.execute("UPDATE ops__quote_history SET material = ?, is_compliant = 1 WHERE id = ?", (normalized, quote_id))
    conn.execute("UPDATE ops__quotes SET material = ? WHERE id = ?", (normalized, quote_id))
    conn.commit()
    conn.close()
    return (True, "Material updated successfully")

def soft_delete_quote(quote_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    
    # Soft delete in both tables
    cursor.execute("SELECT id FROM ops__quote_history WHERE id = ? AND is_deleted = 0", (quote_id,))
    if cursor.fetchone():
        cursor.execute("UPDATE ops__quote_history SET is_deleted = 1 WHERE id = ?", (quote_id,))
    
    # Add is_deleted column to quotes table if it doesn't exist
    try:
        cursor.execute("ALTER TABLE ops__quotes ADD COLUMN is_deleted INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    
    cursor.execute("SELECT id FROM ops__quotes WHERE id = ?", (quote_id,))
    if cursor.fetchone():
        cursor.execute("UPDATE ops__quotes SET is_deleted = 1 WHERE id = ?", (quote_id,))
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

def seed_default_data() -> None:
    conn = get_connection()
    cur = conn.cursor()
    defaults = [
        ('Aluminum 6061', 0.30, 1.0),
        ('Steel 1018', 0.25, 1.8),
        ('Stainless 304', 0.65, 2.5),
        ('Customer Supplied', 0.00, 1.0)
    ]
    cur.executemany("INSERT OR IGNORE INTO ops__materials (name, cost_per_cubic_inch, machinability_score) VALUES (?,?,?)", defaults)
    conn.commit()
    conn.close()

def seed_shop_config() -> None:
    conn = get_connection()
    cur = conn.cursor()
    defaults = [
        ('base_mrr', '30.0', 'Material Removal Rate for Aluminum 6061'),
        ('setup_time_minutes', '60.0', 'Default setup time'),
        ('saw_kerf', '0.125', 'Stock buffer'),
        ('min_hand_time', '5.0', 'Minimum hand time'),
        ('material_markup', '1.2', 'Material markup'),
        ('shop_rate_standard', '75.0', 'Standard shop rate'),
        ('shop_rate_marginal', '45.0', 'Marginal shop rate'),
        ('default_handling_time', '0.5', 'Default load/unload time'),
        # Shop Branding (PDF Headers) - Per EXECUTION_CHAT_BRIEF.md
        ('shop_name', 'Precision Machine Works', 'Company name for PDFs'),
        ('shop_address', '123 Industrial Way, City, ST 12345', 'Address for PDFs'),
        ('shop_phone', '(555) 123-4567', 'Contact phone'),
        ('shop_email', 'quotes@precisionworks.com', 'Contact email'),
        ('shop_logo_path', '', 'Optional logo path (future use)')
    ]
    cur.executemany("INSERT OR IGNORE INTO ops__shop_config (key, value, description) VALUES (?, ?, ?)", defaults)
    conn.commit()
    conn.close()

def get_config(key: str, default: Any = None, value_type: type = float) -> Any:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT value FROM ops__shop_config WHERE key = ?", (key,))
        result = cursor.fetchone()
        if result:
            val = result[0]
            if value_type == bool: return val.lower() in ('true', '1', 'yes')
            if value_type == int: return int(float(val))
            if value_type == float: return float(val)
            return val
        return default
    except:
        return default
    finally:
        conn.close()

def set_config(key: str, value: Any, description: str = None) -> bool:
    conn = get_connection()
    try:
        if description:
            conn.execute("INSERT OR REPLACE INTO ops__shop_config (key, value, description, updated_at) VALUES (?, ?, ?, datetime('now'))", (key, str(value), description))
        else:
            conn.execute("INSERT OR REPLACE INTO ops__shop_config (key, value, updated_at) VALUES (?, ?, datetime('now'))", (key, str(value)))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


# ============================================================================
# CUSTOMER MANAGEMENT FUNCTIONS (Phase 5.6)
# ============================================================================

def get_all_customers():
    """
    Get all customers with summary counts.
    
    Returns:
        list[dict]: List of customer summaries
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            c.id,
            c.name,
            c.domain,
            c.created_at,
            COUNT(DISTINCT cp.genesis_hash) as parts_count,
            COUNT(DISTINCT cc.contact_id) as contacts_count,
            COUNT(DISTINCT q.id) as quotes_count,
            MAX(q.created_at) as last_active
        FROM ops__customers c
        LEFT JOIN customer_parts cp ON c.id = cp.customer_id
        LEFT JOIN contact_companies cc ON c.id = cc.customer_id
        LEFT JOIN ops__quotes q ON c.id = q.customer_id
        GROUP BY c.id
        ORDER BY last_active DESC, c.name ASC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    customers = []
    for row in rows:
        customers.append({
            'id': row[0],
            'company_name': row[1],
            'domain': row[2],
            'created_at': row[3],
            'parts_count': row[4],
            'contacts_count': row[5],
            'quotes_count': row[6],
            'last_active': row[7]
        })
    
    return customers


def get_customer_details(customer_id):
    """
    Get full customer details including parts, contacts, and history.
    
    Args:
        customer_id (int): Customer ID
    
    Returns:
        dict: Full customer data with nested parts, contacts, and history
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Get customer basic info
    cursor.execute("""
        SELECT id, name, domain, created_at
        FROM ops__customers
        WHERE id = ?
    """, (customer_id,))
    
    customer_row = cursor.fetchone()
    if not customer_row:
        conn.close()
        return None
    
    customer = {
        'id': customer_row[0],
        'company_name': customer_row[1],
        'domain': customer_row[2],
        'created_at': customer_row[3],
        'parts': [],
        'contacts': [],
        'history': [],
        'summary': {}
    }
    
    # 2. Get parts associated with this customer
    cursor.execute("""
        SELECT 
            p.genesis_hash,
            p.filename,
            cp.total_quotes,
            cp.first_quoted_at
        FROM customer_parts cp
        JOIN ops__parts p ON cp.genesis_hash = p.genesis_hash
        WHERE cp.customer_id = ?
        ORDER BY cp.first_quoted_at DESC
        LIMIT 10
    """, (customer_id,))
    
    for row in cursor.fetchall():
        customer['parts'].append({
            'genesis_hash': row[0],
            'filename': row[1],
            'total_quotes': row[2],
            'first_quoted_at': row[3]
        })
    
    # 3. Get contacts for this customer
    cursor.execute("""
        SELECT 
            co.id,
            co.name,
            co.email,
            co.phone,
            cc.is_primary,
            COUNT(q.id) as quote_count
        FROM contact_companies cc
        JOIN ops__contacts co ON cc.contact_id = co.id
        LEFT JOIN ops__quotes q ON co.id = q.contact_id
        WHERE cc.customer_id = ?
        GROUP BY co.id
        ORDER BY cc.is_primary DESC, co.name ASC
    """, (customer_id,))
    
    for row in cursor.fetchall():
        customer['contacts'].append({
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'phone': row[3],
            'is_primary': bool(row[4]),
            'quote_count': row[5]
        })
    
    # 4. Get combined quote/job history (last 10)
    cursor.execute("""
        SELECT 
            q.quote_id,
            q.final_quoted_price,
            q.status,
            q.created_at,
            co.name
        FROM ops__quotes q
        LEFT JOIN ops__contacts co ON q.contact_id = co.id
        WHERE q.customer_id = ?
        ORDER BY q.created_at DESC
        LIMIT 10
    """, (customer_id,))
    
    for row in cursor.fetchall():
        customer['history'].append({
            'quote_id': row[0],
            'price': row[1],
            'status': row[2],
            'date': row[3],
            'contact_name': row[4]
        })
    
    # 5. Get summary statistics
    cursor.execute("""
        SELECT 
            COUNT(*) as total_quotes,
            SUM(CASE WHEN status = 'Won' THEN 1 ELSE 0 END) as won_count,
            SUM(CASE WHEN status = 'Lost' THEN 1 ELSE 0 END) as lost_count,
            SUM(CASE WHEN status IN ('Draft', 'Sent', 'In Review') THEN 1 ELSE 0 END) as unclosed_count,
            SUM(CASE WHEN status = 'Won' THEN final_quoted_price ELSE 0 END) as total_revenue
        FROM ops__quotes
        WHERE customer_id = ?
    """, (customer_id,))
    
    summary_row = cursor.fetchone()
    customer['summary'] = {
        'total_quotes': summary_row[0],
        'won_count': summary_row[1],
        'lost_count': summary_row[2],
        'unclosed_count': summary_row[3],
        'total_revenue': summary_row[4] or 0
    }
    
    conn.close()
    return customer


def create_customer(company_name, domain=None):
    """
    Create a new customer.
    
    Args:
        company_name (str): Company name
        domain (str, optional): Company domain (e.g., "spacex.com")
    
    Returns:
        int: New customer ID
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO ops__customers (name, domain)
        VALUES (?, ?)
    """, (company_name, domain))
    
    customer_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return customer_id


def update_customer(customer_id, company_name=None, domain=None):
    """
    Update customer information.
    
    Args:
        customer_id (int): Customer ID
        company_name (str, optional): New company name
        domain (str, optional): New domain
    
    Returns:
        bool: Success status
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if company_name is not None:
        updates.append("name = ?")
        params.append(company_name)
    
    if domain is not None:
        updates.append("domain = ?")
        params.append(domain)
    
    if not updates:
        conn.close()
        return False
    
    params.append(customer_id)
    
    cursor.execute(f"""
        UPDATE ops__customers
        SET {", ".join(updates)}
        WHERE id = ?
    """, params)
    
    conn.commit()
    conn.close()
    
    return True


def delete_customer(customer_id):
    """
    Delete a customer.
    Note: Will fail if there are quotes referencing this customer (FK constraint).
    
    Args:
        customer_id (int): Customer ID
    
    Returns:
        bool: Success status
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # First remove from junction tables
    cursor.execute("DELETE FROM customer_parts WHERE customer_id = ?", (customer_id,))
    cursor.execute("DELETE FROM contact_companies WHERE customer_id = ?", (customer_id,))
    
    # Then delete the customer
    cursor.execute("DELETE FROM ops__customers WHERE id = ?", (customer_id,))
    
    conn.commit()
    conn.close()
    
    return True


def create_contact_for_customer(customer_id, contact_name, email=None, phone=None, is_primary=False):
    """
    Create a new contact and link to customer.
    
    Args:
        customer_id (int): Customer ID
        contact_name (str): Contact name
        email (str, optional): Email
        phone (str, optional): Phone
        is_primary (bool): Is this the primary contact?
    
    Returns:
        int: New contact ID
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create contact (using 'name' and 'current_customer_id' per actual schema)
    cursor.execute("""
        INSERT INTO ops__contacts (name, email, phone, current_customer_id)
        VALUES (?, ?, ?, ?)
    """, (contact_name, email, phone, customer_id))
    
    contact_id = cursor.lastrowid
    
    # Link to customer via junction table
    cursor.execute("""
        INSERT INTO contact_companies (contact_id, customer_id, is_primary)
        VALUES (?, ?, ?)
    """, (contact_id, customer_id, 1 if is_primary else 0))
    
    conn.commit()
    conn.close()
    
    return contact_id


def update_contact(contact_id, contact_name=None, email=None, phone=None):
    """
    Update contact information.
    
    Args:
        contact_id (int): Contact ID
        contact_name (str, optional): New name
        email (str, optional): New email
        phone (str, optional): New phone
    
    Returns:
        bool: Success status
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if contact_name is not None:
        updates.append("name = ?")
        params.append(contact_name)
    
    if email is not None:
        updates.append("email = ?")
        params.append(email)
    
    if phone is not None:
        updates.append("phone = ?")
        params.append(phone)
    
    if not updates:
        conn.close()
        return False
    
    params.append(contact_id)
    
    cursor.execute(f"""
        UPDATE ops__contacts
        SET {", ".join(updates)}
        WHERE id = ?
    """, params)
    
    conn.commit()
    conn.close()
    
    return True


def get_contact_details(contact_id):
    """
    Get contact details by ID.
    
    Args:
        contact_id (int): Contact ID
    
    Returns:
        dict: Contact data or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, phone, current_customer_id FROM ops__contacts WHERE id = ?", (contact_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return {
        'id': row[0],
        'name': row[1],
        'email': row[2],
        'phone': row[3],
        'current_customer_id': row[4]
    }


def count_quotes_for_contact(contact_id):
    """
    Count quotes associated with a contact.
    
    Args:
        contact_id (int): Contact ID
    
    Returns:
        int: Number of quotes
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ops__quotes WHERE contact_id = ?", (contact_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count


def count_quotes_using_tag_name_approx(tag_name: str) -> int:
    """
    Count quotes approximately using a tag name (via JSON LIKE search).
    
    Note: This is approximate because it uses LIKE on JSON text.
    
    Args:
        tag_name (str): Tag name to search for
    
    Returns:
        int: Approximate count of quotes using this tag
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM ops__quotes 
        WHERE pricing_tags_json LIKE ?
    """, (f'%"{tag_name}"%',))
    count = cursor.fetchone()[0]
    conn.close()
    return count


def delete_contact(contact_id):
    """
    Delete a contact.
    Note: Will set quotes.contact_id to NULL if this contact has quotes.
    
    Args:
        contact_id (int): Contact ID
    
    Returns:
        bool: Success status
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # First remove from junction table
    cursor.execute("DELETE FROM contact_companies WHERE contact_id = ?", (contact_id,))
    
    # Then delete the contact (FK ON DELETE SET NULL will handle quotes)
    cursor.execute("DELETE FROM ops__contacts WHERE id = ?", (contact_id,))
    
    conn.commit()
    conn.close()
    
    return True


# =============================================================================
# LEDGER CORE: Operational Event Emission
# =============================================================================
# NOTE: Direct writes to cutter__operational_events are now handled by
#       cutter_ledger.boundary module (single authorized write path)

def emit_event(event_type: str, quote_id: Optional[int], event_data: Optional[Dict[str, Any]] = None) -> int:
    """
    Emit an operational event to the Cutter Ledger (append-only).
    
    DEPRECATED: This function now delegates to cutter_ledger.boundary.emit_cutter_event()
    for constitutional enforcement and boundary consolidation.
    
    CONSTITUTIONAL CONSTRAINTS:
    - C1 (Outcome Agnosticism): Event types must be descriptive, never evaluative
    - C4 (Irreversible Memory): Events cannot be edited or deleted (enforced by DB triggers)
    - C7 (Overrides Must Leave Scars): Override events preserve magnitude, frequency, persistence
    
    Args:
        event_type: Descriptive event name (e.g., "QUOTE_OVERRIDDEN", "JOB_STARTED")
        quote_id: Quote record ID (if applicable, None for non-quote events)
        event_data: JSON-serializable dict with event-specific data
    
    Returns:
        Event record ID
    
    Raises:
        ValueError: If event_type contains evaluative language (good/bad/healthy/risky)
    """
    # Delegate to consolidated boundary module
    from cutter_ledger.boundary import emit_cutter_event
    return emit_cutter_event(event_type, subject_ref=quote_id, event_data=event_data)


def get_events_for_quote(quote_id: int) -> List[Dict[str, Any]]:
    """
    Retrieve all operational events for a specific quote.
    
    DEPRECATED: Use cutter_ledger.boundary.get_events(subject_ref=...) instead.
    NOTE: Delegates to cutter_ledger.boundary for consolidated access.
    
    Returns events in chronological order (oldest first).
    """
    from cutter_ledger.boundary import get_events
    return get_events(subject_ref=quote_id)
#


def _run_db_mode_smoke_test() -> None:
    original = dict(os.environ)
    try:
        if "TEST_DB_PATH" in os.environ:
            del os.environ["TEST_DB_PATH"]
        validate_db_mode()

        test_path = Path(os.environ.get("TEMP", ".")) / "test_db_mode_guard.db"
        os.environ["TEST_DB_PATH"] = str(test_path)
        validate_db_mode()

        os.environ["TEST_DB_PATH"] = str(PROD_DB_PATH)
        try:
            validate_db_mode()
            raise SystemExit(1)
        except SystemExit:
            pass
        print("[DB MODE] Guard checks complete")
    finally:
        os.environ.clear()
        os.environ.update(original)


if __name__ == "__main__":
    _run_db_mode_smoke_test()