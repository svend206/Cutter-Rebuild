"""
Runtime estimation engine for machining operations.
"""
import math
from typing import Tuple, Dict, Any
import database


# --- CONFIGURATION (Now Database-Driven) ---
# Refactoring Strike 1: Moved hardcoded values to shop_config table

def BASE_MRR() -> float:
    """Base Material Removal Rate for Aluminum (cubic inches per minute)"""
    return database.get_config('base_mrr', 30.0)

def SETUP_TIME() -> float:
    """Fixed setup time in minutes"""
    return database.get_config('setup_time_minutes', 60.0)

def SAW_KERF() -> float:
    """Saw kerf buffer / facing allowance (inches)"""
    return database.get_config('saw_kerf', 0.125)

def MIN_HAND_TIME_PER_PART() -> float:
    """Minimum hand time per part - load, unload, inspect, debur (minutes)"""
    return database.get_config('min_hand_time', 5.0)


def _round_to_increment(value: float, increment: float) -> float:
    """
    Round a value UP to the nearest increment.
    
    Args:
        value: Value to round
        increment: Increment size (e.g., 0.0625 for 1/16")
        
    Returns:
        Rounded value
    """
    return math.ceil(value / increment) * increment


def suggest_stock(x: float, y: float, z: float) -> Tuple[float, float, float, float]:
    """
    Suggest stock dimensions based on part bounding box with scale-aware rounding.
    
    Logic:
    1. Add SAW_KERF inches to each dimension (saw cut buffer)
    2. Round each dimension based on part size:
       - If dimension < 1.0": round to nearest 0.0625" (1/16")
       - If 1.0" <= dimension < 3.0": round to nearest 0.125" (1/8")
       - If dimension >= 3.0": round to nearest 0.25" (1/4")
    
    Args:
        x: Part dimension in X (inches)
        y: Part dimension in Y (inches)
        z: Part dimension in Z (inches)
        
    Returns:
        Tuple of (stock_x, stock_y, stock_z, stock_volume) in inches and cubic inches
    """
    # Add saw kerf buffer
    stock_x = x + SAW_KERF()
    stock_y = y + SAW_KERF()
    stock_z = z + SAW_KERF()
    
    # Apply scale-aware rounding to each dimension
    def round_dimension(dim: float) -> float:
        if dim < 1.0:
            # Round to nearest 1/16" (0.0625")
            return _round_to_increment(dim, 0.0625)
        elif dim < 3.0:
            # Round to nearest 1/8" (0.125")
            return _round_to_increment(dim, 0.125)
        else:
            # Round to nearest 1/4" (0.25")
            return _round_to_increment(dim, 0.25)
    
    stock_x = round_dimension(stock_x)
    stock_y = round_dimension(stock_y)
    stock_z = round_dimension(stock_z)
    
    # Calculate stock volume
    stock_volume = stock_x * stock_y * stock_z
    
    return (stock_x, stock_y, stock_z, stock_volume)


def estimate_runtime(
    part_volume_in3: float,
    stock_volume_in3: float,
    material_name: str,
    complexity_factor: float = 1.0
) -> Dict[str, float]:
    """
    Estimate per-part runtime in minutes for machining a part from stock.
    
    IMPORTANT: Returns PER-PART time WITHOUT setup. Setup time should be 
    added ONCE by the pricing engine and amortized over quantity.
    
    Logic:
    1. Get machinability score from database
    2. Adjusted_MRR = BASE_MRR / score
    3. Removal_Volume = Stock_Volume - Part_Volume
    4. Base_Machine_Time = Removal_Volume / Adjusted_MRR
    5. Base_Run_Time = Base_Machine_Time + MIN_HAND_TIME_PER_PART
    6. Per_Part_Time = Base_Run_Time * complexity_factor  (complexity applies to machine + hand time)
    7. Machine_Time = (Base_Machine_Time * complexity_factor)  (for reporting)
    8. Hand_Time = (MIN_HAND_TIME_PER_PART * complexity_factor)  (for reporting)
    
    Args:
        part_volume_in3: Part volume in cubic inches
        stock_volume_in3: Stock volume in cubic inches
        material_name: Name of the material
        complexity_factor: Multiplier for run time (machine + hand) (1.0 = standard, higher = more complex)
        
    Returns:
        Dictionary with keys:
        - machine_time_mins: Spindle/machine time in minutes (with complexity applied)
        - hand_time_mins: Hand time in minutes (with complexity applied)
        - per_part_time_mins: Machine time + Hand time per part (with complexity applied)
        - setup_time_mins: Fixed setup time (returned separately for pricing engine)
        
    Raises:
        ValueError: If material is not found in database
    """
    # Get machinability score from database
    score = database.get_material_score(material_name)
    
    # Fallback Pricing: Use Aluminum 6061 values if material not found
    if score is None:
        print(f"WARNING: Material '{material_name}' not found. Using fallback pricing.")
        score = 1.0  # Aluminum 6061 machinability score
    
    # Calculate adjusted Material Removal Rate
    adjusted_mrr = BASE_MRR() / score
    
    # Calculate removal volume
    removal_volume = stock_volume_in3 - part_volume_in3
    
    # Calculate base machine time (spindle time)
    # FIX: Lowered minimum from 1.0 to 0.1 to allow price sensitivity on small parts
    base_machine_time = max(removal_volume / adjusted_mrr, 0.1)
    
    # Base run time (machine + hand, before complexity)
    base_run_time = base_machine_time + MIN_HAND_TIME_PER_PART()
    
    # Apply complexity factor to the sum of machine time and hand time
    # This prevents fixed setup costs from drowning out the difficulty adjustment
    per_part_time = base_run_time * complexity_factor
    
    # Calculate individual components with complexity applied (for reporting)
    machine_time = base_machine_time * complexity_factor
    hand_time = MIN_HAND_TIME_PER_PART() * complexity_factor
    
    return {
        'machine_time_mins': machine_time,
        'hand_time_mins': hand_time,
        'per_part_time_mins': per_part_time,  # Per-part time WITHOUT setup
        'setup_time_mins': SETUP_TIME()  # Return setup separately
    }


