"""
Pattern Matcher - Local History Analysis for "Ted View"
Phase 5: RFQ-First Refactor
PHASE 3 REMEDIATION: "Guild Intelligence" → "Local History" (this analyzes local shop data)

Purpose: Detect pricing patterns from historical quotes to suggest variance tags.

The system looks for:
1. Genesis Hash matches (Same geometry)
2. Customer patterns (This customer always gets X tag)
3. Material patterns (Titanium always gets "Difficult Material" tag)
4. Quantity patterns (Low qty = "Prototype" tag)

Output: Suggested variance tags with confidence scores for "Ted View" UI banner.
"""

import sqlite3
import json
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import sys
import os

# Add parent directory to path for cross-layer imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

# Use database module's connection (respects TEST_DB_PATH for hermetic testing)
def get_db_connection():
    """Get database connection via the database module."""
    return database.get_connection()

# ============================================================================
# PATTERN DETECTION LOGIC
# ============================================================================

def detect_patterns(
    genesis_hash: Optional[str],
    customer_id: Optional[int],
    material: str,
    quantity: int,
    lead_time_days: Optional[int] = None
) -> List[Dict]:
    """
    Detect pricing patterns from historical quotes.
    
    Args:
        genesis_hash: SHA-256 hash of geometry (The "ISBN" of parts)
        customer_id: Customer ID (for customer-specific patterns)
        material: Material name
        quantity: Quantity requested
        lead_time_days: Days until delivery (for rush detection)
    
    Returns:
        List of suggested variance tags with confidence scores:
        [
            {
                'tag': 'Rush Job',
                'confidence': 0.85,
                'reason': 'This customer has received Rush Job tag on 85% of quotes',
                'historical_count': 12
            },
            ...
        ]
    """
    try:
        conn = get_db_connection()
    except Exception as e:
        print(f"[PATTERN MATCHER] Database connection failed: {e}")
        return []
    cursor = conn.cursor()
    
    suggestions = []
    
    try:
        # ===== PATTERN 1: EXACT GEOMETRY MATCH (Genesis Hash) =====
        if genesis_hash:
            suggestions.extend(_detect_genesis_patterns(cursor, genesis_hash))
        
        # ===== PATTERN 2: CUSTOMER PATTERNS =====
        if customer_id:
            suggestions.extend(_detect_customer_patterns(cursor, customer_id))
        
        # ===== PATTERN 3: MATERIAL PATTERNS =====
        suggestions.extend(_detect_material_patterns(cursor, material))
        
        # ===== PATTERN 4: QUANTITY PATTERNS =====
        suggestions.extend(_detect_quantity_patterns(cursor, quantity))
        
        # ===== PATTERN 5: LEAD TIME PATTERNS (Rush Detection) =====
        if lead_time_days is not None:
            suggestions.extend(_detect_lead_time_patterns(cursor, lead_time_days))
        
        # Deduplicate and sort by confidence
        suggestions = _deduplicate_suggestions(suggestions)
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Return top 5 suggestions
        return suggestions[:5]
        
    except Exception as e:
        print(f"[PATTERN MATCHER] Error: {e}")
        return []
    finally:
        conn.close()

# ============================================================================
# PATTERN DETECTION FUNCTIONS
# ============================================================================

def _detect_genesis_patterns(cursor, genesis_hash: str) -> List[Dict]:
    """Detect patterns for this exact geometry (The Gold Standard)."""
    suggestions = []
    
    # Find all quotes for this geometry
    cursor.execute("""
        SELECT q.pricing_tags_json, q.variance_json
        FROM ops__quotes q
        JOIN ops__parts p ON q.part_id = p.id
        WHERE p.genesis_hash = ?
        AND q.pricing_tags_json IS NOT NULL
        AND q.status IN ('Sent', 'Won')
    """, (genesis_hash,))
    
    rows = cursor.fetchall()
    if not rows:
        return suggestions
    
    # Count tag occurrences
    tag_counts = {}
    total_quotes = len(rows)
    
    for row in rows:
        try:
            tags = json.loads(row['pricing_tags_json'])
            for tag_name, tag_value in tags.items():
                if tag_value > 0:  # Only count active tags
                    tag_counts[tag_name] = tag_counts.get(tag_name, 0) + 1
        except (json.JSONDecodeError, TypeError):
            continue
    
    # Generate suggestions for tags that appear in >50% of quotes
    for tag_name, count in tag_counts.items():
        confidence = count / total_quotes
        if confidence >= 0.5:  # 50% threshold
            suggestions.append({
                'tag': tag_name,
                'confidence': confidence,
                'reason': f'This exact geometry has been quoted {total_quotes} times. "{tag_name}" was applied {count} times.',
                'historical_count': count,
                'pattern_type': 'genesis_hash'
            })
    
    return suggestions

def _detect_customer_patterns(cursor, customer_id: int) -> List[Dict]:
    """Detect patterns for this specific customer."""
    suggestions = []
    
    cursor.execute("""
        SELECT pricing_tags_json
        FROM ops__quotes
        WHERE customer_id = ?
        AND pricing_tags_json IS NOT NULL
        AND status IN ('Sent', 'Won')
    """, (customer_id,))
    
    rows = cursor.fetchall()
    if not rows or len(rows) < 3:  # Need at least 3 quotes for pattern
        return suggestions
    
    tag_counts = {}
    total_quotes = len(rows)
    
    for row in rows:
        try:
            tags = json.loads(row['pricing_tags_json'])
            for tag_name, tag_value in tags.items():
                if tag_value > 0:
                    tag_counts[tag_name] = tag_counts.get(tag_name, 0) + 1
        except (json.JSONDecodeError, TypeError):
            continue
    
    # Generate suggestions for tags that appear in >60% of customer quotes
    for tag_name, count in tag_counts.items():
        confidence = count / total_quotes
        if confidence >= 0.6:  # 60% threshold for customer patterns
            suggestions.append({
                'tag': tag_name,
                'confidence': confidence,
                'reason': f'This customer has received "{tag_name}" on {count} of {total_quotes} previous quotes.',
                'historical_count': count,
                'pattern_type': 'customer'
            })
    
    return suggestions

