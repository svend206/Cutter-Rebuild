#!/usr/bin/env python3
"""
Bootstrap Initial State Ledger Registry for org:cutterlayers.com

Registers the initial 7 entities from canon/decision_log/initial_state_ledger_registry.md
and assigns their intended owners.

Constitutional compliance:
- No inference (all data hardcoded from canonical registry)
- No summaries or advice (raw JSON output only)
- Identifiers validated by state_ledger.boundary validators

Usage:
    python scripts/bootstrap_initial_registry.py
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from state_ledger.boundary import register_entity, assign_owner


# Hardcoded from canon/decision_log/initial_state_ledger_registry.md
# Entity registry for org:cutterlayers.com
INITIAL_REGISTRY = [
    {
        "entity_ref": "org:cutterlayers.com/entity:equipment:cnc-primary",
        "entity_label": "Primary CNC Mill",
        "cadence_days": 1,
        "scope_ref": "org:cutterlayers.com/scope:daily-ops",
        "owner_actor_ref": "org:cutterlayers.com/actor:shop-floor"
    },
    {
        "entity_ref": "org:cutterlayers.com/entity:equipment:laser-cutter",
        "entity_label": "Laser Cutter",
        "cadence_days": 1,
        "scope_ref": "org:cutterlayers.com/scope:daily-ops",
        "owner_actor_ref": "org:cutterlayers.com/actor:shop-floor"
    },
    {
        "entity_ref": "org:cutterlayers.com/entity:customer:top-3",
        "entity_label": "Top 3 Revenue Customers (Aggregate)",
        "cadence_days": 30,
        "scope_ref": "org:cutterlayers.com/scope:monthly-review",
        "owner_actor_ref": "org:cutterlayers.com/actor:sales-lead"
    },
    {
        "entity_ref": "org:cutterlayers.com/entity:supplier:metal-stock",
        "entity_label": "Primary Metal Stock Supplier",
        "cadence_days": 30,
        "scope_ref": "org:cutterlayers.com/scope:monthly-review",
        "owner_actor_ref": "org:cutterlayers.com/actor:procurement"
    },
    {
        "entity_ref": "org:cutterlayers.com/entity:process:quote-turnaround",
        "entity_label": "Quote Response Time",
        "cadence_days": 7,
        "scope_ref": "org:cutterlayers.com/scope:weekly-ops",
        "owner_actor_ref": "org:cutterlayers.com/actor:sales-lead"
    },
    {
        "entity_ref": "org:cutterlayers.com/entity:process:quality-control",
        "entity_label": "Quality Control Process",
        "cadence_days": 7,
        "scope_ref": "org:cutterlayers.com/scope:weekly-ops",
        "owner_actor_ref": "org:cutterlayers.com/actor:qa-owner"
    },
    {
        "entity_ref": "org:cutterlayers.com/entity:capacity:shop-utilization",
        "entity_label": "Overall Shop Capacity",
        "cadence_days": 7,
        "scope_ref": "org:cutterlayers.com/scope:weekly-ops",
        "owner_actor_ref": "org:cutterlayers.com/actor:shop-floor"
    }
]

# Actor performing the bootstrap (system initialization)
BOOTSTRAP_ACTOR = "org:cutterlayers.com/actor:system-init"


def main():
    """Register initial State Ledger entities and assign owners."""
    
    results = {
        "registered_entities": [],
        "assigned_owners": [],
        "errors": []
    }
    
    for entry in INITIAL_REGISTRY:
        entity_ref = entry["entity_ref"]
        
        try:
            # Register entity
            register_entity(
                entity_ref=entity_ref,
                entity_label=entry["entity_label"],
                cadence_days=entry["cadence_days"]
            )
            
            results["registered_entities"].append({
                "entity_ref": entity_ref,
                "entity_label": entry["entity_label"],
                "cadence_days": entry["cadence_days"]
            })
            
        except Exception as e:
            results["errors"].append({
                "entity_ref": entity_ref,
                "operation": "register_entity",
                "error": str(e)
            })
            continue
        
        try:
            # Assign owner
            assign_owner(
                entity_ref=entity_ref,
                owner_actor_ref=entry["owner_actor_ref"],
                assigned_by_actor_ref=BOOTSTRAP_ACTOR
            )
            
            results["assigned_owners"].append({
                "entity_ref": entity_ref,
                "owner_actor_ref": entry["owner_actor_ref"],
                "assigned_by_actor_ref": BOOTSTRAP_ACTOR
            })
            
        except Exception as e:
            results["errors"].append({
                "entity_ref": entity_ref,
                "operation": "assign_owner",
                "error": str(e)
            })
    
    # Print raw JSON (no summaries, no advice)
    print(json.dumps(results, indent=2))
    
    # Exit code based on errors
    if results["errors"]:
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
