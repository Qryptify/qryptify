"""Test bootstrap.

Prefer editable installs (pip install -e .). If not installed, add repo root to
sys.path so imports like `qryptify_strategy.*` work when running pytest from
the project root.
"""

from __future__ import annotations

from pathlib import Path
import sys

try:
    import qryptify  # noqa: F401
    import qryptify_strategy  # noqa: F401
except Exception:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
