"""
Pricing Engine for calculating material and labor costs.
"""
from typing import Dict, Optional, List
import database


# --- CONFIGURATION (Now Database-Driven) ---
# Refactoring Strike 1: Moved hardcoded values to shop_config table

def MATERIAL_MARKUP() -> float:
    """Material markup multiplier (The Anchor) - e.g., 1.2 = 20% markup"""
    return database.get_config('material_markup', 1.2)

# Specific quantity breaks for pricing (kept as constant - not shop-specific)
QUANTITY_BREAKS = [1, 5, 25, 100, 250]


class PriceCalculator:
    """
    Calculates pricing for machining operations.
    """
    
    def __init__(self) -> None:
        """
        Initialize the price calculator and ensure database is ready.
        """
        database.initialize_database()
        database.seed_default_data()
    
    def calculate_anchor(
        self,
        stock_volume_in3: float,
        material_name: str,
        per_part_time_mins: float,
        setup_time_mins: float,
        shop_rate_hour: float,
        quantity: int = 1,
        handling_time_mins: float = 0.5
    ) -> Dict[str, float]:
        """
        Calculate anchor pricing: material cost + labor cost.
        
        Formula: (Stock_Volume * MaterialCost) + ((Setup + (Per-Part + Handling) × Qty) / 60 * ShopRate)
        
        CRITICAL: Setup time is added ONCE, then (per-part + handling) time is multiplied by quantity.
        This prevents overcharging for multiple quantities.
        
        Note: User pays for the entire stock block, not just the part volume.
        
        Args:
            stock_volume_in3: Stock volume in cubic inches (user pays for whole block)
            material_name: Name of the material
            per_part_time_mins: Runtime per part in minutes (machine + hand, WITHOUT setup or handling)
            setup_time_mins: One-time setup time in minutes
            shop_rate_hour: Shop rate per hour
            quantity: Quantity of parts (default: 1)
            handling_time_mins: Time to swap parts between cycles (load, vise, unload) in minutes (default: 0.5)
            
        Returns:
            Dictionary with keys: material_cost, labor_cost, total_price, total_runtime_mins
            
        Raises:
            ValueError: If material is not found in database
        """
        # Look up material cost from database
        material_cost_per_in3 = database.get_material_cost(material_name)
        
        # Fallback Pricing: Use Aluminum 6061 values if material not found
        if material_cost_per_in3 is None:
            print(f"WARNING: Material '{material_name}' not found. Using fallback pricing.")
            material_cost_per_in3 = 0.30  # Aluminum 6061 cost
        
        # Calculate base material cost per unit (billed for stock volume, not part volume)
        # Apply material markup (The Anchor)
        base_material_cost_per_unit = stock_volume_in3 * material_cost_per_in3 * MATERIAL_MARKUP()
        
        # Apply setup scrap logic
        if quantity < 10:
            # For low quantities: add 1 extra unit for setup scrap
            material_units = quantity + 1
            total_material_cost = base_material_cost_per_unit * material_units
        else:
            # For higher quantities: add 2% scrap factor
            total_material_cost = base_material_cost_per_unit * quantity * 1.02
        
        # Calculate labor cost: ONE-TIME setup + ((per-part time + handling time) × quantity)
        # FIX: This prevents multiplying setup time by quantity
        # NEW: Includes handling time (load/unload between cycles) per part
        total_runtime_mins = setup_time_mins + ((per_part_time_mins + handling_time_mins) * quantity)
        total_labor_cost = (total_runtime_mins / 60.0) * shop_rate_hour
        
        # Calculate per-unit costs for display
        labor_cost_per_unit = total_labor_cost / quantity
        
        # Calculate total
        total_price = total_material_cost + total_labor_cost
        
        return {
            'material_cost': total_material_cost,
            'labor_cost': total_labor_cost,
            'total_price': total_price,
            'material_cost_per_unit': base_material_cost_per_unit,
            'labor_cost_per_unit': labor_cost_per_unit,
            'total_runtime_mins': total_runtime_mins  # For transparency
        }
    
    def calculate_price_breaks(
        self,
        stock_volume_in3: float,
        material_name: str,
        per_part_time_mins: float,
        setup_time_mins: float,
        shop_rate_hour: float
    ) -> Dict[int, Dict[str, float]]:
        """
        Calculate pricing for specific quantity breaks: [1, 5, 25, 100, 250].
        
        Args:
            stock_volume_in3: Stock volume in cubic inches
            material_name: Name of the material
            per_part_time_mins: Runtime per part in minutes (WITHOUT setup)
            setup_time_mins: One-time setup time in minutes
            shop_rate_hour: Shop rate per hour
            
        Returns:
            Dictionary mapping quantity to price breakdown:
            {
                1: {'total_price': ..., 'material_cost': ..., 'labor_cost': ...},
                5: {...},
                ...
            }
        """
        price_breaks = {}
        
        for qty in QUANTITY_BREAKS:
            price_result = self.calculate_anchor(
                stock_volume_in3=stock_volume_in3,
                material_name=material_name,
                per_part_time_mins=per_part_time_mins,
                setup_time_mins=setup_time_mins,
                shop_rate_hour=shop_rate_hour,
                quantity=qty
            )
            
            price_breaks[qty] = {
                'total_price': round(price_result['total_price'], 2),
                'material_cost': round(price_result['material_cost'], 2),
                'labor_cost': round(price_result['labor_cost'], 2),
                'price_per_unit': round(price_result['total_price'] / qty, 2)
            }
        
        return price_breaks

