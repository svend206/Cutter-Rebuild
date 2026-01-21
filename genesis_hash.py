"""
Compatibility wrapper for genesis_hash module.

Tests import this at repo root; delegate to ops_layer implementation.
"""

from ops_layer.genesis_hash import (  # noqa: F401
    generate_genesis_hash,
    generate_from_trimesh,
    generate_from_parametric,
    validate_genesis_hash,
)
