"""
Flask API for geometry analysis and pricing calculations.
"""
import os
import time
import base64
import json
import uuid
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import trimesh
import psutil

# Custom Modules
from .pricing_engine import PriceCalculator
from .estimator import estimate_runtime, suggest_stock, calculate_geometry_raw, get_unit_options, calculate_geometry
from . import genesis_hash
from . import pdf_generator
import vector_engine  # Cross-layer utility (remains at root)
import database  # Cross-layer utility (remains at root)
from cutter_ledger.boundary import emit_cutter_event
from state_ledger import validation as state_validation
from .ledger_events import emit_carrier_handoff
from .query_a import get_query_a_open_deadlines
from cutter_ledger.queries import query_dwell_vs_expectation, query_open_response_deadlines
from .preflight import run_preflight_or_exit

# --- CONFIGURATION (AIR GAP ANCHOR) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Flask paths now point to ops_layer subdirectories
app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))
CORS(app)

# Physical Anchor: Bypass all BASE_DIR logic and set hard-coded path
app.config['UPLOAD_FOLDER'] = r'C:\cutter_assets'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize database
database.initialize_database()
# Fail-fast if ledger schema/triggers are missing
run_preflight_or_exit()

# Default values
DEFAULT_MATERIAL = "Aluminum 6061"
# Refactoring Strike 1: DEFAULT_SHOP_RATE now comes from shop_config table
def DEFAULT_SHOP_RATE() -> float:
    return database.get_config('shop_rate_standard', 75.0)

# --- HELPER FUNCTIONS ---

OPS_MODE_VALUES = {"execution", "planning"}
EXECUTION_FORBIDDEN_KEYS = {
    "aggregate",
    "aggregates",
    "cluster_stats",
    "dashboard",
    "dashboards",
    "explanation",
    "history_match",
    "interpretation",
    "interpretations",
    "local_history_analysis",
    "market_analysis",
    "metrics",
    "recommendation",
    "recommendations",
    "variance_pct",
    "why",
}


def get_ops_mode() -> str | None:
    """Return explicit ops_mode from request or None if missing/invalid."""
    mode = None
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        mode = payload.get("ops_mode") or payload.get("mode")
    if not mode:
        mode = request.form.get("ops_mode")
    if not mode:
        mode = request.args.get("ops_mode")
    if not mode:
        mode = request.headers.get("X-Ops-Mode")
    if mode not in OPS_MODE_VALUES:
        return None
    return mode


def require_ops_mode():
    mode = get_ops_mode()
    if mode is None:
        return None, (jsonify({"error": "ops_mode is required", "success": False}), 400)
    return mode, None


def strip_execution_fields(payload: Any) -> Any:
    if isinstance(payload, dict):
        return {
            key: strip_execution_fields(value)
            for key, value in payload.items()
            if key not in EXECUTION_FORBIDDEN_KEYS
        }
    if isinstance(payload, list):
        return [strip_execution_fields(item) for item in payload]
    return payload


def apply_execution_guard(payload: Dict[str, Any], mode: str | None = None) -> Dict[str, Any]:
    if mode is None:
        mode = get_ops_mode()
    if mode == "execution":
        return strip_execution_fields(payload)
    return payload

def load_mesh_file(file_path: str) -> trimesh.Trimesh:
    """Load a mesh file (STL or STEP) using trimesh."""
    if not isinstance(file_path, str):
        file_path = str(file_path)
    
    print(f"DEBUG: Loading mesh from {file_path}")
    
    try:
        mesh = trimesh.load(file_path)
        # Handle Scene objects (common with STEP files)
        if isinstance(mesh, trimesh.Scene):
            # Concatenate all geometries in the scene
            geometries = list(mesh.geometry.values())
            if not geometries:
                raise ValueError("Scene is empty")
            mesh = trimesh.util.concatenate(geometries)
        return mesh
    except Exception as e:
        raise RuntimeError(f"Failed to load mesh file from {file_path}: {str(e)}")

# --- CORE ENDPOINTS ---

