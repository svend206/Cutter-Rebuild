"""
Genesis Hash Generator - The "ISBN of Parts"
Phase 5.5: Genesis Hash Standard
PHASE 3 REMEDIATION: Clarified this is a technical standard, not Guild-specific

Purpose: Generate deterministic, globally unique identifiers for parts.

The Genesis Hash is a SHA-256 hash of:
- Volume (cubic inches, 6 decimal precision)
- Bounding box dimensions [X, Y, Z] (inches, sorted ascending, 4 decimal precision)

This standard enables:
- Local pattern matching within Ops (same shop, historical quotes)
- Cross-shop aggregation by Guild (separate product) without sharing 3D files
"""

import hashlib
from typing import Tuple, Optional
import numpy as np


def generate_genesis_hash(volume: float, dimensions: Tuple[float, float, float]) -> str:
    """
    Generate a deterministic Genesis Hash for a part.
    
    Args:
        volume: Part volume in cubic inches
        dimensions: Tuple of (X, Y, Z) bounding box dimensions in inches
    
    Returns:
        SHA-256 hash as hex string (64 characters)
    
    Example:
        >>> generate_genesis_hash(24.0, (4.0, 3.0, 2.0))
        'a7f3b21c89d4e5f6...'
    """
    # Normalize volume to 6 decimal places
    volume_normalized = f"{volume:.6f}"
    
    # Sort dimensions ascending and normalize to 4 decimal places
    dims_sorted = sorted(dimensions)
    dims_normalized = [f"{d:.4f}" for d in dims_sorted]
    
    # Create deterministic input string
    input_string = f"{volume_normalized}|{'|'.join(dims_normalized)}"
    
    # Generate SHA-256 hash
    hash_obj = hashlib.sha256(input_string.encode('utf-8'))
    genesis_hash = hash_obj.hexdigest()
    
    print(f"[GENESIS HASH] Input: {input_string}")
    print(f"[GENESIS HASH] Output: {genesis_hash[:16]}...")
    
    return genesis_hash


def generate_from_trimesh(mesh) -> Tuple[str, float, Tuple[float, float, float]]:
    """
    Generate Genesis Hash from a trimesh object (File Mode).
    
    Args:
        mesh: trimesh.Trimesh object (already loaded STL)
    
    Returns:
        Tuple of (genesis_hash, volume, dimensions)
    
    Raises:
        ValueError: If mesh is invalid or empty
    """
    if mesh is None or not hasattr(mesh, 'volume'):
        raise ValueError("Invalid mesh object")
    
    # Get volume (trimesh uses mm³, convert to in³)
    volume_mm3 = abs(mesh.volume)
    volume_in3 = volume_mm3 / 16387.064  # 1 in³ = 16387.064 mm³
    
    # Get bounding box dimensions (mm → inches)
    bounds = mesh.bounds  # [[min_x, min_y, min_z], [max_x, max_y, max_z]]
    dimensions_mm = bounds[1] - bounds[0]  # [width, depth, height]
    dimensions_in = tuple(dimensions_mm / 25.4)  # mm → inches
    
    # Generate hash
    genesis_hash = generate_genesis_hash(volume_in3, dimensions_in)
    
    return genesis_hash, volume_in3, dimensions_in


def generate_from_parametric(volume_in3: float, shape_type: str, dimensions: dict) -> Tuple[str, Tuple[float, float, float]]:
    """
    Generate Genesis Hash from parametric shape (Napkin Mode).
    
    Args:
        volume_in3: Part volume in cubic inches (already calculated)
        shape_type: Shape type (block, cylinder, tube, l-bracket, plate)
        dimensions: Shape-specific dimensions dict
    
    Returns:
        Tuple of (genesis_hash, bounding_dimensions)
    
    Example:
        Block (4 × 2 × 1):
            dimensions = {'x': 4.0, 'y': 2.0, 'z': 1.0}
            bounding_dimensions = (4.0, 2.0, 1.0)
        
        Cylinder (Ø2 × 6):
            dimensions = {'diameter': 2.0, 'length': 6.0}
            bounding_dimensions = (2.0, 2.0, 6.0)  # [D, D, L]
    """
    # Calculate bounding box based on shape type
    if shape_type in ['block', 'plate']:
        bounding_dims = (dimensions['x'], dimensions['y'], dimensions['z'])
    
    elif shape_type == 'cylinder':
        d = dimensions['diameter']
        l = dimensions['length']
        bounding_dims = (d, d, l)
    
    elif shape_type == 'tube':
        od = dimensions['od']
        l = dimensions['length']
        bounding_dims = (od, od, l)
    
    elif shape_type == 'l-bracket':
        leg1 = dimensions['leg1']
        leg2 = dimensions['leg2']
        width = dimensions['width']
        bounding_dims = (leg1, leg2, width)
    
    else:
        raise ValueError(f"Unknown shape type: {shape_type}")
    
    # Generate hash
    genesis_hash = generate_genesis_hash(volume_in3, bounding_dims)
    
    return genesis_hash, bounding_dims


def validate_genesis_hash(genesis_hash: str) -> bool:
    """
    Validate that a string is a valid Genesis Hash.
    
    Args:
        genesis_hash: String to validate
    
    Returns:
        True if valid SHA-256 hex string, False otherwise
    """
    if not isinstance(genesis_hash, str):
        return False
    
    if len(genesis_hash) != 64:
        return False
    
    try:
        int(genesis_hash, 16)  # Verify it's valid hex
        return True
    except ValueError:
        return False


# ============================================================================
# COLLISION DETECTION (Future Enhancement)
# ============================================================================

def detect_collision(db_connection, genesis_hash: str, volume: float, dimensions: Tuple[float, float, float]) -> Optional[dict]:
    """
    Check if this Genesis Hash collides with a different part (extremely rare).
    
    SHA-256 collision probability is ~2^-256, but we check anyway for robustness.
    
    Args:
        db_connection: SQLite connection
        genesis_hash: Generated hash to check
        volume: Part volume
        dimensions: Bounding dimensions
    
    Returns:
        None if no collision, dict with collision details if found
    """
    cursor = db_connection.cursor()
    cursor.execute("""
        SELECT id, volume, fingerprint_json
        FROM ops__parts
        WHERE genesis_hash = ?
    """, (genesis_hash,))
    
    row = cursor.fetchone()
    if row:
        existing_volume = row[1]
        # If volumes match (within 0.1%), it's the same part, not a collision
        if abs(existing_volume - volume) / volume < 0.001:
            return None
        
        # Volumes differ -> TRUE COLLISION (should never happen)
        return {
            'existing_part_id': row[0],
            'existing_volume': existing_volume,
            'new_volume': volume,
            'collision_type': 'sha256_hash_collision'
        }
    
    return None