def calculate_geometry(input) -> Tuple[float, Dict[str, float], float, str]:
    """
    Calculate geometry from STL/STEP file or mesh object with SMART UNIT DETECTION.
    
    OPTIMIZATION PASS 1: Now accepts either filepath OR mesh object to avoid double-loading.
    UNIT AUTO-DETECTION: Handles files in meters, millimeters, or inches automatically.
    
    STL/STEP files don't store unit metadata, so we use heuristic detection:
    - If largest dimension is 0.01 to 10    → Assume METERS
    - If largest dimension is 0.1 to 100    → Assume INCHES
    - If largest dimension is 10 to 10000   → Assume MILLIMETERS
    
    Args:
        input: Either a path to STL/STEP file (str) OR a trimesh.Trimesh/Scene object
        
    Returns:
        Tuple of (volume_in3, bbox_dict, surface_area_in2)
        - volume_in3: Volume in cubic inches
        - bbox_dict: Dictionary with 'x', 'y', 'z' keys (dimensions in inches)
        - surface_area_in2: Surface area in square inches (Complexity DNA)
    """
    import trimesh
    
    # ELEGANT CHECK: Accept either filepath or mesh object
    if isinstance(input, str):
        # Input is a filepath - load the mesh
        mesh = trimesh.load(input)
        if isinstance(mesh, trimesh.Scene):
            mesh = mesh.dump(concatenate=True)
    else:
        # Input is already a mesh object - use directly
        mesh = input
        if isinstance(mesh, trimesh.Scene):
            mesh = mesh.dump(concatenate=True)
    
    # Get raw geometry (no unit assumptions)
    bounds = mesh.bounds
    raw_dimensions = bounds[1] - bounds[0]
    max_dimension = max(raw_dimensions)
    raw_volume = mesh.volume
    
    # PHASE 5.6: Multi-Factor Unit Detection using vector_engine
    # Import here to avoid circular dependency
    import vector_engine
    
    # Use multi-factor heuristic (dimension, volume, aspect ratio)
    assumed_unit = vector_engine.guess_units(bounds, raw_volume)
    
    # Convert to inches based on assumed units
    if assumed_unit == "in":
        # File is already in inches
        scale_factor = 1.0
        volume_scale_factor = 1.0
        area_scale_factor = 1.0
        detected_unit = "INCHES"
    elif assumed_unit == "mm":
        # File is in millimeters, convert to inches
        scale_factor = 0.0393701  # mm to inches (1/25.4)
        volume_scale_factor = 0.0000610237  # mm³ to in³
        area_scale_factor = 0.00155  # mm² to in²
        detected_unit = "MILLIMETERS"
    else:
        # Fallback (shouldn't happen with new heuristic)
        scale_factor = 1.0
        volume_scale_factor = 1.0
        area_scale_factor = 1.0
        detected_unit = "INCHES (fallback)"
        assumed_unit = "in"
    
    # Convert to inches
    volume_in3 = raw_volume * volume_scale_factor
    surface_area_in2 = mesh.area * area_scale_factor
    
    bbox = {
        'x': raw_dimensions[0] * scale_factor,
        'y': raw_dimensions[1] * scale_factor,
        'z': raw_dimensions[2] * scale_factor
    }
    
    # Debug logging
    print(f"[UNIT] MULTI-FACTOR DETECTION: {detected_unit}")
    print(f"   Raw max dimension: {max_dimension:.6f}")
    print(f"   Raw volume: {raw_volume:.6f}")
    print(f"   Assumed units: {assumed_unit}")
    print(f"   Converted to inches: {max(bbox['x'], bbox['y'], bbox['z']):.4f}\"")
    print(f"   Converted volume: {volume_in3:.6f} in³")
    
    return volume_in3, bbox, surface_area_in2, assumed_unit