@app.route('/quote', methods=['POST'])
def quote() -> Dict[str, Any]:
    """POST /quote endpoint."""
    try:
        mode, error = require_ops_mode()
        if error:
            return error
        print("[DEBUG] /quote endpoint called", flush=True)
        print(f"[DEBUG] request.files keys: {list(request.files.keys())}", flush=True)
        print(f"[DEBUG] request.form keys: {list(request.form.keys())}", flush=True)
        
        if 'file' not in request.files:
            print("[ERROR] No file in request.files")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        print(f"[DEBUG] File object: {file}")
        print(f"[DEBUG] Filename: {file.filename}")
        
        if file.filename == '':
            print("[ERROR] Empty filename")
            return jsonify({'error': 'No file selected'}), 400
        
        # Get parameters
        material_name = request.form.get('material_name', DEFAULT_MATERIAL)
        try:
            shop_rate_hour = float(request.form.get('shop_rate_hour', DEFAULT_SHOP_RATE()))
        except ValueError:
            shop_rate_hour = DEFAULT_SHOP_RATE()
        
        # Save file
        filename = secure_filename(file.filename)
        export_dir = app.config['UPLOAD_FOLDER']
        if os.environ.get('TEST_DB_PATH'):
            export_dir = tempfile.gettempdir()
        filepath = os.path.join(export_dir, filename)
        
        print(f"[FILE] Saving file to: {filepath}")
        file.save(filepath)
        print(f"[FILE] File saved successfully")
        
        # OPTIMIZATION PASS 1: Load mesh ONCE and reuse the object
        try:
            print(f"[DEBUG] Loading mesh from: {filepath}")
            mesh_obj = load_mesh_file(filepath)
            print(f"[DEBUG] Mesh loaded successfully: {type(mesh_obj)}")
        except Exception as e:
            print(f"[ERROR] Failed to load mesh: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Failed to load mesh: {str(e)}'}), 400
        
        # 1. PHYSICS (The Anchor)
        # Pass mesh object instead of filepath to avoid double-loading
        try:
            print("=" * 60)
            print(f"[PROCESSING] FILE: {filename.split('.')[-1].upper()}")
            
            # Smart unit detection happens inside calculate_geometry
            volume, bbox, surface_area, assumed_units = calculate_geometry(mesh_obj)
            
            print(f"[SUCCESS] FINAL GEOMETRY:")
            print(f"   Volume: {volume:.6f} in³")
            print(f"   BBox: {bbox['x']:.4f} x {bbox['y']:.4f} x {bbox['z']:.4f} inches")
            print(f"   Surface Area: {surface_area:.6f} in²")
            print(f"   Assumed Units: {assumed_units}")
            print("=" * 60)
        except Exception as e:
            return jsonify({'error': f'Geometry calculation failed: {str(e)}'}), 400
        
        # Generate Genesis Hash (The "ISBN" of this part)
        try:
            part_genesis_hash, _, _ = genesis_hash.generate_from_trimesh(mesh_obj)
            print(f"[GENESIS HASH] Generated: {part_genesis_hash[:16]}...")
        except Exception as e:
            print(f"[WARNING] Genesis Hash generation failed: {str(e)}")
            part_genesis_hash = None
        
        stock_x, stock_y, stock_z, stock_vol = suggest_stock(bbox['x'], bbox['y'], bbox['z'])
        
        # Estimate runtime
        runtime_breakdown = estimate_runtime(
            part_volume_in3=volume,
            stock_volume_in3=stock_vol,
            material_name=material_name
        )
        
        # Calculate physics price
        calculator = PriceCalculator()
        physics_result = calculator.calculate_anchor(
            stock_volume_in3=stock_vol,
            material_name=material_name,
            per_part_time_mins=runtime_breakdown['per_part_time_mins'],
            setup_time_mins=runtime_breakdown['setup_time_mins'],
            shop_rate_hour=shop_rate_hour,
            quantity=1
        )
        
        # 2. BRAIN (5D Vector Search)
        fingerprint = vector_engine.create_fingerprint(volume, bbox, surface_area)
        
        # Pass current volume for the Vise Check logic
        similar_parts = vector_engine.find_similar_parts(fingerprint, current_vol=volume)
        
        # --- PHASE 2: THE BRAIN UPGRADE (Cluster Inference) ---
        # Analyze the entire cluster instead of just the first match
        # PHASE 3 REMEDIATION: Renamed market_analysis → local_history_analysis (clarity)
        local_history_analysis = None
        if similar_parts:
            cluster_stats = vector_engine.analyze_cluster(similar_parts)

            if cluster_stats:
                # Compare current Physics Price vs Historical Median
                current_price = physics_result['total_price']
                median = cluster_stats['median_price']
                
                # Variance: Positive = Current is Higher. Negative = Current is Lower.
                variance_pct = ((current_price - median) / median) * 100 if median > 0 else 0
                
                local_history_analysis = {
                    'cluster_stats': cluster_stats,
                    'variance_pct': round(variance_pct, 1),
                    'recommendation': 'High' if variance_pct > 15 else 'Low' if variance_pct < -15 else 'Safe'
                }
                
                print(f"[CLUSTER] ANALYSIS:")
                print(f"   Similar Parts Found: {cluster_stats['count']}")
                print(f"   Price Range: ${cluster_stats['min_price']:.2f} - ${cluster_stats['max_price']:.2f}")
                print(f"   Median: ${cluster_stats['median_price']:.2f}")
                print(f"   Current vs Median: {variance_pct:+.1f}% ({market_analysis['recommendation']})")
        
        # 3. OPTIMIZATION PASS 1: Stream URL instead of Base64
        # Generate model URL for browser streaming (no memory bloat)
        model_url = f'/files/{filename}'
        
        response = {
            'filename': filename,
            'genesis_hash': part_genesis_hash,  # Phase 5.5: The "ISBN" of this part
            'geometry': {
                'volume': volume,
                'bbox': bbox,
                'surface_area': surface_area,
                'stock': {'x': stock_x, 'y': stock_y, 'z': stock_z},
                'stock_volume': stock_vol
            },
            'physics_price': {
                'total_price': round(physics_result['total_price'], 2),
                'material_cost': round(physics_result['material_cost'], 2),
                'labor_cost': round(physics_result['labor_cost'], 2)
            },
            # Legacy support for older frontend
            'price': {
                'total_price': round(physics_result['total_price'], 2)
            },
            'stock': {'volume': stock_vol, 'x': stock_x, 'y': stock_y, 'z': stock_z},
            'runtime': {
                'minutes': round(physics_result['total_runtime_mins'], 2),
                'total_time_mins': round(physics_result['total_runtime_mins'], 2),
                'machine_time_mins': round(runtime_breakdown['machine_time_mins'], 2),
                'hand_time_mins': round(runtime_breakdown['hand_time_mins'], 2)
            },
            'material': material_name,
            'shop_rate': shop_rate_hour,
            'setup_time': 60.0,
            'fingerprint': fingerprint,
            'model_url': model_url,  # OPTIMIZATION PASS 1: Stream URL instead of Base64
            'local_history_analysis': local_history_analysis  # PHASE 3: Renamed from market_analysis
        }
        
        # 4. GHOST PROTOCOL (Inheritance)
        # THRESHOLD: < 2.5 for "Fuzzy Matching" (Mutations)
        if similar_parts and similar_parts[0]['distance'] < 2.5:
            top_match = similar_parts[0]
            
            # --- FIX: ROBUST JSON PARSING ---
            # Handle cases where tag_weights is already a dict OR a JSON string
            tag_weights_dict = {}
            raw_weights = top_match.get('tag_weights')
            
            if raw_weights:
                if isinstance(raw_weights, dict):
                    # Already a dictionary - use directly
                    tag_weights_dict = raw_weights
                elif isinstance(raw_weights, str) and raw_weights.strip():
                    # JSON string - parse it
                    try:
                        tag_weights_dict = json.loads(raw_weights)
                        # Ensure it's a dict after parsing
                        if not isinstance(tag_weights_dict, dict):
                            tag_weights_dict = {}
                    except (json.JSONDecodeError, TypeError):
                        # Invalid JSON - default to empty dict
                        tag_weights_dict = {}

            # Format tags for display string
            tag_parts = []
            if tag_weights_dict:
                for tag, weight in tag_weights_dict.items():
                    tag_parts.append(f"{tag}")
            tags_display = ', '.join(tag_parts) if tag_parts else 'No tags'
            
            # Parse process_routing (Traveler Tags) from history match
            process_routing_list = []
            raw_routing = top_match.get('process_routing')
            if raw_routing:
                if isinstance(raw_routing, list):
                    process_routing_list = raw_routing
                elif isinstance(raw_routing, str) and raw_routing.strip():
                    try:
                        process_routing_list = json.loads(raw_routing)
                        if not isinstance(process_routing_list, list):
                            process_routing_list = []
                    except (json.JSONDecodeError, TypeError):
                        process_routing_list = []
            
            response['history_match'] = {
                'last_price': top_match['final_price'],
                'tags': tags_display,
                'setup_time': top_match.get('setup_time'),
                'tag_weights': tag_weights_dict, # Send the clean dict
                'date': top_match.get('timestamp', ''),
                'match_type': top_match.get('match_type', 'twin'),
                'process_routing': process_routing_list  # Traveler Tags (Ghost Protocol)
            }
            
        response = apply_execution_guard(response)
        return jsonify(response)
        
    except Exception as e:
        # Comprehensive error logging for debugging
        import traceback
        error_details = traceback.format_exc()
        print("=" * 60)
        print("[ERROR] ERROR IN /quote ENDPOINT:")
        print(error_details)
        print("=" * 60)
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/quote/confirm-units', methods=['POST'])
def confirm_units() -> Dict[str, Any]:
    """POST /quote/confirm-units endpoint."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    unit_option = request.form.get('unit_option', 'option_2')
    material_name = request.form.get('material_name', DEFAULT_MATERIAL)
    try:
        shop_rate_hour = float(request.form.get('shop_rate_hour', DEFAULT_SHOP_RATE()))
    except ValueError:
        shop_rate_hour = DEFAULT_SHOP_RATE()
    
    # Save temp file
    filename = secure_filename(file.filename).lower()
    temp_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(temp_file_path)
    
    # Atomic flush (Windows compat)
    with open(temp_file_path, 'rb+') as f:
        f.flush()
        os.fsync(f.fileno())
    
    try:
        # Load mesh
        mesh = load_mesh_file(temp_file_path)
        
        # Calculate Geometry Options
        raw_geometry = calculate_geometry_raw(mesh)
        unit_options = get_unit_options(raw_geometry['bbox_raw'], raw_geometry['volume_raw'])
        
        # Select Unit
        if unit_option == 'option_1': # Inches
            bbox_x = unit_options['as_inches']['x']
            bbox_y = unit_options['as_inches']['y']
            bbox_z = unit_options['as_inches']['z']
            part_volume_in3 = unit_options['as_inches']['volume']
        else: # MM
            bbox_x = unit_options['as_mm_converted']['x']
            bbox_y = unit_options['as_mm_converted']['y']
            bbox_z = unit_options['as_mm_converted']['z']
            part_volume_in3 = unit_options['as_mm_converted']['volume']
            
        stock_x, stock_y, stock_z, stock_volume_in3 = suggest_stock(bbox_x, bbox_y, bbox_z)
        
        # Runtime
        runtime_breakdown = estimate_runtime(part_volume_in3, stock_volume_in3, material_name)
        
        # Price
        calculator = PriceCalculator()
        price_result = calculator.calculate_anchor(
            stock_volume_in3=stock_volume_in3,
            material_name=material_name,
            per_part_time_mins=runtime_breakdown['per_part_time_mins'],
            setup_time_mins=runtime_breakdown['setup_time_mins'],
            shop_rate_hour=shop_rate_hour
        )
        
        # Price Breaks
        price_breaks = calculator.calculate_price_breaks(
            stock_volume_in3=stock_volume_in3,
            material_name=material_name,
            per_part_time_mins=runtime_breakdown['per_part_time_mins'],
            setup_time_mins=runtime_breakdown['setup_time_mins'],
            shop_rate_hour=shop_rate_hour
        )
        
        physics_price = round(price_result['total_price'], 2)
        
        # Fingerprint
        surface_area_approx = part_volume_in3 * 6 
        fingerprint = vector_engine.create_fingerprint(part_volume_in3, {'x':bbox_x, 'y':bbox_y, 'z':bbox_z}, surface_area_approx)
        
        # Search History
        similar_parts = vector_engine.find_similar_parts(fingerprint, current_vol=part_volume_in3)
        
        history_match = None
        # THRESHOLD: < 2.5
        if similar_parts and similar_parts[0]['distance'] < 2.5:
            best_match = similar_parts[0]
            
            # --- FIX: ROBUST JSON PARSING ---
            tag_weights_dict = {}
            raw_weights = best_match.get('tag_weights')
            
            if raw_weights:
                if isinstance(raw_weights, dict):
                    tag_weights_dict = raw_weights
                elif isinstance(raw_weights, str):
                    try:
                        tag_weights_dict = json.loads(raw_weights)
                    except:
                        pass
            
            tag_parts = []
            for tag, weight in tag_weights_dict.items():
                tag_parts.append(f"{tag}")
            tags_display = ', '.join(tag_parts) if tag_parts else 'No tags'
            
            # Parse process_routing (Traveler Tags) from history match
            process_routing_list = []
            raw_routing = best_match.get('process_routing')
            if raw_routing:
                if isinstance(raw_routing, list):
                    process_routing_list = raw_routing
                elif isinstance(raw_routing, str) and raw_routing.strip():
                    try:
                        process_routing_list = json.loads(raw_routing)
                        if not isinstance(process_routing_list, list):
                            process_routing_list = []
                    except (json.JSONDecodeError, TypeError):
                        process_routing_list = []
            
            history_match = {
                'last_price': round(best_match['final_price'], 2),
                'tags': tags_display,
                'tag_weights': tag_weights_dict,
                'setup_time': best_match.get('setup_time'),
                'process_routing': process_routing_list  # Traveler Tags (Ghost Protocol)
            }
            
        response = {
            'price': {
                'total_price': physics_price,
                'material_cost': round(price_result['material_cost'], 2),
                'labor_cost': round(price_result['labor_cost'], 2)
            },
            'price_breaks': price_breaks,
            'dimensions': {
                'part': {
                    'x': round(bbox_x, 3),
                    'y': round(bbox_y, 3),
                    'z': round(bbox_z, 3),
                    'volume': round(part_volume_in3, 6)
                }
            },
            'stock': {
                'x': round(stock_x, 3),
                'y': round(stock_y, 3),
                'z': round(stock_z, 3),
                'volume': round(stock_volume_in3, 6)
            },
            'runtime': {
                'minutes': round(runtime_breakdown['total_time_mins'], 2),
                'machine_time_mins': round(runtime_breakdown['machine_time_mins'], 2),
                'hand_time_mins': round(runtime_breakdown['hand_time_mins'], 2),
                'total_run_time_mins': round(runtime_breakdown['total_run_time_mins'], 2)
            },
            'material': material_name,
            'shop_rate': shop_rate_hour,
            'setup_time': 60.0,
            'part_volume': round(part_volume_in3, 6),
            'fingerprint': fingerprint,
            'anchor_price': physics_price,
            'requires_unit_confirmation': False,
            'file_path': f'/uploads/{filename}'
        }
        
        if history_match:
            response['history_match'] = history_match
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(temp_file_path):
            try: os.remove(temp_file_path)
            except: pass


@app.route('/recalculate', methods=['POST'])
def recalculate() -> Dict[str, Any]:
    """POST /recalculate endpoint."""
    try:
        mode = get_ops_mode() or "planning"
        data = request.get_json()
        if not data: return jsonify({'error': 'No data'}), 400
        
        # Extract
        material_name = data.get('material_name', DEFAULT_MATERIAL)
        stock_vol = float(data.get('stock_x', 0)) * float(data.get('stock_y', 0)) * float(data.get('stock_z', 0))
        part_volume = float(data.get('part_volume', 0))
        setup_time = float(data.get('setup_time', 60.0))
        shop_rate = float(data.get('shop_rate', DEFAULT_SHOP_RATE()))
        # Phase 5: Complexity slider removed - anchor must be pure physics
        complexity = 1.0  # Always 1.0 for pure physics anchor
        quantity = int(data.get('quantity', 1))
        handling_time = float(data.get('handling_time', 0.5))
        
        # Calculate Runtime
        score = database.get_material_score(material_name)
        if score is None:
            print(f"WARNING: Material '{material_name}' not found. Using fallback pricing.")
            score = 1.0  # Aluminum 6061 machinability score
        from estimator import BASE_MRR, MIN_HAND_TIME_PER_PART
        adjusted_mrr = BASE_MRR() / score
        removal_vol = max(0, stock_vol - part_volume)
        # FIX: Lowered minimum from 1.0 to 0.1 to allow price sensitivity on small parts
        base_machine = max(removal_vol / adjusted_mrr, 0.1)
        
        # Pure physics runtime (no complexity multiplier - Phase 5)
        machine_time = base_machine
        hand_time = MIN_HAND_TIME_PER_PART()
        per_part_time = machine_time + hand_time
        
        # Pricing - Include handling time in per-part calculation
        calculator = PriceCalculator()
        price_result = calculator.calculate_anchor(
            stock_volume_in3=stock_vol,
            material_name=material_name,
            per_part_time_mins=per_part_time,
            setup_time_mins=setup_time,
            shop_rate_hour=shop_rate,
            quantity=quantity,
            handling_time_mins=handling_time
        )
        
        # Calculate total runtime: one-time setup + ((per-part time + handling time) × quantity)
        total_runtime_mins = setup_time + ((per_part_time + handling_time) * quantity)
        
        response = {
            'total_price': round(price_result['total_price'], 2),
            'material_cost': round(price_result['material_cost'], 2),
            'labor_cost': round(price_result['labor_cost'], 2),
            'total_runtime_mins': round(total_runtime_mins, 2),
            'per_part_time_mins': round(per_part_time, 2),
            'setup_time_mins': round(setup_time, 2),
            'machine_time_mins': round(machine_time, 2),
            'hand_time_mins': round(hand_time, 2),
            'quantity': quantity
        }
        response = apply_execution_guard(response)
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/manual_quote', methods=['POST'])
def manual_quote() -> Dict[str, Any]:
    """
    POST /manual_quote endpoint - Napkin Mode (Manual Entry).
    Calculates pricing without a 3D file, using stock dimensions and removal rate.
    """
    try:
        mode = get_ops_mode() or "execution"
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract parameters
        stock_x = float(data.get('stock_x', 0))
        stock_y = float(data.get('stock_y', 0))
        stock_z = float(data.get('stock_z', 0))
        material_name = data.get('material_name', data.get('material', DEFAULT_MATERIAL))
        
        # FIX: Define part_volume_in3 explicitly here to avoid NameError later
        part_volume_in3 = float(data.get('part_volume', 0)) 
        
        # Phase 5: Complexity slider removed - anchor must be pure physics
        complexity = 1.0  # Always 1.0 for pure physics anchor
        setup_time = float(data.get('setup_time', 60.0))
        shop_rate_hour = float(data.get('shop_rate', DEFAULT_SHOP_RATE()))
        quantity = int(data.get('quantity', 1))
        handling_time = float(data.get('handling_time', 0.5))
        
        # Get reference name (filename) - use provided name or generate default
        reference_name = data.get('filename', data.get('reference_name', ''))
        if not reference_name or not reference_name.strip():
            # Generate default name with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime('%b %d, %I:%M %p')
            reference_name = f'Manual Quote - {timestamp}'
        
        # Validation
        if stock_x <= 0 or stock_y <= 0 or stock_z <= 0:
            return jsonify({'error': 'Stock dimensions must be greater than 0'}), 400
        
        if not material_name:
            return jsonify({'error': 'Material is required'}), 400
        
        # Calculate volumes
        stock_volume_in3 = stock_x * stock_y * stock_z
        
        # Validate part volume
        if part_volume_in3 <= 0:
            return jsonify({'error': 'Part volume must be greater than 0'}), 400
        
        if part_volume_in3 > stock_volume_in3:
            return jsonify({'error': 'Part volume cannot exceed stock volume'}), 400
        
        # FIX: Ensure calculation uses correct variable name
        removal_volume_in3 = stock_volume_in3 - part_volume_in3
        
        # Estimate runtime (based on removal volume for machining time calculation)
        runtime_breakdown = estimate_runtime(
            part_volume_in3=part_volume_in3,
            stock_volume_in3=stock_volume_in3,
            material_name=material_name
        )
        
        # Pure physics runtime (no complexity multiplier - Phase 5)
        machine_time = runtime_breakdown['machine_time_mins']
        hand_time = runtime_breakdown['hand_time_mins']
        per_part_time = machine_time + hand_time
        
        # Calculate physics price
        # FIX: No longer need to manually amortize - calculator handles setup correctly now
        calculator = PriceCalculator()
        physics_result = calculator.calculate_anchor(
            stock_volume_in3=stock_volume_in3,
            material_name=material_name,
            per_part_time_mins=per_part_time,
            setup_time_mins=setup_time,
            shop_rate_hour=shop_rate_hour,
            quantity=quantity,
            handling_time_mins=handling_time
        )
        
        # --- PHASE 1: THE SYNTHETIC BRIDGE (Napkin Mode Upgrade) ---
        # Generate synthetic geometry to create a real 5D Fingerprint
        # This makes manual quotes searchable by the Vector Engine
        try:
            print(f"[SYNTHETIC] SYNTHETIC BRIDGE: Generating Virtual Twin...")
            
            # 1. Generate Synthetic Mesh (Box) representing the stock envelope
            # trimesh expects extents as [x, y, z] in consistent units (we use inches)
            synthetic_mesh = trimesh.creation.box(extents=[stock_x, stock_y, stock_z])
            
            # 2. Extract Geometry Data
            # Surface Area: Use the stock's surface area as a proxy for complexity
            synthetic_area = synthetic_mesh.area
            
            # BBox: Stock dimensions
            bbox = {'x': stock_x, 'y': stock_y, 'z': stock_z}
            
            # 3. Generate 5D Vector Fingerprint
            # [Vol/10, Small_Dim, Mid_Dim, Large_Dim, Area/50]
            # Use PART volume (finished geometry), not stock volume
            fingerprint = vector_engine.create_fingerprint(
                part_volume_in3, 
                bbox, 
                synthetic_area
            )
            
            # 4. Generate Genesis Hash (The ISBN)
            # Use part volume + stock dims to create the unique ID
            genesis_hash = vector_engine.generate_genesis_hash(
                part_volume_in3, 
                [stock_x, stock_y, stock_z]
            )
            
            print(f"[SUCCESS] Synthetic Twin Created: {genesis_hash}")
            print(f"   [DATA] 5D Fingerprint: {[round(f, 3) for f in fingerprint]}")
            print(f"   [DATA] Surface Area: {synthetic_area:.2f} in^2")
            
        except Exception as e:
            print(f"[WARNING] Synthetic Generation Failed: {e}")
            import traceback
            traceback.print_exc()
            fingerprint = []
            genesis_hash = None
            synthetic_area = 0
        
        # --- PHASE 2: THE BRAIN UPGRADE (Cluster Inference) ---
        # Find similar parts using the synthetic fingerprint
        # PHASE 3 REMEDIATION: Renamed market_analysis → local_history_analysis
        local_history_analysis = None
        if fingerprint:  # Only if we have a valid fingerprint
            similar_parts = vector_engine.find_similar_parts(fingerprint, current_vol=part_volume_in3)
            
            if similar_parts:
                cluster_stats = vector_engine.analyze_cluster(similar_parts)
                
                if cluster_stats:
                    # Compare current Physics Price vs Historical Median
                    current_price = physics_result['total_price']
                    median = cluster_stats['median_price']
                    
                    # Variance: Positive = Current is Higher. Negative = Current is Lower.
                    variance_pct = ((current_price - median) / median) * 100 if median > 0 else 0
                    
                    local_history_analysis = {
                        'cluster_stats': cluster_stats,
                        'variance_pct': round(variance_pct, 1),
                        'recommendation': 'High' if variance_pct > 15 else 'Low' if variance_pct < -15 else 'Safe'
                    }
                    
                    print(f"[CLUSTER] ANALYSIS (Manual Quote):")
                    print(f"   Similar Parts Found: {cluster_stats['count']}")
                    print(f"   Price Range: ${cluster_stats['min_price']:.2f} - ${cluster_stats['max_price']:.2f}")
                    print(f"   Median: ${cluster_stats['median_price']:.2f}")
                    print(f"   Current vs Median: {variance_pct:+.1f}% ({market_analysis['recommendation']})")
        
        # Calculate total runtime and amortized values for display
        # Formula: Setup (once) + ((Per-Part Time + Handling Time) × Quantity)
        total_runtime_mins = setup_time + ((per_part_time + handling_time) * quantity)
        amortized_setup = setup_time / quantity if quantity > 0 else setup_time
        amortized_runtime = total_runtime_mins / quantity if quantity > 0 else total_runtime_mins
        
        # DEBUG LOGGING
        print(f"--- MANUAL QUOTE DEBUG ---")
        print(f"Stock Dims: {stock_x} x {stock_y} x {stock_z} = {stock_volume_in3:.4f} in3")
        print(f"Material: {material_name}")
        print(f"Quantity: {quantity}")
        print(f"Removal Vol: {removal_volume_in3:.4f} in3")
        print(f"Machine Time: {machine_time:.2f} min | Hand Time: {hand_time:.2f} min")
        print(f"Per-Part Time: {per_part_time:.2f} min")
        print(f"Setup Time: {setup_time:.2f} min | Amortized: {amortized_setup:.2f} min/part")
        print(f"Total Runtime: {total_runtime_mins:.2f} min | Amortized: {amortized_runtime:.2f} min/part")
        print(f"Material Cost: ${physics_result['material_cost']:.2f}")
        print(f"Labor Cost: ${physics_result['labor_cost']:.2f}")
        print(f"Total Price: ${physics_result['total_price']:.2f}")
        print(f"--------------------------")
        
        # Create response matching /quote structure
        response = {
            'filename': reference_name,
            'geometry': {
                'volume': part_volume_in3,
                'bbox': {'x': stock_x, 'y': stock_y, 'z': stock_z},
                'surface_area': synthetic_area,  # Synthetic Bridge: Real surface area
                'stock': {'x': stock_x, 'y': stock_y, 'z': stock_z},
                'stock_volume': stock_volume_in3
            },
            'physics_price': {
                'total_price': round(physics_result['total_price'], 2),
                'material_cost': round(physics_result['material_cost'], 2),
                'labor_cost': round(physics_result['labor_cost'], 2)
            },
            'price': {
                'total_price': round(physics_result['total_price'], 2)
            },
            'stock': {
                'volume': stock_volume_in3,
                'x': stock_x,
                'y': stock_y,
                'z': stock_z
            },
            'runtime': {
                'minutes': round(total_runtime_mins, 2),
                'machine_time_mins': round(machine_time, 2),
                'hand_time_mins': round(hand_time, 2),
                'total_time_mins': round(total_runtime_mins, 2),
                'per_part_time_mins': round(per_part_time, 2),
                'setup_time_mins': round(setup_time, 2)
            },
            'material': material_name,
            'shop_rate': shop_rate_hour,
            'setup_time': setup_time,
            'fingerprint': fingerprint,  # Synthetic Bridge: Real 5D Vector
            'genesis_hash': genesis_hash,  # Synthetic Bridge: The ISBN
            'stl_data': '',  # No 3D model in manual mode
            'anchor_price': round(physics_result['total_price'], 2),
            'is_manual': True,  # Flag to indicate manual mode
            'local_history_analysis': local_history_analysis  # PHASE 3: Renamed from market_analysis
        }
        
        return jsonify(response)
        
    except Exception as e:
        # Log the full stack trace to the console for debugging
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/upload_reference_image', methods=['POST'])
def upload_reference_image() -> Dict[str, Any]:
    r"""
    POST /upload_reference_image endpoint - Evidence Locker (Napkin Mode).
    Accepts JPG/PNG images via drag-drop or paste, saves to C:\cutter_assets\images.
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'jpg', 'jpeg', 'png'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if file_ext not in allowed_extensions:
            return jsonify({'error': 'Invalid file type. Only JPG and PNG are allowed.'}), 400
        
        # Create assets directory if it doesn't exist
        assets_dir = r'C:\cutter_assets\images'
        os.makedirs(assets_dir, exist_ok=True)
        
        # Generate unique filename (timestamp + original name)
        timestamp = int(time.time() * 1000)  # Milliseconds
        safe_filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(assets_dir, safe_filename)
        
        # Save file
        file.save(filepath)
        
        # Return relative path (for storage in database)
        relative_path = f'C:\\cutter_assets\\images\\{safe_filename}'
        
        return jsonify({
            'success': True,
            'path': relative_path,
            'filename': safe_filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/save_quote', methods=['POST'])
def save_quote_endpoint() -> Dict[str, Any]:
    """
    POST /save_quote endpoint (Option B Refactor).
    Step 1: Upsert part (get or create part_id)
    Step 2: Create quote (link to part_id)
    """
    try:
        data = request.get_json()
        
        # --- STEP 1: EXTRACT PART DATA ---
        
        # Extract fingerprint and reverse engineer raw physics values
        fingerprint = data.get('fingerprint', [])
        part_genesis_hash = None
        raw_vol = 0.0
        raw_dims = [0, 0, 0]
        
        # Phase 5.5: Check for parametric shape data (Napkin Mode)
        shape_config = data.get('shape_config', None)
        if shape_config and isinstance(shape_config, dict):
            # Parametric shape from Napkin Mode
            shape_type = shape_config.get('type')
            dimensions = shape_config.get('dimensions', {})
            volume_in3 = shape_config.get('volume', 0)
            
            if shape_type and dimensions and volume_in3 > 0:
                try:
                    part_genesis_hash, bounding_dims = genesis_hash.generate_from_parametric(
                        volume_in3=volume_in3,
                        shape_type=shape_type,
                        dimensions=dimensions
                    )
                    raw_vol = volume_in3
                    raw_dims = list(bounding_dims)
                    print(f"[GENESIS HASH] Generated from parametric shape: {part_genesis_hash[:16]}...")
                except Exception as e:
                    print(f"[WARNING] Failed to generate Genesis Hash from parametric shape: {e}")
        
        # Fallback: Generate from fingerprint (File Mode or legacy)
        if not part_genesis_hash and fingerprint and len(fingerprint) >= 4:
            # Fingerprint format: [Vol/10, Small_Dim, Mid_Dim, Large_Dim, Area/50]
            raw_vol = fingerprint[0] * 10.0
            raw_dims = [fingerprint[1], fingerprint[2], fingerprint[3]]
            
            # Generate Genesis Hash (The ISBN)
            part_genesis_hash = vector_engine.generate_genesis_hash(raw_vol, raw_dims)
        
        if not part_genesis_hash:
            return jsonify({'error': 'Invalid geometry data - cannot generate genesis_hash'}), 400
        
        # Extract part properties
        filename = data.get('filename', 'unknown')
        fingerprint_json = json.dumps(fingerprint)
        volume = raw_vol
        surface_area = fingerprint[4] * 50.0 if len(fingerprint) >= 5 else 0.0
        dimensions_json = json.dumps({'x': raw_dims[0], 'y': raw_dims[1], 'z': raw_dims[2]})
        
        # Extract process_routing (Traveler Tags)
        process_routing = data.get('process_routing', [])
        if not isinstance(process_routing, list):
            process_routing = []
        process_routing_json = json.dumps(process_routing)
        
        # Upsert part (get existing or create new)
        part_id = database.upsert_part(
            genesis_hash=part_genesis_hash,
            filename=filename,
            fingerprint_json=fingerprint_json,
            volume=volume,
            surface_area=surface_area,
            dimensions_json=dimensions_json,
            process_routing_json=process_routing_json
        )
        
        # --- STEP 2: RESOLVE CUSTOMER & CONTACT (4-Table Identity Model) ---
        
        # Extract customer/contact info
        customer_name = data.get('customer_name', 'Walk-In Customer')
        customer_domain = data.get('customer_domain', None)
        contact_name = data.get('contact_name', '')
        contact_email = data.get('contact_email', '')
        contact_phone = data.get('contact_phone', '')
        
        # Parse email domain for customer resolution (if not already provided)
        if not customer_domain and contact_email and '@' in contact_email:
            customer_domain = contact_email.split('@')[1].lower()
        
        # Resolve customer (by domain or name) - returns (id, metadata)
        customer_id, customer_metadata = database.resolve_customer(customer_name, customer_domain)
        
        # Emit customer resolution event
        try:
            if customer_metadata['resolution_action'] == 'created':
                emit_cutter_event(
                    event_type='CUSTOMER_CREATED',
                    subject_ref=f'customer:{customer_id}',
                    event_data={
                        'name': customer_name,
                        'input_domain_present': customer_metadata['input_domain_present']
                    }
                )
            else:
                emit_cutter_event(
                    event_type='CUSTOMER_RESOLVED',
                    subject_ref=f'customer:{customer_id}',
                    event_data={
                        'match_method': customer_metadata['resolution_action'],
                        'input_domain_present': customer_metadata['input_domain_present']
                    }
                )
        except Exception as event_error:
            print(f"[LEDGER] Customer resolution event emission failed: {event_error}")
        
        # Resolve contact (by email, handles roaming buyers) - returns (id, metadata)
        contact_id = None
        if contact_name or contact_email:
            contact_id, contact_metadata = database.resolve_contact(
                name=contact_name if contact_name else "Anonymous",
                email=contact_email if contact_email else "",
                customer_id=customer_id,
                phone=contact_phone if contact_phone else None
            )
            
            # Emit contact resolution events
            try:
                if contact_metadata['roaming']:
                    emit_cutter_event(
                        event_type='CONTACT_ROAMING_DETECTED',
                        subject_ref=f'contact:{contact_id}',
                        event_data={
                            'old_customer_id': contact_metadata['old_customer_id'],
                            'new_customer_id': customer_id
                        }
                    )
                
                if contact_metadata['resolution_action'] == 'created':
                    emit_cutter_event(
                        event_type='CONTACT_CREATED',
                        subject_ref=f'contact:{contact_id}',
                        event_data={
                            'name': contact_name if contact_name else "Anonymous",
                            'placeholder_email': contact_metadata['placeholder_email']
                        }
                    )
                else:
                    emit_cutter_event(
                        event_type='CONTACT_RESOLVED',
                        subject_ref=f'contact:{contact_id}',
                        event_data={
                            'match_method': contact_metadata['resolution_action']
                        }
                    )
            except Exception as event_error:
                print(f"[LEDGER] Contact resolution event emission failed: {event_error}")
        
        # --- STEP 3: EXTRACT QUOTE DATA ---
        
        # Extract custom quote_id from user
        custom_quote_id = data.get('quote_id', None)
        
        # Extract user_id
        user_id = data.get('user_id', None)
        
        # Extract material
        material = data.get('material', 'Unknown')
        
        # Extract transaction details (NEW for 4-Table Model)
        quantity = int(data.get('quantity', 1))
        target_date = data.get('target_date', None)  # ISO format: YYYY-MM-DD
        notes = data.get('notes', None)
        
        # Extract Glass Box variance data
        system_price_anchor = data.get('system_price_anchor', None)
        final_quoted_price = data.get('final_quoted_price', None)
        
        # If not provided, fall back to legacy fields
        if system_price_anchor is None:
            system_price_anchor = float(data.get('anchor_price', 0)) if data.get('anchor_price') else 0.0
        if final_quoted_price is None:
            final_quoted_price = float(data.get('final_price', 0))
        
        # Variance attribution
        variance_json_str = None
        if data.get('variance_attribution'):
            variance_json_str = json.dumps(data.get('variance_attribution'))
        
        # Normalize pricing tags
        tag_weights = data.get('tag_weights', {})
        normalized = {}
        for k, v in tag_weights.items():
            vf = float(v)
            if vf > 1.0: vf = vf / 100.0
            normalized[k] = max(0.0, min(1.0, vf))
        pricing_tags_json = json.dumps(normalized)
        
        # Physics Snapshot (Phase 4: Price Stack)
        # Store raw cost breakdown at quote time to prevent historical drift
        physics_snapshot = {
            'material_cost': data.get('material_cost', 0.0),
            'labor_cost': data.get('labor_cost', 0.0),
            'setup_cost': data.get('setup_cost', 0.0),
            'scrap_cost': data.get('scrap_cost', 0.0),
            'total_cost': data.get('total_cost', 0.0),
            'timestamp': datetime.now().isoformat()
        }
        physics_snapshot_json = json.dumps(physics_snapshot)
        
        # Phase 5: Extract RFQ-First Fields
        lead_time_date = data.get('lead_time_date', None)
        lead_time_days = data.get('lead_time_days', None)
        target_price_per_unit = data.get('target_price_per_unit', None)
        price_breaks_json = data.get('price_breaks_json', None)
        outside_processing_json = data.get('outside_processing_json', None)
        quality_requirements_json = data.get('quality_requirements_json', None)
        part_marking_json = data.get('part_marking_json', None)
        
        # Create quote with 4-Table Identity Model + RFQ-First Fields
        quote_record_id = database.create_quote(
            part_id=part_id,
            customer_id=customer_id,
            contact_id=contact_id,
            quote_id=custom_quote_id,
            user_id=user_id,
            material=material,
            system_price_anchor=system_price_anchor,
            final_quoted_price=final_quoted_price,
            quantity=quantity,
            target_date=target_date,
            notes=notes,
            variance_json=variance_json_str,
            pricing_tags_json=pricing_tags_json,
            physics_snapshot_json=physics_snapshot_json,
            # Phase 5: RFQ-First Fields
            lead_time_date=lead_time_date,
            lead_time_days=lead_time_days,
            target_price_per_unit=target_price_per_unit,
            price_breaks_json=price_breaks_json,
            outside_processing_json=outside_processing_json,
            quality_requirements_json=quality_requirements_json,
            part_marking_json=part_marking_json,
            status='Draft'
        )
        
        # --- CUTTER LEDGER: Emit QUOTE_CREATED event ---
        # Record quote creation in append-only ledger
        try:
            emit_cutter_event(
                event_type='QUOTE_CREATED',
                subject_ref=quote_record_id,
                event_data={
                    'quote_id_human': custom_quote_id,
                    'material': material,
                    'quantity': quantity,
                    'system_price_anchor': float(system_price_anchor),
                    'final_quoted_price': float(final_quoted_price),
                    'customer_name': customer_name,
                    'status': 'Draft'
                }
            )
            print(f"[LEDGER] QUOTE_CREATED event emitted for quote {quote_record_id}")
        except Exception as event_error:
            print(f"[LEDGER] Event emission failed: {event_error}")
        
        # --- CONTROL SURFACE: Detect and emit QUOTE_OVERRIDDEN event ---
        # Constitutional authority: C7 (Overrides Must Leave Scars)
        # Emit event when final_quoted_price != system_price_anchor
        
        from decimal import Decimal, ROUND_HALF_UP
        
        # Quantize to cents (currency semantics)
        quantized_anchor = Decimal(str(system_price_anchor)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        quantized_final = Decimal(str(final_quoted_price)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Emit if prices differ after quantization
        if quantized_final != quantized_anchor:
            override_delta = float(quantized_final - quantized_anchor)
            
            # Avoid divide-by-zero
            if quantized_anchor != 0:
                override_percent = (override_delta / float(quantized_anchor)) * 100.0
            else:
                override_percent = None
            
            event_data = {
                'system_price_anchor': float(quantized_anchor),
                'final_quoted_price': float(quantized_final),
                'override_delta': override_delta,
                'override_percent': override_percent,
                'quote_id_human': custom_quote_id,
                'material': material,
                'quantity': quantity
            }
            
            # Include variance attribution if provided
            variance_attribution = data.get('variance_attribution')
            if variance_attribution:
                event_data['variance_json'] = variance_attribution
                
                # Calculate explained vs unexplained (arithmetic only)
                if isinstance(variance_attribution, dict) and 'items' in variance_attribution:
                    explained_total = 0.0
                    for item in variance_attribution['items']:
                        if isinstance(item, dict) and item.get('type') != 'unexplained':
                            try:
                                explained_total += float(item.get('value', 0))
                            except (TypeError, ValueError):
                                pass  # Ignore non-numeric values
                    event_data['explained_amount_total'] = explained_total
                    event_data['unexplained_amount'] = override_delta - explained_total
            
            try:
                emit_cutter_event(
                    event_type='QUOTE_OVERRIDDEN',
                    subject_ref=f'quote:{quote_record_id}',
                    event_data=event_data
                )
                if override_percent is not None:
                    print(f"[LEDGER] QUOTE_OVERRIDDEN event emitted: ${override_delta:+.2f} ({override_percent:+.1f}%)")
                else:
                    print(f"[LEDGER] QUOTE_OVERRIDDEN event emitted: ${override_delta:+.2f} (anchor was zero)")
            except Exception as event_error:
                print(f"[LEDGER] Event emission failed: {event_error}")
        
        return jsonify({
            'success': True,
            'id': quote_record_id,
            'part_id': part_id,
            'customer_id': customer_id,
            'contact_id': contact_id
        })
        
    except Exception as e:
        print(f"[ERROR] Save quote failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/quote/<int:quote_id>/pdf', methods=['GET'])
def generate_quote_pdf_endpoint(quote_id: int) -> Any:
    """
    GET /api/quote/<quote_id>/pdf
    GET /api/quote/<quote_id>/pdf?internal=true
    
    Generate and serve a PDF for a specific quote.
    Local-First: Uses ReportLab (no cloud services).
    
    Query Parameters:
        internal (bool): If 'true', show Glass Box breakdown (System Anchor, Variance).
                        Default: False (customer-safe mode, only shows final price).
    
    Returns:
        PDF file download
    """
    try:
        # Check if internal view requested (default: customer-safe)
        internal_view = request.args.get('internal', 'false').lower() == 'true'
        customer_facing = not internal_view  # Invert for clarity
        # Fetch quote from database
        conn = database.get_connection()
        cursor = conn.cursor()
        
        # Query quote with all related data (4-Table Identity Model)
        cursor.execute("""
            SELECT 
                q.id, q.quote_id, q.material, q.system_price_anchor, q.final_quoted_price,
                q.variance_json, q.pricing_tags_json, q.status, q.created_at, q.user_id,
                q.quantity, q.target_date, q.notes,
                q.lead_time_date, q.lead_time_days, q.target_price_per_unit,
                q.price_breaks_json, q.outside_processing_json, q.quality_requirements_json,
                q.part_marking_json,
                p.id as part_id, p.genesis_hash, p.filename, p.fingerprint_json, 
                p.volume, p.surface_area, p.dimensions_json, p.process_routing_json,
                cu.id as customer_id, cu.name as customer_name, cu.domain as customer_domain,
                co.id as contact_id, co.name as contact_name, co.email as contact_email, co.phone as contact_phone
            FROM ops__quotes q
            JOIN ops__parts p ON q.part_id = p.id
            LEFT JOIN ops__customers cu ON q.customer_id = cu.id
            LEFT JOIN ops__contacts co ON q.contact_id = co.id
            WHERE q.id = ?
        """, (quote_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Quote not found'}), 404
        
        # Build quote_data dictionary
        quote_data = {
            # Quote data
            'id': row[0],
            'quote_id': row[1],
            'material': row[2],
            'system_price_anchor': row[3],
            'final_quoted_price': row[4],
            'variance_json': json.loads(row[5]) if row[5] else None,
            'pricing_tags_json': json.loads(row[6]) if row[6] else {},
            'status': row[7],
            'timestamp': row[8],
            'user_id': row[9],
            'quantity': row[10],
            'target_date': row[11],
            'notes': row[12],
            
            # RFQ fields
            'lead_time_date': row[13],
            'lead_time_days': row[14],
            'payment_terms_days': row[15],
            'target_price_per_unit': row[16],
            'price_breaks_json': row[17],
            'outside_processing_json': row[18],
            'quality_requirements_json': row[19],
            'part_marking_json': row[20],
            
            # Part data
            'part_id': row[21],
            'genesis_hash': row[22],
            'filename': row[23],
            'fingerprint': json.loads(row[24]) if row[24] else [],
            'volume': row[25],
            'surface_area': row[26],
            'dimensions': json.loads(row[27]) if row[27] else {},
            'process_routing': json.loads(row[28]) if row[28] else [],
            
            # Customer data
            'customer_id': row[29],
            'customer_name': row[30],
            'customer_domain': row[31],
            
            # Contact data
            'contact_id': row[32],
            'contact_name': row[33],
            'contact_email': row[34],
            'contact_phone': row[35],
            
            # Legacy fields for backwards compatibility
            'final_price': row[4],
            'anchor_price': row[3],
        }
        
        # Generate PDF (customer-safe by default)
        pdf_path = pdf_generator.generate_quote_pdf(
            quote_data=quote_data,
            output_dir="quotes_pdf",
            customer_facing=customer_facing
        )
        
        # Serve PDF file
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"{quote_data['quote_id']}.pdf"
        )
        
    except Exception as e:
        print(f"[ERROR] PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/quote/<int:quote_id>/traveler', methods=['GET'])
def generate_traveler_pdf_endpoint(quote_id: int) -> Any:
    """
    GET /api/quote/<quote_id>/traveler
    
    Generate and serve a Traveler PDF (Shop Floor Work Order).
    Local-First: Uses ReportLab (no cloud services).
    
    CRITICAL: NO PRICING INFORMATION (shop floor security).
    
    Returns:
        PDF file download
    """
    try:
        # Fetch quote from database (same query as quote PDF)
        conn = database.get_connection()
        cursor = conn.cursor()
        
        # Query quote with all related data (4-Table Identity Model)
        cursor.execute("""
            SELECT 
                q.id, q.quote_id, q.material, q.system_price_anchor, q.final_quoted_price,
                q.variance_json, q.pricing_tags_json, q.status, q.created_at, q.user_id,
                q.quantity, q.target_date, q.notes,
                q.lead_time_date, q.lead_time_days, q.target_price_per_unit,
                q.price_breaks_json, q.outside_processing_json, q.quality_requirements_json,
                q.part_marking_json,
                p.id as part_id, p.genesis_hash, p.filename, p.fingerprint_json, 
                p.volume, p.surface_area, p.dimensions_json, p.process_routing_json,
                cu.id as customer_id, cu.name as customer_name, cu.domain as customer_domain,
                co.id as contact_id, co.name as contact_name, co.email as contact_email, co.phone as contact_phone
            FROM ops__quotes q
            JOIN ops__parts p ON q.part_id = p.id
            LEFT JOIN ops__customers cu ON q.customer_id = cu.id
            LEFT JOIN ops__contacts co ON q.contact_id = co.id
            WHERE q.id = ?
        """, (quote_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Quote not found'}), 404
        
        # Build quote_data dictionary (same as quote PDF)
        quote_data = {
            # Quote data
            'id': row[0],
            'quote_id': row[1],
            'material': row[2],
            'system_price_anchor': row[3],
            'final_quoted_price': row[4],
            'variance_json': json.loads(row[5]) if row[5] else None,
            'pricing_tags_json': json.loads(row[6]) if row[6] else {},
            'status': row[7],
            'timestamp': row[8],
            'user_id': row[9],
            'quantity': row[10],
            'target_date': row[11],
            'notes': row[12],
            
            # RFQ fields
            'lead_time_date': row[13],
            'lead_time_days': row[14],
            'target_price_per_unit': row[15],
            'price_breaks_json': row[16],
            'outside_processing_json': row[17],
            'quality_requirements_json': row[18],
            'part_marking_json': row[19],
            
            # Part data
            'part_id': row[20],
            'genesis_hash': row[21],
            'filename': row[22],
            'fingerprint': json.loads(row[23]) if row[23] else [],
            'volume': row[24],
            'surface_area': row[25],
            'dimensions': json.loads(row[26]) if row[26] else {},
            'process_routing': json.loads(row[27]) if row[27] else [],
            
            # Customer data (NOT included in traveler PDF)
            'customer_id': row[28],
            'customer_name': row[29],
            'customer_domain': row[30],
            
            # Contact data (NOT included in traveler PDF)
            'contact_id': row[31],
            'contact_name': row[32],
            'contact_email': row[33],
            'contact_phone': row[34],
            
            # Legacy fields for backwards compatibility
            'final_price': row[4],
            'anchor_price': row[3],
        }
        
        # Generate Traveler PDF (NO PRICING)
        pdf_path = pdf_generator.generate_traveler_pdf(
            quote_data=quote_data,
            output_dir="travelers_pdf"
        )
        
        # Serve PDF file
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"TRAVELER-{quote_data['quote_id']}.pdf"
        )
        
    except Exception as e:
        print(f"[ERROR] Traveler PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/quote/<int:quote_id>/mark_won', methods=['POST'])
def mark_quote_won_endpoint(quote_id: int) -> Dict[str, Any]:
    """
    POST /api/quote/<quote_id>/mark_won
    
    Mark a quote as "Won" (changes status to 'Won').
    Used before generating Traveler PDFs (work orders for shop floor).
    
    Args:
        quote_id: The quote record ID
    
    Returns:
        JSON with success status
    """
    try:
        success = database.update_quote_status_simple(quote_id, 'Won')
        
        if success:
            # --- CUTTER LEDGER: Emit QUOTE_STATUS_CHANGED event ---
            try:
                emit_cutter_event(
                    event_type='QUOTE_STATUS_CHANGED',
                    subject_ref=quote_id,
                    event_data={'new_status': 'Won'}
                )
                print(f"[LEDGER] QUOTE_STATUS_CHANGED event emitted: quote {quote_id} -> Won")
            except Exception as event_error:
                print(f"[LEDGER] Event emission failed: {event_error}")
            
            return jsonify({
                'success': True,
                'message': f'Quote {quote_id} marked as Won',
                'status': 'Won'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Quote not found'
            }), 404
            
    except Exception as e:
        print(f"[ERROR] Mark quote as won failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/unclosed_quotes', methods=['GET'])
def get_unclosed_quotes_endpoint():
    """
    GET /api/unclosed_quotes
    
    Per minimum viable truth spec: Returns quotes WITHOUT outcome events.
    Unclosed = no saved outcome in append-only truth ledger.
    
    Returns:
        JSON array of unclosed quotes
    """
    try:
        unclosed = database.get_unclosed_quotes()
        return jsonify({
            'success': True,
            'count': len(unclosed),
            'quotes': unclosed
        }), 200
    except Exception as e:
        print(f"[ERROR] Failed to fetch unclosed quotes: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/quote/<int:quote_id>/outcome', methods=['POST'])
def save_quote_outcome_endpoint(quote_id: int):
    """
    POST /api/quote/<quote_id>/outcome
    
    Minimum viable truth: 2-step outcome capture with training signal depth.
    
    Request Body:
        {
            "outcome_type": "WON" | "LOST" | "NO_DECISION",
            "actor_user_id": 1 (optional, from localStorage),
            "change_needed": true/false (optional detail),
            "price_value": 150.00 (optional detail),
            "note": "text" (optional, always last)
        }
    
    Returns:
        JSON with success status
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        outcome_type = data.get('outcome_type')
        if not outcome_type or outcome_type not in ['WON', 'LOST', 'NO_DECISION']:
            return jsonify({
                'success': False,
                'error': 'outcome_type must be WON, LOST, or NO_DECISION'
            }), 400
        
        actor_user_id = data.get('actor_user_id')
        change_needed = data.get('change_needed')
        price_value = data.get('price_value')
        note = data.get('note')
        
        # Parse price if it's a string with $ sign
        if price_value and isinstance(price_value, str):
            price_value = price_value.replace('$', '').replace(',', '').strip()
            try:
                price_value = float(price_value)
            except:
                price_value = None
        
        success = database.save_quote_outcome(
            quote_id=quote_id,
            outcome_type=outcome_type,
            actor_user_id=actor_user_id,
            change_needed=change_needed,
            price_value=price_value,
            note=note
        )
        
        if success:
            # Emit exhaust
            try:
                event_data = {
                    'outcome_type': outcome_type
                }
                if change_needed is not None:
                    event_data['change_needed'] = change_needed
                if price_value is not None:
                    event_data['price_value'] = price_value
                
                emit_cutter_event(
                    event_type='QUOTE_OUTCOME_CAPTURED',
                    subject_ref=f'quote:{quote_id}',
                    event_data=event_data
                )
            except Exception as event_error:
                print(f"[LEDGER] Event emission failed: {event_error}")
            
            return jsonify({
                'success': True,
                'message': f'Outcome {outcome_type} saved for quote {quote_id}'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save outcome'
            }), 500
        
    except Exception as e:
        print(f"[ERROR] Failed to save outcome: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/quote/<int:quote_id>/outcome/wizard', methods=['POST'])
def save_wizard_outcome_endpoint(quote_id: int):
    """
    POST /api/quote/<quote_id>/outcome/wizard
    
    Wizard flow: Progressive auto-save with original vs final value tracking.
    
    Request Body:
        {
            "outcome_type": "WON" | "LOST" | "NO_RESPONSE",
            "wizard_step": 0-4,
            "actor_user_id": 1 (optional, from localStorage),
            "original_price": 150.00,
            "final_price": 140.00,
            "original_leadtime": 14,
            "final_leadtime": 10,
            "original_terms": 30,
            "final_terms": 30,
            "other_notes": "text" (optional),
            "event_id": 123 (optional, for progressive updates)
        }
    
    Returns:
        JSON with success status and event_id
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        outcome_type = data.get('outcome_type')
        if not outcome_type or outcome_type not in ['WON', 'LOST', 'NO_RESPONSE']:
            return jsonify({
                'success': False,
                'error': 'outcome_type must be WON, LOST, or NO_RESPONSE'
            }), 400
        
        # Call wizard save function
        event_id = database.save_quote_outcome_wizard(
            quote_id=quote_id,
            outcome_type=outcome_type,
            actor_user_id=data.get('actor_user_id'),
            original_price=data.get('original_price'),
            final_price=data.get('final_price'),
            original_leadtime=data.get('original_leadtime'),
            final_leadtime=data.get('final_leadtime'),
            original_terms=data.get('original_terms'),
            final_terms=data.get('final_terms'),
            other_notes=data.get('other_notes'),
            wizard_step=data.get('wizard_step', 0)
        )
        
        if event_id > 0:
            # Emit exhaust
            try:
                event_data = {
                    'outcome_type': outcome_type,
                    'wizard_step': data.get('wizard_step', 0),
                    'original_price': data.get('original_price'),
                    'final_price': data.get('final_price'),
                    'original_leadtime': data.get('original_leadtime'),
                    'final_leadtime': data.get('final_leadtime'),
                    'original_terms_present': bool(data.get('original_terms')),
                    'final_terms_present': bool(data.get('final_terms'))
                }
                
                # Add price_delta only if both prices are numeric
                orig_price = data.get('original_price')
                final_price = data.get('final_price')
                if orig_price is not None and final_price is not None:
                    try:
                        event_data['price_delta'] = float(final_price) - float(orig_price)
                    except (ValueError, TypeError):
                        pass
                
                emit_cutter_event(
                    event_type='QUOTE_OUTCOME_WIZARD_SAVED',
                    subject_ref=f'quote:{quote_id}',
                    event_data=event_data
                )
            except Exception as event_error:
                print(f"[LEDGER] Event emission failed: {event_error}")
            
            return jsonify({
                'success': True,
                'event_id': event_id,
                'message': f'Wizard step {data.get("wizard_step")} saved for quote {quote_id}'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save wizard outcome'
            }), 500
        
    except Exception as e:
        print(f"[ERROR] save_wizard_outcome_endpoint: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/quote/<int:quote_id>/update_status', methods=['POST'])
def update_quote_status_endpoint(quote_id: int) -> Dict[str, Any]:
    """
    POST /api/quote/<quote_id>/update_status
    
    The "Deal Closer" - Comprehensive status update with Win/Loss data capture.
    Primary method for changing quote status with optional reason/notes.
    
    Request Body (JSON):
        {
            "status": "Won" | "Lost" | "Draft" | "Sent",
            "win_notes": "Final agreed price: $X" (optional, for Won),
            "loss_reason": "Price" | ["Price", "Lead Time"] (optional, for Lost),
            "final_agreed_price": 150.00 (optional, for Won - updates final_quoted_price),
            "win_attribution": {...} (optional, structured win data),
            "loss_attribution": {...} (optional, structured loss data)
        }
    
    Returns:
        JSON with success status and updated quote data
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        new_status = data.get('status')
        if not new_status:
            return jsonify({'success': False, 'error': 'status is required'}), 400
        
        # Validate status
        valid_statuses = ['Draft', 'Sent', 'Won', 'Lost']
        if new_status not in valid_statuses:
            return jsonify({
                'success': False,
                'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }), 400
        
        # Extract optional fields
        win_notes = data.get('win_notes', None)
        loss_reason = data.get('loss_reason', None)
        final_agreed_price = data.get('final_agreed_price', None)
        win_attribution = data.get('win_attribution', None)
        loss_attribution = data.get('loss_attribution', None)
        
        # Serialize loss_reason if it's a list
        if loss_reason and isinstance(loss_reason, list):
            loss_reason = json.dumps(loss_reason)
        
        # Update status with win/loss data
        success = database.update_quote_status_simple(
            quote_id=quote_id,
            status=new_status,
            win_notes=win_notes,
            loss_reason=loss_reason,
            win_attribution=win_attribution,
            loss_attribution=loss_attribution
        )
        
        if not success:
            return jsonify({'success': False, 'error': 'Quote not found'}), 404
        
        # --- CUTTER LEDGER: Emit QUOTE_STATUS_CHANGED event ---
        # Record status transition in append-only ledger
        try:
            event_data = {
                'new_status': new_status,
            }
            if win_notes:
                event_data['win_notes'] = win_notes
            if loss_reason:
                event_data['loss_reason'] = loss_reason if isinstance(loss_reason, str) else json.loads(loss_reason)
            if final_agreed_price:
                event_data['final_agreed_price'] = float(final_agreed_price)
            
            emit_cutter_event(
                event_type='QUOTE_STATUS_CHANGED',
                subject_ref=quote_id,
                event_data=event_data
            )
            print(f"[LEDGER] QUOTE_STATUS_CHANGED event emitted: quote {quote_id} -> {new_status}")
        except Exception as event_error:
            print(f"[LEDGER] Event emission failed: {event_error}")
        
        # If Won and final_agreed_price provided, update the price
        if new_status == 'Won' and final_agreed_price is not None:
            conn = database.get_connection()
            cursor = conn.cursor()
            
            # Read old price before update
            cursor.execute("SELECT final_quoted_price FROM ops__quotes WHERE id = ?", (quote_id,))
            old_row = cursor.fetchone()
            old_final_quoted_price = old_row[0] if old_row else None
            
            cursor.execute(
                "UPDATE ops__quotes SET final_quoted_price = ? WHERE id = ?",
                (float(final_agreed_price), quote_id)
            )
            conn.commit()
            conn.close()
            print(f"[UPDATE] Quote {quote_id} final price updated to: ${final_agreed_price}")
            
            # Emit exhaust
            try:
                event_data = {
                    'final_quoted_price': float(final_agreed_price)
                }
                if old_final_quoted_price is not None:
                    event_data['old_final_quoted_price'] = old_final_quoted_price
                
                emit_cutter_event(
                    event_type='QUOTE_PRICE_FINALIZED',
                    subject_ref=f'quote:{quote_id}',
                    event_data=event_data
                )
            except Exception as event_error:
                print(f"[LEDGER] Event emission failed: {event_error}")
        
        # Fetch updated quote data to return
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT status, closed_at, win_notes, loss_reason, final_quoted_price
            FROM ops__quotes WHERE id = ?
        """, (quote_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return jsonify({
                'success': True,
                'message': f'Quote {quote_id} status updated to {new_status}',
                'quote': {
                    'id': quote_id,
                    'status': row[0],
                    'closed_at': row[1],
                    'win_notes': row[2],
                    'loss_reason': row[3],
                    'final_quoted_price': row[4]
                }
            }), 200
        else:
            return jsonify({'success': False, 'error': 'Quote not found after update'}), 500
        
    except Exception as e:
        print(f"[ERROR] Update quote status failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/convert_units', methods=['POST'])
def convert_units_endpoint() -> Dict[str, Any]:
    """
    POST /api/convert_units
    
    Convert volume and dimensions between mm and in for unit correction in File Mode.
    
    Phase 5.6 - Unit Verification Feature (Enhanced with dimension conversion)
    
    When user uploads STL, system guesses units (mm or in). If guess is wrong,
    user can select correct units and this endpoint recalculates volume and dimensions.
    
    Request Body:
        {
            "original_volume": 2899.125,           # Volume in original units
            "dimensions": {                         # OPTIONAL: Bounding box dimensions
                "x": 96.3,
                "y": 15.0,
                "z": 15.0
            },
            "from_unit": "in",                     # "mm" or "in"
            "to_unit": "mm"                        # "mm" or "in"
        }
    
    Returns:
        {
            "success": true,
            "converted_volume": 47502246.8,        # Volume in new units
            "converted_dimensions": {               # Dimensions in new units (if provided)
                "x": 2446.02,
                "y": 381.0,
                "z": 381.0
            },
            "from_unit": "in",
            "to_unit": "mm",
            "requires_repricing": true             # Signal to frontend to recalculate
        }
    
    Example:
        curl -X POST http://localhost:5000/api/convert_units \
             -H "Content-Type: application/json" \
             -d '{"original_volume": 2899.125, "dimensions": {"x": 96.3, "y": 15, "z": 15}, "from_unit": "in", "to_unit": "mm"}'
    """
    from vector_engine import convert_units, convert_dimensions
    
    try:
        # Get request data
        data = request.json
        
        # Validate required fields
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        required_fields = ['original_volume', 'from_unit', 'to_unit']
        missing_fields = [f for f in required_fields if f not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Extract parameters
        original_volume = data['original_volume']
        dimensions = data.get('dimensions')  # Optional
        from_unit = data['from_unit']
        to_unit = data['to_unit']
        
        # Validate volume is a number
        try:
            original_volume = float(original_volume)
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'original_volume must be a number'
            }), 400
        
        # Validate units
        valid_units = ['mm', 'in']
        if from_unit not in valid_units or to_unit not in valid_units:
            return jsonify({
                'success': False,
                'error': f'Units must be one of: {", ".join(valid_units)}'
            }), 400
        
        # Convert volume
        new_volume = convert_units(original_volume, from_unit, to_unit)
        
        # Prepare response
        response = {
            'success': True,
            'converted_volume': round(new_volume, 3),  # 3 decimal places for display
            'from_unit': from_unit,
            'to_unit': to_unit,
            'requires_repricing': True  # Signal frontend to trigger full recalculation
        }
        
        # Convert dimensions if provided
        if dimensions and isinstance(dimensions, dict):
            try:
                # Validate dimensions has x, y, z
                if 'x' in dimensions and 'y' in dimensions and 'z' in dimensions:
                    dim_tuple = (
                        float(dimensions['x']),
                        float(dimensions['y']),
                        float(dimensions['z'])
                    )
                    
                    # Convert dimensions
                    new_dims = convert_dimensions(dim_tuple, from_unit, to_unit)
                    
                    response['converted_dimensions'] = {
                        'x': round(new_dims[0], 2),
                        'y': round(new_dims[1], 2),
                        'z': round(new_dims[2], 2)
                    }
                    
                    print(f"[UNIT CONVERSION] Volume: {original_volume:.3f} {from_unit}³ → {new_volume:.3f} {to_unit}³")
                    print(f"[UNIT CONVERSION] Dimensions: ({dim_tuple[0]:.2f}, {dim_tuple[1]:.2f}, {dim_tuple[2]:.2f}) {from_unit} → ({new_dims[0]:.2f}, {new_dims[1]:.2f}, {new_dims[2]:.2f}) {to_unit}")
                else:
                    print(f"[WARN] Dimensions provided but missing x, y, or z")
            except (ValueError, TypeError) as e:
                print(f"[WARN] Could not convert dimensions: {e}")
                # Don't fail the whole request if dimensions fail
        else:
            print(f"[UNIT CONVERSION] Volume only: {original_volume:.3f} {from_unit}³ → {new_volume:.3f} {to_unit}³")
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"[ERROR] Unit conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Unit conversion error: {str(e)}'
        }), 500


@app.route('/api/system/health', methods=['GET'])
def system_health_endpoint() -> Dict[str, Any]:
    """
    GET /api/system/health
    
    System health and telemetry endpoint for monitoring resource usage.
    Designed for Raspberry Pi 5 deployment verification.
    
    Returns:
        JSON with CPU, memory, disk, and database metrics
    """
    try:
        mode = get_ops_mode() or "planning"
        # Get current process (Python/Flask app)
        process = psutil.Process(os.getpid())
        
        # CPU usage (system-wide snapshot)
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Memory usage (Python process RSS - Resident Set Size)
        memory_info = process.memory_info()
        memory_usage_mb = memory_info.rss / (1024 * 1024)  # Convert bytes to MB
        
        # Disk usage (where the app is running)
        disk_usage = psutil.disk_usage(BASE_DIR)
        disk_free_gb = disk_usage.free / (1024 * 1024 * 1024)  # Convert bytes to GB
        
        # Database file size
        db_path = Path("cutter.db")
        db_size_mb = 0.0
        if db_path.exists():
            db_size_mb = db_path.stat().st_size / (1024 * 1024)  # Convert bytes to MB
        
        # Build response
        health_data = {
            'status': 'healthy',
            'ping': 'pong',
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'cpu_percent': round(cpu_percent, 2),
                'memory_usage_mb': round(memory_usage_mb, 2),
                'disk_free_gb': round(disk_free_gb, 2),
                'db_size_mb': round(db_size_mb, 2)
            },
            'system_info': {
                'python_pid': os.getpid(),
                'platform': os.name,
                'cpu_count': psutil.cpu_count()
            }
        }
        
        health_data = apply_execution_guard(health_data, mode=mode)
        return jsonify(health_data), 200
        
    except Exception as e:
        print(f"[ERROR] Health check failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'ping': 'pong',
            'error': str(e)
        }), 500


# --- IDENTITY INTEGRATION (PHASE 4 - CUSTOMER & CONTACT MANAGEMENT) ---
# PHASE 1 REMEDIATION: "Guild Intelligence" label removed - this is Ops functionality

@app.route('/api/customers/search', methods=['GET'])
def search_customers() -> Dict[str, Any]:
    """
    GET /api/customers/search?q=...
    Search customers by name or domain.
    """
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify({'results': []}), 200
    
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        
        # Search by name OR domain
        search_pattern = f'%{query}%'
        cursor.execute("""
            SELECT id, name, domain 
            FROM ops__customers 
            WHERE name LIKE ? OR domain LIKE ?
            ORDER BY name
            LIMIT 10
        """, (search_pattern, search_pattern))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = [{'id': row[0], 'name': row[1], 'domain': row[2]} for row in rows]
        return jsonify({'results': results}), 200
        
    except Exception as e:
        print(f"[ERROR] Customer search failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/contacts/search', methods=['GET'])
def search_contacts() -> Dict[str, Any]:
    """
    GET /api/contacts/search?q=...&customer_id=...
    Search contacts by name or email.
    Optionally filter by customer_id.
    """
    query = request.args.get('q', '').strip()
    customer_id = request.args.get('customer_id', None)
    
    if not query or len(query) < 2:
        return jsonify({'results': []}), 200
    
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        
        search_pattern = f'%{query}%'
        
        if customer_id:
            # Filter by current_customer_id
            cursor.execute("""
                SELECT id, name, email 
                FROM ops__contacts 
                WHERE (name LIKE ? OR email LIKE ?) 
                  AND current_customer_id = ?
                ORDER BY name
                LIMIT 10
            """, (search_pattern, search_pattern, int(customer_id)))
        else:
            # Search all contacts
            cursor.execute("""
                SELECT id, name, email 
                FROM ops__contacts 
                WHERE name LIKE ? OR email LIKE ?
                ORDER BY name
                LIMIT 10
            """, (search_pattern, search_pattern))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = [{'id': row[0], 'name': row[1], 'email': row[2]} for row in rows]
        return jsonify({'results': results}), 200
        
    except Exception as e:
        print(f"[ERROR] Contact search failed: {e}")
        return jsonify({'error': str(e)}), 500


# --- LOOP 1: CARRIER HANDOFF (OPS EXHAUST) ---

@app.route('/ops/carrier_handoff', methods=['POST'])
def create_carrier_handoff() -> Dict[str, Any]:
    """POST /ops/carrier_handoff endpoint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        subject_ref = data.get('subject_ref')
        if not subject_ref:
            return jsonify({'error': 'subject_ref is required'}), 400

        carrier = data.get('carrier')
        event_data = data.get('event_data')
        if event_data is not None and not isinstance(event_data, dict):
            return jsonify({'error': 'event_data must be an object'}), 400

        event_id = emit_carrier_handoff(
            subject_ref=subject_ref,
            carrier=carrier,
            event_data=event_data
        )

        return jsonify({'success': True, 'event_id': event_id}), 200
    except ValueError as e:
        return jsonify({'error': f'Invalid parameter: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- LOOP 1: QUERY A (READ-ONLY) ---

@app.route('/api/state/open-deadlines', methods=['GET'])
def get_open_deadlines() -> Dict[str, Any]:
    """GET /api/state/open-deadlines endpoint."""
    try:
        entity_ref = request.args.get('entity_ref')
        db_path = database.resolve_db_path()
        results = get_query_a_open_deadlines(db_path=db_path, entity_ref=entity_ref)
        return jsonify({'results': results}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- LOOP 1: QUERY B (READ-ONLY) ---

@app.route('/api/cutter/dwell-vs-expectation', methods=['GET'])
def get_dwell_vs_expectation() -> Dict[str, Any]:
    """GET /api/cutter/dwell-vs-expectation endpoint."""
    try:
        subject_ref = request.args.get('subject_ref')
        db_path = database.resolve_db_path()
        results = query_dwell_vs_expectation(db_path=db_path, subject_ref=subject_ref)
        return jsonify({'results': results}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- LOOP 2: QUERY A2 (READ-ONLY) ---

@app.route('/api/state/open-response-deadlines', methods=['GET'])
def get_open_response_deadlines() -> Dict[str, Any]:
    """GET /api/state/open-response-deadlines endpoint."""
    try:
        entity_ref = request.args.get('entity_ref')
        db_path = database.resolve_db_path()
        results = query_open_response_deadlines(db_path=db_path, entity_ref=entity_ref)
        return jsonify({'results': results}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- TAG MANAGEMENT (RESTORED SAFETY GUARDRAILS) ---

@app.route('/tags', methods=['GET'])
@app.route('/api/tags', methods=['GET'])
def get_tags() -> Dict[str, Any]:
    """GET /tags and /api/tags endpoint."""
    tags = database.get_all_tags()
    return jsonify({'success': True, 'tags': tags}), 200


@app.route('/tags/new', methods=['POST'])
def create_tag() -> Dict[str, Any]:
    """POST /tags/new endpoint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        name = data.get('name', '').strip()
        category = data.get('category', 'General')
        impact_type = data.get('impact_type', 'none')
        impact_value = float(data.get('impact_value', 0))
        
        if not name:
            return jsonify({'error': 'Tag name is required'}), 400
        
        # Create tag
        tag_id = database.create_custom_tag(name, impact_type, impact_value, category=category)
        
        # Emit exhaust
        emit_cutter_event(
            event_type='CUSTOM_TAG_CREATED',
            subject_ref=f'tag:{tag_id}',
            event_data={
                'name': name,
                'impact_type': impact_type,
                'impact_value': impact_value,
                'category': category
            }
        )
        
        return jsonify({
            'success': True,
            'tag_id': tag_id,
            'message': 'Tag created successfully'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': f'Invalid parameter: {str(e)}'}), 400
    except Exception as e:
        error_msg = str(e)
        if 'UNIQUE constraint' in error_msg:
            return jsonify({'error': 'Tag name already exists'}), 400
        return jsonify({'error': f'Unexpected error: {error_msg}'}), 500


@app.route('/tags/<int:tag_id>', methods=['PUT'])
def update_tag(tag_id: int) -> Dict[str, Any]:
    """PUT /tags/<tag_id> endpoint."""
    try:
        data = request.get_json()
        
        # Protection Logic
        tags = database.get_all_tags()
        tag_to_update = next((t for t in tags if t['id'] == tag_id), None)
        
        if not tag_to_update:
            return jsonify({'error': 'Tag not found'}), 404
        
        # Universal 9 Protection
        protected_tags = [
            'Rush Job', 'Expedite', 'Risk: Scrap High', 'Friends / Family',
            'Tight Tol', 'Complex Fixture', 'Heavy Deburr', 'Proto', 'Cust. Material'
        ]
        
        if tag_to_update['name'] in protected_tags:
            return jsonify({'error': 'Cannot modify system tag (Universal 9)'}), 403
        
        # Extract update data
        name = data.get('name', '').strip()
        category = data.get('category', 'General')
        impact_type = data.get('impact_type', 'none')
        impact_value = float(data.get('impact_value', 0))
        
        # Emit exhaust
        emit_cutter_event(
            event_type='CUSTOM_TAG_UPDATED',
            subject_ref=f'tag:{tag_id}',
            event_data={
                'name': name,
                'old_impact_type': tag_to_update['impact_type'],
                'new_impact_type': impact_type,
                'old_impact_value': tag_to_update['impact_value'],
                'new_impact_value': impact_value,
                'old_category': tag_to_update['category'],
                'new_category': category
            }
        )
        
        database.update_custom_tag(tag_id, name, impact_type, impact_value, category)
        
        return jsonify({'success': True, 'message': 'Tag updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to update tag: {str(e)}'}), 500


@app.route('/tags/<int:tag_id>', methods=['DELETE'])
def delete_tag(tag_id: int) -> Dict[str, Any]:
    """DELETE /tags/<tag_id> endpoint."""
    try:
        # Protection Logic
        tags = database.get_all_tags()
        tag_to_delete = next((t for t in tags if t['id'] == tag_id), None)
        
        if not tag_to_delete:
            return jsonify({'error': 'Tag not found'}), 404
        
        # Universal 9 Protection
        protected_tags = [
            'Rush Job', 'Expedite', 'Risk: Scrap High', 'Friends / Family',
            'Tight Tol', 'Complex Fixture', 'Heavy Deburr', 'Proto', 'Cust. Material'
        ]
        
        if tag_to_delete['name'] in protected_tags:
            return jsonify({'error': 'Cannot delete system tag (Universal 9)'}), 403
        
        # Count quotes potentially using this tag
        approximate_affected_quotes = database.count_quotes_using_tag_name_approx(tag_to_delete['name'])
        
        # Emit exhaust before deletion
        emit_cutter_event(
            event_type='CUSTOM_TAG_DELETED',
            subject_ref=f'tag:{tag_id}',
            event_data={
                'name': tag_to_delete['name'],
                'impact_type': tag_to_delete['impact_type'],
                'impact_value': tag_to_delete['impact_value'],
                'approximate_affected_quotes_count': approximate_affected_quotes
            }
        )
        
        database.delete_custom_tag(tag_id)
        return jsonify({'success': True, 'message': 'Tag deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to delete tag: {str(e)}'}), 500


@app.route('/update_status', methods=['POST'])
def update_status() -> Dict[str, Any]:
    """POST /update_status endpoint - Update quote outcome status.
    PHASE 1 REMEDIATION: 'Partner Mode (Data Dividend)' label removed for clarity."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        quote_id = data.get('quote_id')
        if not quote_id:
            return jsonify({'error': 'quote_id is required'}), 400
        
        status = data.get('status', 'Draft')
        if status not in ('Draft', 'Won', 'Lost', 'Archived'):
            return jsonify({'error': 'Invalid status. Must be Draft, Won, Lost, or Archived'}), 400
        
        actual_runtime = data.get('actual_runtime')
        if actual_runtime is not None:
            try:
                actual_runtime = float(actual_runtime)
            except (ValueError, TypeError):
                return jsonify({'error': 'actual_runtime must be a number'}), 400
        
        submit_to_guild = data.get('submit_to_guild', False)
        if not isinstance(submit_to_guild, bool):
            submit_to_guild = str(submit_to_guild).lower() in ('true', '1', 'yes')
        
        loss_reason = data.get('loss_reason')
        if loss_reason is not None:
            # Handle both single string and list/array
            if isinstance(loss_reason, list):
                # Already a list, pass it through (will be serialized in database)
                pass
            elif isinstance(loss_reason, str):
                # Try to parse as JSON array, otherwise treat as single string
                try:
                    parsed = json.loads(loss_reason)
                    if isinstance(parsed, list):
                        loss_reason = parsed
                    else:
                        loss_reason = [loss_reason]  # Single string -> list
                except (json.JSONDecodeError, TypeError):
                    # Not JSON, treat as single string
                    loss_reason = loss_reason.strip()
                    if not loss_reason:
                        loss_reason = None
                    else:
                        loss_reason = [loss_reason]  # Convert to list
            else:
                # Other type, convert to list
                loss_reason = [str(loss_reason)]
        
        # Update quote status (PHASE 1: credit calculation removed)
        database.update_quote_status(
            quote_id=int(quote_id),
            status=status,
            actual_runtime=actual_runtime,
            is_guild_submission=submit_to_guild,
            loss_reason=loss_reason
        )
        
        # PHASE 1 REMEDIATION: Credit values removed from response
        # Guild economics belong in Guild product, not Ops API
        return jsonify({
            'success': True
        }), 200
        
    except ValueError as e:
        return jsonify({'error': f'Invalid parameter: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to update status: {str(e)}'}), 500


# /ledger endpoint removed - PHASE 1 REMEDIATION
# Guild credit display in Ops violates firewall (Guild economics belong in Guild product)


@app.route('/export_guild_packet', methods=['POST'])
def export_guild_packet() -> Dict[str, Any]:
    """POST /export_guild_packet endpoint - Export closed-loop data for external analysis.
    
    PHASE 2 REMEDIATION: Endpoint preserved but semantics clarified.
    - Export is explicit and manual (not automatic)
    - No Guild economics/credits displayed
    - Neutral terminology in responses
    - Guild contribution evaluation happens in Guild product, not here
    """
    try:
        payload = request.get_json(silent=True) or {}
        actor_ref = payload.get('actor_ref')
        if not actor_ref:
            return jsonify({'error': 'actor_ref is required'}), 400
        valid_actor, actor_error = state_validation.validate_actor_ref(actor_ref)
        if not valid_actor:
            return jsonify({'error': f'actor_ref invalid: {actor_error}'}), 400

        # Get pending exports
        pending_records = database.get_pending_exports()
        
        if not pending_records:
            return jsonify({
                'success': False,
                'error': 'No data available for export'
            }), 400
        
        # Create sanitized export data
        export_id = str(uuid.uuid4())
        export_data = {
            'export_id': export_id,
            'export_date': datetime.now().isoformat(),
            'initiated_by_actor_ref': actor_ref,
            'source_system': 'ops_layer',
            'record_count': len(pending_records),
            'records': pending_records
        }
        
        # PHASE 2: Neutral filename (no "guild_packet" terminology)
        date_str = datetime.now().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())[:8]
        filename = f'closed_loop_export_{date_str}_{unique_id}.json'
        export_dir = app.config['UPLOAD_FOLDER']
        if os.environ.get('TEST_DB_PATH'):
            export_dir = tempfile.gettempdir()
        filepath = os.path.join(export_dir, filename)
        
        # Write JSON file (human-readable with indent=2)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        # Mark records as exported
        quote_ids = [record['record']['id'] for record in pending_records]
        database.mark_as_exported(quote_ids)
        
        # Return file as download
        return send_file(
            filepath,
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': f'Failed to export data: {str(e)}'}), 500


@app.route('/pending_exports', methods=['GET'])
def pending_exports() -> Dict[str, Any]:
    """GET /pending_exports endpoint - Returns count of quotes ready for export.
    
    PHASE 2: Neutral bookkeeping endpoint (no Guild economics displayed).
    """
    try:
        count = database.get_pending_export_count()
        
        return jsonify({
            'success': True,
            'pending_count': count
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get pending exports: {str(e)}'}), 500


@app.route('/history', methods=['GET'])
def history() -> Dict[str, Any]: return jsonify({'history': database.get_all_history()})

@app.route('/delete_quote/<int:quote_id>', methods=['POST'])
def delete_quote_endpoint(quote_id: int) -> Dict[str, Any]:
    """
    POST /delete_quote/<id> endpoint - Soft Delete (The Trash Can).
    Sets is_deleted = 1, hiding the quote from:
    - UI history table
    - Vector search (KNN learning)
    - Guild exports
    
    Data is preserved for forensic recovery.
    """
    try:
        success = database.soft_delete_quote(quote_id)
        
        if success:
            # --- CUTTER LEDGER: Emit QUOTE_DELETED event ---
            # Record soft deletion in append-only ledger
            try:
                emit_cutter_event(
                    event_type='QUOTE_DELETED',
                    subject_ref=quote_id,
                    event_data={'deleted_at': datetime.now().isoformat()}
                )
                print(f"[LEDGER] QUOTE_DELETED event emitted for quote {quote_id}")
            except Exception as event_error:
                print(f"[LEDGER] Event emission failed: {event_error}")
            
            return jsonify({
                'success': True,
                'message': f'Quote {quote_id} archived successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Quote not found or already deleted'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to delete quote: {str(e)}'
        }), 500

@app.route('/materials', methods=['GET'])
def get_materials() -> Dict[str, Any]:
    """GET /materials endpoint - Returns all valid materials."""
    try:
        materials = database.get_all_materials()
        return jsonify({'materials': materials}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get materials: {str(e)}'}), 500

@app.route('/check_quote_id/<quote_id>', methods=['GET'])
def check_quote_id(quote_id: str) -> Dict[str, Any]:
    """
    GET /check_quote_id/<quote_id> endpoint - Check if a Quote ID already exists.
    
    This prevents accidental overwrites when the user edits the Quote ID field.
    Returns {"exists": true} if found, {"exists": false} if available.
    """
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        
        # Check if quote_id exists in quote_history (excluding soft-deleted)
        cursor.execute("""
            SELECT COUNT(*) FROM ops__quote_history 
            WHERE quote_id = ? AND is_deleted = 0
        """, (quote_id,))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        exists = count > 0
        
        return jsonify({'exists': exists, 'quote_id': quote_id}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to check quote ID: {str(e)}'}), 500

@app.route('/fix_compliance', methods=['POST'])
def fix_compliance() -> Dict[str, Any]:
    """POST /fix_compliance endpoint - Janitor Protocol."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        quote_id = data.get('quote_id')
        material = data.get('material')
        
        if not quote_id or not material:
            return jsonify({'error': 'quote_id and material are required'}), 400
        
        success, message = database.fix_quote_compliance(quote_id, material)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health() -> Dict[str, Any]: return jsonify({'status': 'ok'})

@app.route('/files/<filename>')
@app.route('/uploads/<filename>')
def serve_file(filename: str) -> Dict[str, Any]:
    """
    Streaming endpoint for 3D models (OPTIMIZATION PASS 1).
    Converts STEP files to STL on-the-fly for Three.js viewer compatibility.
    Serves from both /files/ and /uploads/ for backward compatibility.
    """
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Check if file is STEP format (needs conversion)
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext in ['.step', '.stp']:
            # Convert STEP to STL for Three.js viewer
            print(f"[CONVERT] Converting STEP to STL for viewer: {filename}")
            
            try:
                # Load STEP file
                mesh = load_mesh_file(file_path)
                
                # Export to STL binary format (more efficient than ASCII)
                import io
                stl_data = io.BytesIO()
                mesh.export(stl_data, file_type='stl')
                stl_data.seek(0)
                
                print(f"[SUCCESS] STEP converted to STL ({len(stl_data.getvalue())} bytes)")
                
                # Serve as STL with appropriate headers
                return send_file(
                    stl_data,
                    mimetype='application/sla',
                    as_attachment=False,
                    download_name=filename.rsplit('.', 1)[0] + '.stl'
                )
                
            except Exception as e:
                print(f"[ERROR] STEP conversion failed: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({'error': f'Failed to convert STEP file: {str(e)}'}), 500
        
        # For STL files, serve directly
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        print(f"[ERROR] File serving error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index() -> str: return render_template('index.html')

@app.route('/api/quote/<int:quote_id>', methods=['GET'])
def get_quote_by_id(quote_id: int) -> Dict[str, Any]:
    """
    GET /api/quote/<id>
    Fetch a single quote by ID for editing
    
    Response:
        {
            'success': True,
            'quote': {
                'id': 1,
                'quote_id': 'Q-20260102-001',
                'customer_name': 'Test Corp',
                'contact_name': 'John Doe',
                'material': 'Aluminum 6061-T6',
                'quantity': 5,
                'final_quoted_price': 120.00,
                ...
            }
        }
    """
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                q.id, q.quote_id, q.material, q.quantity,
                q.system_price_anchor, q.final_quoted_price,
                q.target_date, q.notes,
                q.variance_json, q.pricing_tags_json,
                q.created_at, q.status,
                c.name as customer_name, c.id as customer_id,
                ct.name as contact_name, ct.id as contact_id,
                p.filename, p.fingerprint_json, p.volume,
                p.dimensions_json, p.process_routing_json,
                q.lead_time_date, q.lead_time_days,
                q.target_price_per_unit, q.price_breaks_json,
                q.outside_processing_json, q.quality_requirements_json,
                q.part_marking_json
            FROM ops__quotes q
            LEFT JOIN ops__customers c ON q.customer_id = c.id
            LEFT JOIN ops__contacts ct ON q.contact_id = ct.id
            LEFT JOIN ops__parts p ON q.part_id = p.id
            WHERE q.id = ?
        """, (quote_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Quote not found', 'success': False}), 404
        
        # Convert row to dict
        quote = {
            'id': row[0],
            'quote_id': row[1],
            'material': row[2],
            'quantity': row[3],
            'system_price_anchor': row[4],
            'final_quoted_price': row[5],
            'target_date': row[6],
            'notes': row[7],
            'variance_json': row[8],
            'pricing_tags_json': row[9],
            'created_at': row[10],
            'status': row[11],
            'customer_name': row[12],
            'customer_id': row[13],
            'contact_name': row[14],
            'contact_id': row[15],
            'filename': row[16],
            'fingerprint_json': row[17],
            'volume': row[18],
            'dimensions_json': row[19],
            'process_routing_json': row[20],
            'lead_time_date': row[21],
            'lead_time_days': row[22],
            'target_price_per_unit': row[23],
            'price_breaks_json': row[24],
            'outside_processing_json': row[25],
            'quality_requirements_json': row[26],
            'part_marking_json': row[27]
        }
        
        return jsonify({'success': True, 'quote': quote})
        
    except Exception as e:
        print(f"[ERROR] Get quote failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/pattern_suggestions', methods=['POST'])
def get_pattern_suggestions() -> Dict[str, Any]:
    """
    POST /api/pattern_suggestions
    Phase 5: "Ted View" - Pattern matching for variance tag suggestions
    
    Request Body:
        {
            'genesis_hash': str (optional),
            'customer_id': int (optional),
            'material': str (required),
            'quantity': int (required),
            'lead_time_days': int (optional)
        }
    
    Response:
        {
            'success': True,
            'suggestions': [
                {
                    'tag': 'Rush Job',
                    'confidence': 0.85,
                    'reason': '...',
                    'historical_count': 12,
                    'pattern_type': 'genesis_hash'
                },
                ...
            ],
            'has_patterns': bool
        }
    """
    try:
        mode, error = require_ops_mode()
        if error:
            return error
        if mode == "execution":
            return jsonify({
                "success": False,
                "error": "Planning routes are blocked in execution mode"
            }), 403
        import pattern_matcher
        
        data = request.get_json()
        
        genesis_hash = data.get('genesis_hash', None)
        customer_id = data.get('customer_id', None)
        material = data.get('material', 'Unknown')
        quantity = data.get('quantity', 1)
        lead_time_days = data.get('lead_time_days', None)
        
        result = pattern_matcher.get_pattern_suggestions_for_quote(
            genesis_hash=genesis_hash,
            customer_id=customer_id,
            material=material,
            quantity=quantity,
            lead_time_days=lead_time_days
        )
        
        return jsonify(result)
        
    except Exception as e:
        print(f"[ERROR] Pattern suggestions failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'success': False}), 500

# ============================================================================
# CUSTOMER MANAGEMENT API (Phase 5.6)
# ============================================================================

@app.route('/api/customers', methods=['GET'])
def api_get_customers():
    """Get all customers with summary statistics"""
    try:
        customers = database.get_all_customers()
        return jsonify({
            'success': True,
            'customers': customers
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/customer/<int:customer_id>', methods=['GET'])
def api_get_customer(customer_id):
    """Get full customer details"""
    try:
        customer = database.get_customer_details(customer_id)
        
        if not customer:
            return jsonify({
                'success': False,
                'error': 'Customer not found'
            }), 404
        
        return jsonify({
            'success': True,
            'customer': customer
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/customer', methods=['POST'])
def api_create_customer():
    """Create a new customer"""
    try:
        data = request.json
        company_name = data.get('company_name')
        domain = data.get('domain')
        
        if not company_name:
            return jsonify({
                'success': False,
                'error': 'company_name is required'
            }), 400
        
        customer_id = database.create_customer(company_name, domain)
        
        # Emit exhaust
        emit_cutter_event(
            event_type='CUSTOMER_CREATED',
            subject_ref=f'customer:{customer_id}',
            event_data={
                'name': company_name,
                'domain': domain
            }
        )
        
        return jsonify({
            'success': True,
            'customer_id': customer_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/customer/<int:customer_id>', methods=['PUT'])
def api_update_customer(customer_id):
    """Update customer information"""
    try:
        data = request.json
        company_name = data.get('company_name')
        domain = data.get('domain')
        
        # Get old values before update
        old_customer = database.get_customer_details(customer_id)
        
        success = database.update_customer(customer_id, company_name, domain)
        
        # Emit exhaust
        if success and old_customer:
            emit_cutter_event(
                event_type='CUSTOMER_UPDATED',
                subject_ref=f'customer:{customer_id}',
                event_data={
                    'old_name': old_customer['company_name'],
                    'new_name': company_name,
                    'old_domain': old_customer['domain'],
                    'new_domain': domain
                }
            )
        
        return jsonify({
            'success': success
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/customer/<int:customer_id>', methods=['DELETE'])
def api_delete_customer(customer_id):
    """Soft delete a customer"""
    try:
        # Get customer data before delete
        customer = database.get_customer_details(customer_id)
        
        if customer:
            success = database.delete_customer(customer_id)
            
            # Emit exhaust
            if success:
                emit_cutter_event(
                    event_type='CUSTOMER_DELETED',
                    subject_ref=f'customer:{customer_id}',
                    event_data={
                        'name': customer['company_name'],
                        'domain': customer['domain'],
                        'related_parts_count': customer.get('parts_count', 0),
                        'related_contacts_count': customer.get('contacts_count', 0),
                        'related_quotes_count': customer.get('quotes_count', 0)
                    }
                )
        else:
            success = database.delete_customer(customer_id)
        
        return jsonify({
            'success': success
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/customer/<int:customer_id>/contact', methods=['POST'])
def api_create_contact(customer_id):
    """Create a new contact for a customer"""
    try:
        data = request.json
        contact_name = data.get('contact_name')
        email = data.get('email')
        phone = data.get('phone')
        is_primary = data.get('is_primary', False)
        
        if not contact_name:
            return jsonify({
                'success': False,
                'error': 'contact_name is required'
            }), 400
        
        contact_id = database.create_contact_for_customer(
            customer_id, contact_name, email, phone, is_primary
        )
        
        # Emit exhaust
        emit_cutter_event(
            event_type='CONTACT_CREATED',
            subject_ref=f'contact:{contact_id}',
            event_data={
                'name': contact_name,
                'email': email if email else None,
                'customer_id': customer_id,
                'is_primary': is_primary
            }
        )
        
        return jsonify({
            'success': True,
            'contact_id': contact_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/contact/<int:contact_id>', methods=['PUT'])
def api_update_contact(contact_id):
    """Update contact information"""
    try:
        data = request.json
        contact_name = data.get('contact_name')
        email = data.get('email')
        phone = data.get('phone')
        
        # Get old values before update
        old_contact = database.get_contact_details(contact_id)
        
        success = database.update_contact(contact_id, contact_name, email, phone)
        
        # Emit exhaust
        if success and old_contact:
            emit_cutter_event(
                event_type='CONTACT_UPDATED',
                subject_ref=f'contact:{contact_id}',
                event_data={
                    'old_name': old_contact['name'],
                    'new_name': contact_name,
                    'old_email': old_contact['email'],
                    'new_email': email
                }
            )
        
        return jsonify({
            'success': success
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/contact/<int:contact_id>', methods=['DELETE'])
def api_delete_contact(contact_id):
    """Soft delete a contact"""
    try:
        # Get contact data before delete
        contact = database.get_contact_details(contact_id)
        
        if contact:
            # Count quotes that will have contact_id set to NULL
            quotes_count = database.count_quotes_for_contact(contact_id)
            
            success = database.delete_contact(contact_id)
            
            # Emit exhaust
            if success:
                emit_cutter_event(
                    event_type='CONTACT_DELETED',
                    subject_ref=f'contact:{contact_id}',
                    event_data={
                        'name': contact['name'],
                        'email': contact['email'],
                        'customer_id': contact['current_customer_id'],
                        'affected_quotes_count': quotes_count
                    }
                )
        else:
            success = database.delete_contact(contact_id)
        
        return jsonify({
            'success': success
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)