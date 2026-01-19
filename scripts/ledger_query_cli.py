#!/usr/bin/env python3
"""
Ledger Query CLI - Read-Only Interface

CONSTITUTIONAL CONSTRAINT: This script is READ-ONLY.
It MUST NEVER write, migrate, initialize, or reset the database.
It may only open an existing database and read from it.

Constitutional enforcement: Raw output only. No summaries, recommendations, 
alerts, health checks, or scoring. Makes data queryable, not actionable.

Usage:
    python scripts/ledger_query_cli.py state list-entities
    python scripts/ledger_query_cli.py state declarations --entity_ref org:acme/entity:customer:123
    python scripts/ledger_query_cli.py state open-deadlines
    python scripts/ledger_query_cli.py state ds1
    python scripts/ledger_query_cli.py state ds2
    python scripts/ledger_query_cli.py state ds5
    python scripts/ledger_query_cli.py state time-in-state
    python scripts/ledger_query_cli.py cutter events --subject_ref quote:123
    python scripts/ledger_query_cli.py cutter overrides

Environment:
    TEST_DB_PATH: If set, queries use isolated test database (for hermetic testing)
"""

import argparse
import json
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# CONSTITUTIONAL GUARD: Refuse to import any reset/initialization modules
# This ensures the query CLI cannot accidentally trigger database modifications
FORBIDDEN_IMPORTS = ['reset_db', 'test_setup']
for forbidden in FORBIDDEN_IMPORTS:
    if forbidden in sys.modules:
        print(json.dumps({
            "error": "CONSTITUTIONAL VIOLATION",
            "detail": f"Query CLI cannot import {forbidden} (read-only enforcement)",
            "remedy": "Query CLI must never write, migrate, or reset the database"
        }, indent=2), file=sys.stderr)
        sys.exit(1)

# Import query modules (read-only functions only)
from state_ledger import queries as state_queries
from state_ledger.boundary import get_declarations, query_unowned_entities, query_deferred_recognition
from cutter_ledger.boundary import get_events
import database

# CONSTITUTIONAL GUARD: Verify database exists before attempting queries
# Query CLI must NOT create or initialize databases
def verify_database_exists():
    """
    Verify that database exists before querying.
    
    Constitutional enforcement: Query CLI is read-only.
    It must refuse to run if database doesn't exist.
    """
    test_db_path = os.environ.get('TEST_DB_PATH')
    db_path = Path(test_db_path) if test_db_path else database.DB_PATH
    
    if not db_path.exists():
        print(json.dumps({
            "error": "Database not found",
            "db_path": str(db_path),
            "remedy": "Run 'python scripts/reset_db.py' to create database",
            "constitutional_note": "Query CLI is read-only and cannot create databases"
        }, indent=2), file=sys.stderr)
        sys.exit(1)
    
    return db_path


def output_json(data, pretty=True):
    """Output data as JSON (raw format, no interpretation)."""
    if pretty:
        print(json.dumps(data, indent=2, default=str))
    else:
        print(json.dumps(data, default=str))


def cmd_state_list_entities(args):
    """List all registered entities."""
    entities = state_queries.list_entities()
    output_json(entities, pretty=args.pretty)
    return 0


def cmd_state_latest_declarations(args):
    """Get latest declarations (most recent first)."""
    declarations = state_queries.get_latest_declarations(
        entity_ref=args.entity_ref,
        scope_ref=args.scope_ref,
        limit=args.limit
    )
    output_json(declarations, pretty=args.pretty)
    return 0


def cmd_state_open_deadlines(args):
    """Query open promise:deadline declarations."""
    declarations = state_queries.query_open_deadlines(db_path=database.resolve_db_path())
    output_json(declarations, pretty=args.pretty)
    return 0


def cmd_state_declarations(args):
    """Query declarations with full filtering."""
    declarations = get_declarations(
        entity_ref=args.entity_ref,
        scope_ref=args.scope_ref,
        actor_ref=args.actor_ref,
        limit=args.limit
    )
    output_json(declarations, pretty=args.pretty)
    return 0


def cmd_state_ds1(args):
    """Query DS-1: Persistent Continuity (2+ reaffirmations since last reclassification)."""
    entities = state_queries.query_persistent_continuity()
    output_json(entities, pretty=args.pretty)
    return 0


def cmd_state_ds2(args):
    """Query DS-2: Unowned Recognition (entities with no current owner)."""
    entities = query_unowned_entities()
    output_json(entities, pretty=args.pretty)
    return 0


def cmd_state_ds5(args):
    """Query DS-5: Deferred Recognition (entities past cadence window)."""
    entities = query_deferred_recognition()
    output_json(entities, pretty=args.pretty)
    return 0


def cmd_state_time_in_state(args):
    """Query latest declarations with time-in-state visibility."""
    entities = state_queries.query_time_in_state()
    output_json(entities, pretty=args.pretty)
    return 0


def cmd_cutter_events(args):
    """Query Cutter Ledger events."""
    events = get_events(
        subject_ref=args.subject_ref,
        event_type=args.event_type
    )
    
    # Apply limit client-side if specified
    if args.limit and args.limit > 0:
        events = events[:args.limit]
    
    output_json(events, pretty=args.pretty)
    return 0


