"""
vector_engine.py
The Brain - 5D Vector Search & Fingerprinting
"""
import numpy as np
import database
import json
import hashlib

# ============================================================================
# UNIT DETECTION & CONVERSION (Phase 5.6 - File Mode Unit Verification)
# ============================================================================

def guess_units(bbox, volume=None):
    """
    Multi-factor heuristic using dimension, volume, and aspect ratio.
    
    STL files don't encode units (just coordinates). This function uses multiple
    signals to guess whether the raw coordinates represent inches or millimeters.
    
    Logic:
    1. Very large parts (max_dim > 1000) → definitely mm
    2. Very small parts (max_dim < 0.1) → definitely inches
    3. Thin parts (high aspect ratio) in medium range → likely mm
    4. Large volume → likely mm³
    5. Medium-sized parts → default to inches (common in US machine shops)
    
    Example:
    - 10.5 × 5 × 2 (max=10.5, aspect=5.25) → "in" (typical machined part)
    - 266.7 × 127 × 50.8 (max=266.7, aspect=5.25) → "mm" (same part in mm)
    - 96 × 15 × 5 (max=96, aspect=19.2) → "mm" (thin sheet metal)
    
    Args:
        bbox: trimesh bounding box array [[min_x, min_y, min_z], [max_x, max_y, max_z]]
              OR numpy array of dimensions [x, y, z]
              OR list of dimensions [x, y, z]
        volume (float, optional): Part volume in native units³ for additional signal
    
    Returns:
        str: "in" or "mm"
    """
    # Handle both bbox formats: [[min], [max]] or [x, y, z]
    if len(bbox) == 2:
        # Format: [[min_x, min_y, min_z], [max_x, max_y, max_z]]
        # Convert to numpy arrays for subtraction
        min_coords = np.array(bbox[0])
        max_coords = np.array(bbox[1])
        dimensions = max_coords - min_coords
    else:
        # Format: [x, y, z]
        dimensions = np.array(bbox) if not isinstance(bbox, np.ndarray) else bbox
    
    max_dim = float(max(dimensions))
    min_dim = float(min(dimensions))
    
    # Calculate aspect ratio (max/min) - handle very thin parts
    aspect_ratio = max_dim / min_dim if min_dim > 0.01 else 1.0
    
    # SIGNAL 1: Very large parts are definitely mm
    # Example: 1500mm sheet metal (59 inches - rare in machine shops)
    if max_dim > 1000:
        return "mm"
    
    # SIGNAL 2: Very small parts are definitely inches
    # Example: 0.05" micro part (1.27mm - would read as 1.27 if in mm)
    if max_dim < 0.1:
        return "in"
    
    # SIGNAL 3: Thin parts (high aspect ratio) in medium range → likely mm
    # Example: 100mm × 5mm × 5mm (circuit board, sheet metal, aspect=20)
    # Rationale: Thin inch parts (4" × 0.2" × 0.2") are rare
    if 50 < max_dim < 500 and aspect_ratio > 6:
        return "mm"
    
    # SIGNAL 4: Volume check - if volume is huge, probably mm³
    # Example: 100,000 mm³ = 6.1 in³ (reasonable part in inches, huge in mm)
    if volume is not None and volume > 10000:
        return "mm"
    
    # SIGNAL 5: Default for medium-sized parts → inches
    # Rationale: US machine shops more commonly work in inches
    # Example: 10" × 5" × 2" reads as 10, 5, 2 → assume inches
    if max_dim < 300:
        return "in"
    else:
        return "mm"


def convert_units(volume, from_unit, to_unit):
    """
    Convert volume between units (inches and millimeters).
    
    Conversion factors:
    - mm³ to in³: divide by 25.4³ (16387.064)
    - in³ to mm³: multiply by 25.4³
    
    This function is used when the user corrects the unit interpretation
    of an STL file (e.g., "This file is actually in mm, not inches").
    
    Example:
    - convert_units(1000, "mm", "in") → 0.061 in³
    - convert_units(1, "in", "mm") → 16387.064 mm³
    
    Args:
        volume (float): Original volume
        from_unit (str): "mm" or "in"
        to_unit (str): "mm" or "in"
    
    Returns:
        float: Converted volume
    """
    if from_unit == to_unit:
        return volume
    
    # Conversion factor: 1 inch = 25.4 mm, so 1 in³ = 25.4³ mm³
    MM3_PER_IN3 = 25.4 ** 3  # 16387.064
    
    if from_unit == "mm" and to_unit == "in":
        return volume / MM3_PER_IN3
    elif from_unit == "in" and to_unit == "mm":
        return volume * MM3_PER_IN3
    else:
        # Fallback: return unchanged if invalid units
        return volume


def convert_dimensions(dimensions, from_unit, to_unit):
    """
    Convert linear dimensions (for bounding box display).
    
    Used when user corrects units to convert X/Y/Z dimensions for display.
    
    Example:
    - convert_dimensions((10.5, 5.0, 2.0), "in", "mm") → (266.7, 127.0, 50.8)
    - convert_dimensions((266.7, 127.0, 50.8), "mm", "in") → (10.5, 5.0, 2.0)
    
    Args:
        dimensions: tuple/list/array of (x, y, z) dimensions
        from_unit (str): "mm" or "in"
        to_unit (str): "mm" or "in"
    
    Returns:
        tuple: Converted dimensions (x, y, z)
    """
    if from_unit == to_unit:
        return tuple(dimensions)
    
    # Conversion factor: 1 inch = 25.4 mm
    if from_unit == "mm" and to_unit == "in":
        factor = 1 / 25.4
    elif from_unit == "in" and to_unit == "mm":
        factor = 25.4
    else:
        factor = 1.0  # Fallback
    
    return tuple(float(d) * factor for d in dimensions)

