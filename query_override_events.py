"""
Query Script: Analyze QUOTE_OVERRIDDEN Events

Demonstrates how to query the operational_events ledger to understand
override patterns, frequency, and persistence.

CONSTITUTIONAL NOTE: This script OBSERVES the ledger, it does NOT:
- Recommend actions (C5: Separation of Observation and Judgment)
- Label outcomes as good/bad (C1: Outcome Agnosticism)
- Smooth variance (C6: No Aggregation That Obscures Variance)

All output is purely descriptive.
"""

import sqlite3
import json
from datetime import datetime


def query_all_override_events():
    """Query all QUOTE_OVERRIDDEN events in the ledger."""
    
    conn = sqlite3.connect('cutter.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            oe.id,
            oe.event_type,
            oe.subject_ref,
            oe.event_data,
            oe.created_at,
            q.quote_id as quote_id_human,
            q.material,
            q.quantity
        FROM cutter__events oe
        LEFT JOIN ops__quotes q ON 
            CASE 
                WHEN oe.subject_ref LIKE 'quote:%' THEN 
                    CAST(SUBSTR(oe.subject_ref, 7) AS INTEGER)
                ELSE NULL 
            END = q.id
        WHERE oe.event_type = 'QUOTE_OVERRIDDEN'
        ORDER BY oe.created_at DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return rows


def query_override_frequency_by_quote():
    """Count how many times each quote has been overridden."""
    
    conn = sqlite3.connect('cutter.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            subject_ref,
            COUNT(*) as override_count,
            MIN(created_at) as first_override,
            MAX(created_at) as last_override
        FROM cutter__events
        WHERE event_type = 'QUOTE_OVERRIDDEN'
        GROUP BY subject_ref
        ORDER BY override_count DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return rows


def query_override_magnitude_distribution():
    """Analyze the distribution of override magnitudes."""
    
    conn = sqlite3.connect('cutter.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT event_data, created_at
        FROM cutter__events
        WHERE event_type = 'QUOTE_OVERRIDDEN'
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    magnitudes = []
    for row in rows:
        data = json.loads(row['event_data'])
        magnitudes.append({
            'override_delta': data.get('override_delta', 0),
            'override_percent': data.get('override_percent', 0),
            'created_at': row['created_at']
        })
    
    return magnitudes


def main():
    print("\n" + "="*80)
    print("LEDGER QUERY: QUOTE_OVERRIDDEN Events")
    print("="*80 + "\n")
    
    # Query 1: All override events
    print("[QUERY 1] All QUOTE_OVERRIDDEN Events")
    print("-" * 80)
    
    events = query_all_override_events()
    
    if not events:
        print("  No override events found in ledger.")
    else:
        print(f"  Found {len(events)} override event(s)\n")
        
        for event in events:
            data = json.loads(event['event_data'])
            print(f"  Event ID: {event['id']}")
            print(f"  Subject: {event['subject_ref']}")
            if event['quote_id_human']:
                print(f"  Quote: {event['quote_id_human']}")
            print(f"  Created: {event['created_at']}")
            print(f"  Anchor Price: ${data.get('system_price_anchor', 0):.2f}")
            print(f"  Final Price: ${data.get('final_quoted_price', 0):.2f}")
            print(f"  Override: ${data.get('override_delta', 0):+.2f} ({data.get('override_percent', 0):+.1f}%)")
            print(f"  Material: {data.get('material', 'N/A')}")
            print(f"  Quantity: {data.get('quantity', 'N/A')}")
            print()
    
    # Query 2: Override frequency by quote
    print("\n[QUERY 2] Override Frequency by Quote")
    print("-" * 80)
    
    freq_data = query_override_frequency_by_quote()
    
    if not freq_data:
        print("  No override frequency data.")
    else:
        print(f"  Quotes with overrides: {len(freq_data)}\n")
        
        for row in freq_data:
            print(f"  Subject: {row[0]}")
            print(f"    Override Count: {row[1]}")
            print(f"    First Override: {row[2]}")
            print(f"    Last Override: {row[3]}")
            
            # Calculate time-in-persistence (if multiple overrides)
            if row[1] > 1:
                first = datetime.fromisoformat(row[2])
                last = datetime.fromisoformat(row[3])
                duration = (last - first).total_seconds() / 60.0  # minutes
                print(f"    Time Between First/Last: {duration:.1f} minutes")
            print()
    
    # Query 3: Override magnitude distribution
    print("\n[QUERY 3] Override Magnitude Distribution")
    print("-" * 80)
    
    magnitudes = query_override_magnitude_distribution()
    
    if not magnitudes:
        print("  No magnitude data.")
    else:
        # Calculate descriptive statistics (NO interpretation, C6)
        deltas = [m['override_delta'] for m in magnitudes]
        percents = [m['override_percent'] for m in magnitudes]
        
        print(f"  Total Overrides: {len(magnitudes)}")
        print(f"\n  Dollar Override:")
        print(f"    Min: ${min(deltas):.2f}")
        print(f"    Max: ${max(deltas):.2f}")
        print(f"    Mean: ${sum(deltas) / len(deltas):.2f}")
        
        print(f"\n  Percentage Override:")
        print(f"    Min: {min(percents):.1f}%")
        print(f"    Max: {max(percents):.1f}%")
        print(f"    Mean: {sum(percents) / len(percents):.1f}%")
        
        # Show distribution (no smoothing, C6)
        print(f"\n  Individual Overrides (chronological):")
        for m in reversed(magnitudes[-5:]):  # Last 5
            print(f"    {m['created_at']}: ${m['override_delta']:+.2f} ({m['override_percent']:+.1f}%)")
    
    print("\n" + "="*80)
    print("NOTE: This output is purely descriptive (C1: Outcome Agnosticism)")
    print("      No recommendations, no labels, no smoothing.")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