def cmd_cutter_overrides(args):
    """Query override events (delegate to existing script)."""
    # Delegate to existing query_override_events.py
    override_script = Path(__file__).parent.parent / "query_override_events.py"
    
    if not override_script.exists():
        print("Error: query_override_events.py not found", file=sys.stderr)
        return 1
    
    import subprocess
    
    # Pass TEST_DB_PATH if set
    env = os.environ.copy()
    
    result = subprocess.run(
        [sys.executable, str(override_script)],
        env=env,
        capture_output=True,
        text=True
    )
    
    print(result.stdout, end='')
    if result.stderr:
        print(result.stderr, end='', file=sys.stderr)
    
    return result.returncode


def main():
    # CONSTITUTIONAL GUARD: Verify database exists (read-only enforcement)
    verify_database_exists()
    
    parser = argparse.ArgumentParser(
        description="Ledger Query CLI - Read-only interface for Cutter Ledger and State Ledger",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # State Ledger
  %(prog)s state list-entities
  %(prog)s state latest-declarations --entity_ref org:acme/entity:customer:123
  %(prog)s state declarations --scope_ref org:acme/scope:weekly --limit 5
  %(prog)s state ds1
  %(prog)s state ds2
  %(prog)s state ds5
  %(prog)s state time-in-state
  
  # Cutter Ledger
  %(prog)s cutter events --subject_ref quote:123
  %(prog)s cutter events --event_type quote_overridden --limit 10
  %(prog)s cutter overrides
  
Environment:
  TEST_DB_PATH    Path to test database (for hermetic testing)
        """
    )
    
    parser.add_argument(
        '--pretty',
        action='store_true',
        default=True,
        help='Pretty-print JSON output (default: True)'
    )
    
    parser.add_argument(
        '--no-pretty',
        action='store_false',
        dest='pretty',
        help='Compact JSON output'
    )
    
    subparsers = parser.add_subparsers(dest='ledger', help='Ledger to query')
    
    # ====== STATE LEDGER COMMANDS ======
    state_parser = subparsers.add_parser('state', help='Query State Ledger')
    state_subparsers = state_parser.add_subparsers(dest='command', help='State Ledger command')
    
    # state list-entities
    state_list_entities = state_subparsers.add_parser(
        'list-entities',
        help='List all registered entities'
    )
    state_list_entities.set_defaults(func=cmd_state_list_entities)
    
    # state latest-declarations
    state_latest = state_subparsers.add_parser(
        'latest-declarations',
        help='Get latest declarations (most recent first)'
    )
    state_latest.add_argument('--entity_ref', help='Filter by entity reference')
    state_latest.add_argument('--scope_ref', help='Filter by scope reference')
    state_latest.add_argument('--limit', type=int, default=10, help='Max results (default: 10)')
    state_latest.set_defaults(func=cmd_state_latest_declarations)

    # state open-deadlines
    state_open_deadlines = state_subparsers.add_parser(
        'open-deadlines',
        help='Query open promise:deadline declarations'
    )
    state_open_deadlines.set_defaults(func=cmd_state_open_deadlines)
    
    # state declarations
    state_decls = state_subparsers.add_parser(
        'declarations',
        help='Query declarations with full filtering'
    )
    state_decls.add_argument('--entity_ref', help='Filter by entity reference')
    state_decls.add_argument('--scope_ref', help='Filter by scope reference')
    state_decls.add_argument('--actor_ref', help='Filter by declaring actor reference')
    state_decls.add_argument('--limit', type=int, help='Max results')
    state_decls.set_defaults(func=cmd_state_declarations)
    
    # state ds1
    state_ds1 = state_subparsers.add_parser(
        'ds1',
        help='Query DS-1: Persistent Continuity (2+ reaffirmations)'
    )
    state_ds1.set_defaults(func=cmd_state_ds1)
    
    # state ds2
    state_ds2 = state_subparsers.add_parser(
        'ds2',
        help='Query DS-2: Unowned Recognition (no current owner)'
    )
    state_ds2.set_defaults(func=cmd_state_ds2)
    
    # state ds5
    state_ds5 = state_subparsers.add_parser(
        'ds5',
        help='Query DS-5: Deferred Recognition (past cadence window)'
    )
    state_ds5.set_defaults(func=cmd_state_ds5)

    # state time-in-state
    state_time_in_state = state_subparsers.add_parser(
        'time-in-state',
        help='Query time-in-state visibility for latest declarations'
    )
    state_time_in_state.set_defaults(func=cmd_state_time_in_state)
    
    # ====== CUTTER LEDGER COMMANDS ======
    cutter_parser = subparsers.add_parser('cutter', help='Query Cutter Ledger')
    cutter_subparsers = cutter_parser.add_subparsers(dest='command', help='Cutter Ledger command')
    
    # cutter events
    cutter_events = cutter_subparsers.add_parser(
        'events',
        help='Query Cutter Ledger events'
    )
    cutter_events.add_argument('--subject_ref', help='Filter by subject reference (e.g., quote:123)')
    cutter_events.add_argument('--event_type', help='Filter by event type')
    cutter_events.add_argument('--limit', type=int, help='Max results')
    cutter_events.set_defaults(func=cmd_cutter_events)
    
    # cutter overrides
    cutter_overrides = cutter_subparsers.add_parser(
        'overrides',
        help='Query override events (via query_override_events.py)'
    )
    cutter_overrides.set_defaults(func=cmd_cutter_overrides)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.ledger:
        parser.print_help()
        return 1
    
    if not hasattr(args, 'func'):
        if args.ledger == 'state':
            state_parser.print_help()
        elif args.ledger == 'cutter':
            cutter_parser.print_help()
        return 1
    
    # Execute command
    try:
        return args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