def calculate_geometry_raw(mesh) -> Dict[str, Any]:
    """
    Calculate raw geometry from mesh without unit assumptions.
    
    STL files don't have unit metadata, so we return raw values.
    The caller must determine if raw values are in inches or millimeters.
    
    Args:
        mesh: Trimesh object
        
    Returns:
        Dictionary with:
        - volume_raw: Raw volume (no unit conversion)
        - bbox_raw: Raw bounding box dimensions (x, y, z) as tuple
        - surface_area_raw: Raw surface area (no unit conversion)
    """
    # Get raw volume (no conversion)
    volume_raw = mesh.volume
    
    # Get raw bounding box dimensions
    bounds = mesh.bounds
    dimensions_raw = bounds[1] - bounds[0]  # max - min for each axis
    bbox_raw = tuple(dimensions_raw)
    
    # Get raw surface area (prepare for Brain Upgrade)
    surface_area_raw = mesh.area
    
    return {
        'volume_raw': volume_raw,
        'bbox_raw': bbox_raw,
        'surface_area_raw': surface_area_raw
    }


def get_unit_options(bbox_raw: Tuple[float, float, float], volume_raw: float) -> Dict[str, Any]:
    """
    Calculate geometry in both unit interpretations.
    
    Args:
        bbox_raw: Raw bounding box (x, y, z) - unknown units
        volume_raw: Raw volume - unknown units
        
    Returns:
        Dictionary with:
        - as_inches: {x, y, z, volume} assuming raw is inches
        - as_mm: {x, y, z, volume} assuming raw is mm
        - as_inches_converted: {x, y, z, volume} assuming raw is mm, converted to inches
        - as_mm_converted: {x, y, z, volume} assuming raw is inches, converted to mm
    """
    # Interpretation 1: Raw values are in inches
    bbox_as_inches = {
        'x': bbox_raw[0],
        'y': bbox_raw[1],
        'z': bbox_raw[2],
        'volume': volume_raw
    }
    
    # Interpretation 2: Raw values are in mm, convert to inches
    MM_TO_INCH = 25.4
    bbox_as_mm_converted = {
        'x': bbox_raw[0] / MM_TO_INCH,
        'y': bbox_raw[1] / MM_TO_INCH,
        'z': bbox_raw[2] / MM_TO_INCH,
        'volume': volume_raw / (MM_TO_INCH ** 3)
    }
    
    # Interpretation 3: Raw values are in mm (for display)
    bbox_as_mm = {
        'x': bbox_raw[0],
        'y': bbox_raw[1],
        'z': bbox_raw[2],
        'volume': volume_raw
    }
    
    # Interpretation 4: Raw values are in inches, convert to mm (for display)
    bbox_as_inches_converted = {
        'x': bbox_raw[0] * MM_TO_INCH,
        'y': bbox_raw[1] * MM_TO_INCH,
        'z': bbox_raw[2] * MM_TO_INCH,
        'volume': volume_raw * (MM_TO_INCH ** 3)
    }
    
    return {
        'as_inches': bbox_as_inches,
        'as_mm_converted': bbox_as_mm_converted,
        'as_mm': bbox_as_mm,
        'as_inches_converted': bbox_as_inches_converted
    }


def check_reasonableness(bbox_inches: Dict[str, float]) -> Dict[str, Any]:
    """
    Check if bounding box dimensions are in the "Bob Zone" (reasonable range).
    
    Bob Zone: All dimensions between 0.05 inches and 50 inches.
    
    Args:
        bbox_inches: Bounding box in inches {x, y, z}
        
    Returns:
        Dictionary with:
        - is_reasonable: Boolean indicating if all dimensions are in range
        - high_uncertainty: Boolean indicating if any dimension is outside range
        - issues: List of dimension names that are outside range
    """
    BOB_ZONE_MIN = 0.05  # inches
    BOB_ZONE_MAX = 50.0  # inches
    
    issues = []
    
    for dim_name, dim_value in bbox_inches.items():
        if dim_value < BOB_ZONE_MIN:
            issues.append(f"{dim_name} too small ({dim_value:.4f}\" < {BOB_ZONE_MIN}\")")
        elif dim_value > BOB_ZONE_MAX:
            issues.append(f"{dim_name} too large ({dim_value:.4f}\" > {BOB_ZONE_MAX}\")")
    
    is_reasonable = len(issues) == 0
    high_uncertainty = not is_reasonable
    
    return {
        'is_reasonable': is_reasonable,
        'high_uncertainty': high_uncertainty,
        'issues': issues
    }

