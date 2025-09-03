"""Shared ingestor utilities (types, parsers) used across runners.

This package is introduced for refactoring cohesion; existing modules in
`qryptify_ingestor/` import these helpers to preserve behavior.
"""

__all__ = [
    "types",
    "parsers",
]
