"""
Backward Compatibility Shim
Source of truth: ops_layer/app.py

This shim preserves the original entrypoint for:
- Direct execution: python app.py
- Legacy imports: from app import app
"""

from ops_layer.app import *

if __name__ == "__main__":
    from ops_layer.app import app
    app.run(host='0.0.0.0', port=5000, debug=True)
