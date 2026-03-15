"""
Admin package initializer.

This file intentionally left minimal. It makes the `admin` folder a Python
package so imports like `from admin import uzivatel_admin` work correctly.
"""

# Expose submodules for convenience (keep explicit to avoid accidental imports)
__all__ = ["uzivatel_admin"]