def _detect_material_patterns(cursor, material: str) -> List[Dict]:
    """Detect patterns for this material across all quotes."""
    suggestions = []
    
    # Normalize material name
    material_normalized = material.strip().lower()
    
    cursor.execute("""
        SELECT pricing_tags_json
        FROM ops__quotes
        WHERE LOWER(material) = ?
        AND pricing_tags_json IS NOT NULL
        AND status IN ('Sent', 'Won')
    """, (material_normalized,))
    
    rows = cursor.fetchall()
    if not rows or len(rows) < 5:  # Need at least 5 quotes for material pattern
        return suggestions
    
    tag_counts = {}
    total_quotes = len(rows)
    
    for row in rows:
        try:
            tags = json.loads(row['pricing_tags_json'])
            for tag_name, tag_value in tags.items():
                if tag_value > 0:
                    tag_counts[tag_name] = tag_counts.get(tag_name, 0) + 1
        except (json.JSONDecodeError, TypeError):
            continue
    
    # Generate suggestions for tags that appear in >70% of material quotes
    for tag_name, count in tag_counts.items():
        confidence = count / total_quotes
        if confidence >= 0.7:  # 70% threshold for material patterns
            suggestions.append({
                'tag': tag_name,
                'confidence': confidence,
                'reason': f'Parts made from {material} have received "{tag_name}" on {count} of {total_quotes} quotes.',
                'historical_count': count,
                'pattern_type': 'material'
            })
    
    return suggestions

def _detect_quantity_patterns(cursor, quantity: int) -> List[Dict]:
    """Detect patterns based on quantity (Prototype vs. Production)."""
    suggestions = []
    
    # Prototype pattern (qty 1-5)
    if quantity <= 5:
        cursor.execute("""
            SELECT pricing_tags_json
            FROM ops__quotes
            WHERE quantity <= 5
            AND pricing_tags_json IS NOT NULL
            AND status IN ('Sent', 'Won')
        """)
        
        rows = cursor.fetchall()
        if rows and len(rows) >= 10:
            tag_counts = {}
            total_quotes = len(rows)
            
            for row in rows:
                try:
                    tags = json.loads(row['pricing_tags_json'])
                    for tag_name, tag_value in tags.items():
                        if tag_value > 0 and 'proto' in tag_name.lower():
                            tag_counts[tag_name] = tag_counts.get(tag_name, 0) + 1
                except (json.JSONDecodeError, TypeError):
                    continue
            
            for tag_name, count in tag_counts.items():
                confidence = count / total_quotes
                if confidence >= 0.5:
                    suggestions.append({
                        'tag': tag_name,
                        'confidence': confidence,
                        'reason': f'Low quantity orders (1-5 units) often receive "{tag_name}".',
                        'historical_count': count,
                        'pattern_type': 'quantity'
                    })
    
    return suggestions

def _detect_lead_time_patterns(cursor, lead_time_days: int) -> List[Dict]:
    """Detect rush job patterns based on lead time."""
    suggestions = []
    
    # Rush pattern (< 7 days)
    if lead_time_days < 7:
        cursor.execute("""
            SELECT pricing_tags_json
            FROM ops__quotes
            WHERE lead_time_days < 7
            AND pricing_tags_json IS NOT NULL
            AND status IN ('Sent', 'Won')
        """)
        
        rows = cursor.fetchall()
        if rows and len(rows) >= 5:
            tag_counts = {}
            total_quotes = len(rows)
            
            for row in rows:
                try:
                    tags = json.loads(row['pricing_tags_json'])
                    for tag_name, tag_value in tags.items():
                        if tag_value > 0 and ('rush' in tag_name.lower() or 'expedite' in tag_name.lower()):
                            tag_counts[tag_name] = tag_counts.get(tag_name, 0) + 1
                except (json.JSONDecodeError, TypeError):
                    continue
            
            for tag_name, count in tag_counts.items():
                confidence = count / total_quotes
                if confidence >= 0.6:
                    suggestions.append({
                        'tag': tag_name,
                        'confidence': confidence,
                        'reason': f'Lead times under 7 days often receive "{tag_name}".',
                        'historical_count': count,
                        'pattern_type': 'lead_time'
                    })
    
    return suggestions

def _deduplicate_suggestions(suggestions: List[Dict]) -> List[Dict]:
    """Remove duplicate tags, keeping the one with highest confidence."""
    seen = {}
    for suggestion in suggestions:
        tag = suggestion['tag']
        if tag not in seen or suggestion['confidence'] > seen[tag]['confidence']:
            seen[tag] = suggestion
    
    return list(seen.values())

# ============================================================================
# API ENDPOINT HELPER
# ============================================================================

def get_pattern_suggestions_for_quote(
    genesis_hash: Optional[str],
    customer_id: Optional[int],
    material: str,
    quantity: int,
    lead_time_days: Optional[int] = None
) -> Dict:
    """
    Wrapper function for Flask endpoint.
    
    Returns:
        {
            'success': True,
            'suggestions': [...],
            'has_patterns': bool
        }
    """
    suggestions = detect_patterns(genesis_hash, customer_id, material, quantity, lead_time_days)
    
    return {
        'success': True,
        'suggestions': suggestions,
        'has_patterns': len(suggestions) > 0
    }

