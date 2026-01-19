"""
Ops Layer Package

The Ops Layer performs work, holds domain meaning, and contains mutable operational data.
This layer implements the core business logic of the quoting and manufacturing system.

Module Organization:
- app.py: Flask application and HTTP API endpoints
- estimator.py: Geometry analysis and runtime estimation
- pricing_engine.py: Price calculation with material/labor costs
- genesis_hash.py: Deterministic geometry fingerprinting
- pattern_matcher.py: Historical quote pattern matching
- pdf_generator.py: Quote and traveler PDF generation
- templates/: HTML templates for Flask
- static/: CSS, JavaScript, and static assets

Constitutional Boundary:
The Ops Layer emits operational exhaust to the Cutter Ledger via the boundary module.
It must not directly write to ledger tables.
"""

# Public API exports (for backward compatibility)
# This allows `from ops_layer import app` instead of `from ops_layer.app import app`

__version__ = "1.0.0"
__all__ = []  # Intentionally empty; use explicit imports like ops_layer.app
