#!/usr/bin/env python3
"""
Baseline State Ledger Declarations

Establishes initial recognition state for all registered entities.
Each entity receives exactly ONE RECLASSIFICATION declaration from its owner.

IDEMPOTENT: Refuses to emit duplicate baseline declarations.
If baseline already exists for (entity_ref, scope_ref), the script REFUSES.

Constitutional compliance:
- No inference (all data explicit)
- No defaults (state_text hardcoded per entity)
- Stops on any error (no silent skips)
- Refuses duplicates (baseline already exists)

Usage:
    python scripts/baseline_declarations.py
    python scripts/baseline_declarations.py --force I_UNDERSTAND_DUPLICATES_CREATE_NOISE
"""

import sys
import json
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from state_ledger.boundary import emit_state_declaration, get_declarations


# Baseline declarations for org:cutterlayers.com initial registry
# Matches the registry from scripts/bootstrap_initial_registry.py
BASELINE_DECLARATIONS = [
    {
        "entity_ref": "org:cutterlayers.com/entity:equipment:cnc-primary",
        "scope_ref": "org:cutterlayers.com/scope:daily-ops",
        "actor_ref": "org:cutterlayers.com/actor:shop-floor",
        "state_text": "CNC mill is operational and ready for production work."
    },
    {
        "entity_ref": "org:cutterlayers.com/entity:equipment:laser-cutter",
        "scope_ref": "org:cutterlayers.com/scope:daily-ops",
        "actor_ref": "org:cutterlayers.com/actor:shop-floor",
        "state_text": "Laser cutter is operational and calibrated for current jobs."
    },
    {
        "entity_ref": "org:cutterlayers.com/entity:customer:top-3",
        "scope_ref": "org:cutterlayers.com/scope:monthly-review",
        "actor_ref": "org:cutterlayers.com/actor:sales-lead",
        "state_text": "Top customer relationships are active with regular order flow."
    },
    {
        "entity_ref": "org:cutterlayers.com/entity:supplier:metal-stock",
        "scope_ref": "org:cutterlayers.com/scope:monthly-review",
        "actor_ref": "org:cutterlayers.com/actor:procurement",
        "state_text": "Primary supplier is delivering on time with consistent quality."
    },
    {
        "entity_ref": "org:cutterlayers.com/entity:process:quote-turnaround",
        "scope_ref": "org:cutterlayers.com/scope:weekly-ops",
        "actor_ref": "org:cutterlayers.com/actor:sales-lead",
        "state_text": "Quote process is flowing smoothly with no significant delays."
    },
    {
        "entity_ref": "org:cutterlayers.com/entity:process:quality-control",
        "scope_ref": "org:cutterlayers.com/scope:weekly-ops",
        "actor_ref": "org:cutterlayers.com/actor:qa-owner",
        "state_text": "Quality control process is catching issues before shipping."
    },
    {
        "entity_ref": "org:cutterlayers.com/entity:capacity:shop-utilization",
        "scope_ref": "org:cutterlayers.com/scope:weekly-ops",
        "actor_ref": "org:cutterlayers.com/actor:shop-floor",
        "state_text": "Shop capacity is available for new work without overload."
    }
]


def check_baseline_exists(entity_ref: str, scope_ref: str) -> bool:
    """
    Check if a baseline declaration already exists for (entity_ref, scope_ref).
    
    Returns:
        True if any declaration exists, False otherwise
    """
    existing = get_declarations(entity_ref=entity_ref, scope_ref=scope_ref, limit=1)
    return len(existing) > 0


def main():
    """Emit baseline RECLASSIFICATION declarations for all registered entities."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Emit baseline State Ledger declarations (idempotent)',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--force',
        type=str,
        help='Force duplicate baseline (requires: I_UNDERSTAND_DUPLICATES_CREATE_NOISE)'
    )
    args = parser.parse_args()
    
    # Validate force flag if provided
    force_duplicates = False
    if args.force:
        if args.force == 'I_UNDERSTAND_DUPLICATES_CREATE_NOISE':
            force_duplicates = True
            print(json.dumps({
                "warning": "FORCE MODE ENABLED",
                "detail": "Duplicate baseline declarations will create noise and undermine meaning"
            }, indent=2), file=sys.stderr)
        else:
            print(json.dumps({
                "error": "Invalid force confirmation",
                "provided": args.force,
                "required": "I_UNDERSTAND_DUPLICATES_CREATE_NOISE"
            }, indent=2), file=sys.stderr)
            return 1
    
    results = {
        "baseline_declarations": [],
        "refused": [],
        "errors": []
    }
    
    # Pre-flight check: Look for existing baselines
    if not force_duplicates:
        for entry in BASELINE_DECLARATIONS:
            entity_ref = entry["entity_ref"]
            scope_ref = entry["scope_ref"]
            
            if check_baseline_exists(entity_ref, scope_ref):
                results["refused"].append({
                    "entity_ref": entity_ref,
                    "scope_ref": scope_ref,
                    "reason": "Baseline already exists for entity_ref + scope_ref. Refusing to emit duplicate baseline."
                })
        
        # If any baselines exist, refuse globally
        if results["refused"]:
            results["errors"].append({
                "error": "IDEMPOTENCY VIOLATION",
                "detail": "Baseline declarations already exist. Refusing to create duplicates.",
                "remedy": "Use --force I_UNDERSTAND_DUPLICATES_CREATE_NOISE to override (not recommended)"
            })
            
            print(json.dumps(results, indent=2), file=sys.stderr)
            return 1
    
    # Emit baseline declarations
    for entry in BASELINE_DECLARATIONS:
        entity_ref = entry["entity_ref"]
        
        try:
            # Emit RECLASSIFICATION declaration
            declaration_id = emit_state_declaration(
                entity_ref=entity_ref,
                scope_ref=entry["scope_ref"],
                state_text=entry["state_text"],
                actor_ref=entry["actor_ref"],
                declaration_kind="RECLASSIFICATION"
            )
            
            results["baseline_declarations"].append({
                "declaration_id": declaration_id,
                "entity_ref": entity_ref,
                "scope_ref": entry["scope_ref"],
                "actor_ref": entry["actor_ref"],
                "state_text": entry["state_text"],
                "declaration_kind": "RECLASSIFICATION"
            })
            
        except Exception as e:
            # Stop on first error (no silent skips)
            results["errors"].append({
                "entity_ref": entity_ref,
                "error": str(e)
            })
            
            # Print partial results with error
            print(json.dumps(results, indent=2))
            
            print(f"\n[ERROR] Failed to emit declaration for {entity_ref}", file=sys.stderr)
            print(f"[ERROR] {e}", file=sys.stderr)
            return 1
    
    # Print raw JSON results (no summaries, no advice)
    print(json.dumps(results, indent=2))
    
    # Exit code based on errors
    if results["errors"]:
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
