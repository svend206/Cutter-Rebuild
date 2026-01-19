"""
State Ledger Identifier Validation

Constitutional enforcement of Guild-safe identifier formats.
See: canon/constitution/identifier_conventions.md

Validators accept or refuse. They do NOT correct inputs.
"""

import re
from typing import Tuple


# Regex patterns for identifier validation
# All patterns enforce lowercase to prevent case-sensitivity collisions

# org_ref: org:{domain} where domain is DNS-style (lowercase, alphanumeric, hyphens, dots)
ORG_REF_PATTERN = re.compile(
    r'^org:[a-z0-9]([a-z0-9\-\.]{0,251}[a-z0-9])?$'
)

# actor_ref: {org_ref}/actor:{local_id}
ACTOR_REF_PATTERN = re.compile(
    r'^org:[a-z0-9]([a-z0-9\-\.]{0,251}[a-z0-9])?/actor:[a-z0-9][a-z0-9\-_\.]{0,99}$'
)

# entity_ref: {org_ref}/entity:{type}:{local_id}
ENTITY_REF_PATTERN = re.compile(
    r'^org:[a-z0-9]([a-z0-9\-\.]{0,251}[a-z0-9])?/entity:[a-z0-9\-]{1,50}:[a-z0-9][a-z0-9\-_\.\:]{0,99}$'
)

# scope_ref: {org_ref}/scope:{context}
SCOPE_REF_PATTERN = re.compile(
    r'^org:[a-z0-9]([a-z0-9\-\.]{0,251}[a-z0-9])?/scope:[a-z0-9][a-z0-9\-_\.\:]{0,99}$'
)


def validate_org_ref(org_ref: str) -> Tuple[bool, str]:
    """
    Validate organization reference format.
    
    Format: org:{domain}
    - Domain: DNS-style, lowercase, alphanumeric, hyphens, dots
    - Minimum 2 chars (org:x)
    - Maximum 253 chars for domain (DNS limit)
    
    Args:
        org_ref: Organization reference string
        
    Returns:
        (is_valid, error_message)
        - If valid: (True, "")
        - If invalid: (False, "clear error message")
    """
    if not org_ref:
        return False, "org_ref cannot be empty"
    
    if not isinstance(org_ref, str):
        return False, "org_ref must be a string"
    
    if len(org_ref) > 257:  # "org:" + 253 chars max domain + buffer
        return False, f"org_ref too long ({len(org_ref)} chars, max 257)"
    
    # Check lowercase before checking prefix (better error message)
    if not org_ref.islower():
        return False, "org_ref must be lowercase (found uppercase characters)"
    
    if not org_ref.startswith("org:"):
        return False, "org_ref must start with 'org:'"
    
    if not ORG_REF_PATTERN.match(org_ref):
        return False, "org_ref format invalid (must be org:{domain} with DNS-style domain)"
    
    return True, ""


def validate_actor_ref(actor_ref: str) -> Tuple[bool, str]:
    """
    Validate actor reference format.
    
    Format: {org_ref}/actor:{local_id}
    - Must start with valid org_ref
    - Local ID: alphanumeric, hyphens, underscores, dots
    - Minimum 1 char for local ID
    - Maximum 100 chars for local ID
    
    Args:
        actor_ref: Actor reference string
        
    Returns:
        (is_valid, error_message)
    """
    if not actor_ref:
        return False, "actor_ref cannot be empty"
    
    if not isinstance(actor_ref, str):
        return False, "actor_ref must be a string"
    
    if len(actor_ref) > 360:  # org_ref (257) + "/actor:" (7) + local_id (100) - buffer
        return False, f"actor_ref too long ({len(actor_ref)} chars, max ~360)"
    
    # Check lowercase before checking structure (better error message)
    if not actor_ref.islower():
        return False, "actor_ref must be lowercase (found uppercase characters)"
    
    if "/actor:" not in actor_ref:
        return False, "actor_ref must contain '/actor:' separator"
    
    # Validate org_ref prefix
    org_part = actor_ref.split("/actor:")[0]
    org_valid, org_error = validate_org_ref(org_part)
    if not org_valid:
        return False, f"actor_ref has invalid org prefix: {org_error}"
    
    if not ACTOR_REF_PATTERN.match(actor_ref):
        return False, "actor_ref format invalid (must be org:{domain}/actor:{local_id})"
    
    return True, ""