def create_fingerprint(volume, bbox, surface_area):
    """
    Creates a 5D vector fingerprint.
    Dimensions are SORTED to provide basic rotational invariance.
    Vector: [Vol/10, Small_Dim, Mid_Dim, Large_Dim, Area/50]
    """
    # Sort dimensions [Small, Mid, Large]
    # This ensures a 2x4x1 block matches a 1x4x2 block (Rotation Invariance)
    dims = sorted([bbox['x'], bbox['y'], bbox['z']])
    
    return [
        volume / 10.0, 
        dims[0], 
        dims[1], 
        dims[2], 
        surface_area / 50.0
    ]

def generate_genesis_hash(volume, bbox_dims):
    """
    Generates a deterministic "ISBN" string for a part based on mass and envelope.
    Protocol: GENESIS_V1
    
    Args:
        volume: Raw volume value (float)
        bbox_dims: List/tuple of 3 floats representing bounding box dimensions
    
    Returns:
        String in format: "CUTTER-{8-char-hex-uppercase}"
    """
    # Step 1: Sort dimensions (handles rotation)
    dims = sorted(bbox_dims)
    
    # Step 2: Format payload with 3 decimal precision
    payload = "{:.3f}|{:.3f}|{:.3f}|{:.3f}".format(volume, dims[0], dims[1], dims[2])
    
    # Step 3: Generate SHA256 hash
    hash_obj = hashlib.sha256(payload.encode())
    
    # Step 4: Return formatted hash (first 8 chars, uppercase)
    return f"CUTTER-{hash_obj.hexdigest()[:8].upper()}"

def find_similar_parts(current_fingerprint, history=None, current_vol=None):
    """
    Finds matches in history using Euclidean distance.
    Returns sorted list of matches.
    
    CRITICAL: Only searches ACTIVE quotes (is_deleted = 0).
    The AI must not learn from trash (data integrity).
    """
    if history is None:
        # get_all_history() already filters is_deleted = 0
        history = database.get_all_history()
        
    matches = []
    curr_vec = np.array(current_fingerprint)
    
    for record in history:
        try:
            if not record['fingerprint']: continue
            
            hist_vec = np.array(json.loads(record['fingerprint']))
            
            # Crash Protection: Skip legacy vectors if size mismatch
            if len(hist_vec) != 5: continue

            # 1. Euclidean Distance (The Similarity Score)
            dist = np.linalg.norm(curr_vec - hist_vec)
            
            # 2. The Vise Check (Volume Ratio)
            # Prevents "Geometric Liars" (tiny parts matching huge parts by vector accident)
            is_liar = False
            if current_vol:
                hist_vol = hist_vec[0] * 10.0 # Decode volume from vector
                if hist_vol > 0:
                    ratio = current_vol / hist_vol
                    # If volume varies by > 50%, it's definitely not the same part logic
                    if ratio > 1.5 or ratio < 0.66: 
                        is_liar = True
            
            if is_liar: 
                dist += 10.0 # Hard penalty sends it to the bottom of the list

            matches.append({
                'distance': float(dist),
                'match_type': 'twin' if dist < 2.5 else 'cousin', # WIDENED THRESHOLD FOR SIMULATION
                'id': record['id'],
                'filename': record['filename'],
                'final_price': record['final_price'],
                'setup_time': record.get('setup_time'),
                'tag_weights': record.get('tag_weights'),
                'user_feedback_tags': record.get('user_feedback_tags'),
                'timestamp': record.get('timestamp'),
                'process_routing': record.get('process_routing', [])  # Traveler Tags
            })
        except Exception as e:
            # print(f"Vector Error on ID {record.get('id')}: {e}")
            continue
        
    # Sort by distance (closest first)
    matches.sort(key=lambda x: x['distance'])
    return matches[:5]

def analyze_cluster(matches):
    """
    Analyzes local history cluster for similar parts.
    Returns pricing range, median, and confidence from shop's own historical quotes.
    PHASE 3 REMEDIATION: This is LOCAL data only, not Guild market intelligence.
    
    Args:
        matches: List of similar parts from find_similar_parts()
    
    Returns:
        Dictionary with cluster statistics, or None if insufficient data
    """
    if not matches:
        return None
    
    # Extract prices (filter out zero/invalid prices)
    prices = [m['final_price'] for m in matches if m.get('final_price', 0) > 0]
    
    if not prices:
        return None
        
    import statistics
    
    analysis = {
        'count': len(prices),
        'min_price': min(prices),
        'max_price': max(prices),
        'median_price': statistics.median(prices),
        'average_price': statistics.mean(prices)
    }
    
    # Calculate Spread (Volatility)
    # High spread indicates inconsistent pricing history
    if len(prices) > 1:
        spread = analysis['max_price'] - analysis['min_price']
        spread_pct = (spread / analysis['median_price']) * 100 if analysis['median_price'] > 0 else 0
        analysis['spread_pct'] = round(spread_pct, 1)
    else:
        analysis['spread_pct'] = 0.0
        
    return analysis