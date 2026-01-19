#!/usr/bin/env python3
"""
Weekly Ritual: Raw Structural Visibility

Prints raw JSON outputs for:
- DS-2: Unowned Recognition (entities with no current owner)
- DS-5: Deferred Recognition (entities past cadence window)
- Optional: Last N Cutter Ledger events

Constitutional compliance:
- No summaries or advice
- No "you should" statements
- Raw data only
- Exit code 0 (visibility, not enforcement)

Usage:
    python scripts/weekly_ritual.py
    python scripts/weekly_ritual.py --events 20
    python scripts/weekly_ritual.py --events 50 --output weekly_ritual.json
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from state_ledger.boundary import query_unowned_entities, query_deferred_recognition
    from cutter_ledger.boundary import get_events
    import database
except ImportError as e:
    print(json.dumps({
        "error": "Failed to import required modules",
        "detail": str(e)
    }, indent=2))
    sys.exit(1)


def check_database_exists():
    """Check if database exists and is accessible."""
    try:
        conn = database.get_connection()
        conn.close()
        return True
    except Exception as e:
        print(json.dumps({
            "error": "Database not accessible",
            "detail": str(e),
            "hint": "Run 'python -c \"import database; database.initialize_database()\"' to initialize"
        }, indent=2))
        return False


def get_ds2_unowned_recognition():
    """Query DS-2: Entities with no current owner."""
    try:
        results = query_unowned_entities()
        return {
            "ds2_unowned_recognition": {
                "description": "Entities with no current recognition owner",
                "count": len(results),
                "entities": results
            }
        }
    except Exception as e:
        return {
            "ds2_unowned_recognition": {
                "error": str(e)
            }
        }


def get_ds5_deferred_recognition():
    """Query DS-5: Entities past their expected cadence window."""
    try:
        results = query_deferred_recognition()
        return {
            "ds5_deferred_recognition": {
                "description": "Entities past expected reaffirmation cadence",
                "count": len(results),
                "entities": results
            }
        }
    except Exception as e:
        return {
            "ds5_deferred_recognition": {
                "error": str(e)
            }
        }


def get_recent_cutter_events(limit=10):
    """Query recent Cutter Ledger events."""
    try:
        # Get all events, then take last N
        all_events = get_events()
        recent_events = all_events[-limit:] if len(all_events) > limit else all_events
        
        return {
            "recent_cutter_events": {
                "description": f"Last {limit} operational events from Cutter Ledger",
                "count": len(recent_events),
                "total_events_in_ledger": len(all_events),
                "events": recent_events
            }
        }
    except Exception as e:
        return {
            "recent_cutter_events": {
                "error": str(e)
            }
        }


def main():
    """Run weekly ritual: print raw structural visibility."""
    parser = argparse.ArgumentParser(
        description='Weekly Ritual: Raw Structural Visibility',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/weekly_ritual.py
  python scripts/weekly_ritual.py --events 20
  python scripts/weekly_ritual.py --events 50 --output weekly_ritual.json

Output:
  Raw JSON to stdout (or file if --output specified)
  
Constitutional compliance:
  - No summaries or interpretations
  - No advice or "you should" statements
  - Raw data visibility only
        """
    )
    
    parser.add_argument(
        '--events',
        type=int,
        metavar='N',
        help='Include last N Cutter Ledger events (optional)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        metavar='FILE',
        help='Write output to file instead of stdout'
    )
    
    args = parser.parse_args()
    
    # Get database path for diagnostics
    test_db_path = os.environ.get('TEST_DB_PATH')
    if test_db_path:
        db_path_str = test_db_path
    else:
        db_path_str = str(database.DB_PATH)
    
    # Check database accessibility
    if not check_database_exists():
        return 1
    
    # Collect ritual data
    ritual_data = {
        "ritual": "weekly_structural_visibility",
        "timestamp": datetime.now().isoformat(),
        "db_path": db_path_str,
        "constitutional_note": "Raw visibility only. No summaries, advice, or enforcement."
    }
    
    # DS-2: Unowned Recognition
    ritual_data.update(get_ds2_unowned_recognition())
    
    # DS-5: Deferred Recognition
    ritual_data.update(get_ds5_deferred_recognition())
    
    # Optional: Recent Cutter Events
    if args.events:
        ritual_data.update(get_recent_cutter_events(limit=args.events))
    
    # Output
    output_json = json.dumps(ritual_data, indent=2, default=str)
    
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output_json)
            print(f"Ritual data written to: {args.output}", file=sys.stderr)
        except Exception as e:
            print(json.dumps({
                "error": "Failed to write output file",
                "detail": str(e)
            }, indent=2))
            return 1
    else:
        print(output_json)
    
    # Exit code 0: visibility, not enforcement
    # We show what is, not what should be
    return 0


if __name__ == '__main__':
    sys.exit(main())