def validate_entity_ref(entity_ref: str) -> Tuple[bool, str]:
    """
    Validate entity reference format.
    
    Format: {org_ref}/entity:{type}:{local_id}
    - Must start with valid org_ref
    - Type: alphanumeric, hyphens (describes entity kind)
    - Local ID: alphanumeric, hyphens, underscores, dots, colons
    - Type: 1-50 chars
    - Local ID: 1-100 chars
    
    Args:
        entity_ref: Entity reference string
        
    Returns:
        (is_valid, error_message)
    """
    if not entity_ref:
        return False, "entity_ref cannot be empty"
    
    if not isinstance(entity_ref, str):
        return False, "entity_ref must be a string"
    
    if len(entity_ref) > 410:  # org_ref + "/entity:" + type + ":" + local_id
        return False, f"entity_ref too long ({len(entity_ref)} chars, max ~410)"
    
    # Check lowercase before checking structure (better error message)
    if not entity_ref.islower():
        return False, "entity_ref must be lowercase (found uppercase characters)"
    
    if "/entity:" not in entity_ref:
        return False, "entity_ref must contain '/entity:' separator"
    
    # Validate org_ref prefix
    org_part = entity_ref.split("/entity:")[0]
    org_valid, org_error = validate_org_ref(org_part)
    if not org_valid:
        return False, f"entity_ref has invalid org prefix: {org_error}"
    
    # Check for type:local_id structure
    entity_part = entity_ref.split("/entity:", 1)[1]
    if ":" not in entity_part:
        return False, "entity_ref must have format org:{domain}/entity:{type}:{local_id}"
    
    if not ENTITY_REF_PATTERN.match(entity_ref):
        return False, "entity_ref format invalid (must be org:{domain}/entity:{type}:{local_id})"
    
    return True, ""


def validate_scope_ref(scope_ref: str) -> Tuple[bool, str]:
    """
    Validate scope reference format.
    
    Format: {org_ref}/scope:{context}
    - Must start with valid org_ref
    - Context: alphanumeric, hyphens, underscores, dots, colons
    - Minimum 1 char for context
    - Maximum 100 chars for context
    
    Args:
        scope_ref: Scope reference string
        
    Returns:
        (is_valid, error_message)
    """
    if not scope_ref:
        return False, "scope_ref cannot be empty"
    
    if not isinstance(scope_ref, str):
        return False, "scope_ref must be a string"
    
    if len(scope_ref) > 360:  # org_ref (257) + "/scope:" (7) + context (100) - buffer
        return False, f"scope_ref too long ({len(scope_ref)} chars, max ~360)"
    
    # Check lowercase before checking structure (better error message)
    if not scope_ref.islower():
        return False, "scope_ref must be lowercase (found uppercase characters)"
    
    if "/scope:" not in scope_ref:
        return False, "scope_ref must contain '/scope:' separator"
    
    # Validate org_ref prefix
    org_part = scope_ref.split("/scope:")[0]
    org_valid, org_error = validate_org_ref(org_part)
    if not org_valid:
        return False, f"scope_ref has invalid org prefix: {org_error}"
    
    if not SCOPE_REF_PATTERN.match(scope_ref):
        return False, "scope_ref format invalid (must be org:{domain}/scope:{context})"
    
    return True, ""


def validate_all_refs(
    entity_ref: str,
    actor_ref: str,
    scope_ref: str
) -> Tuple[bool, str]:
    """
    Validate all three refs at once (common case for emit_state_declaration).
    
    Returns:
        (all_valid, error_message)
        - If all valid: (True, "")
        - If any invalid: (False, "first error message")
    """
    entity_valid, entity_error = validate_entity_ref(entity_ref)
    if not entity_valid:
        return False, f"Invalid entity_ref: {entity_error}"
    
    actor_valid, actor_error = validate_actor_ref(actor_ref)
    if not actor_valid:
        return False, f"Invalid actor_ref: {actor_error}"
    
    scope_valid, scope_error = validate_scope_ref(scope_ref)
    if not scope_valid:
        return False, f"Invalid scope_ref: {scope_error}"
    
    return True, ""
