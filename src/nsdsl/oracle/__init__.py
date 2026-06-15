"""Ground-truth oracle: the privileged observer that makes correctness measurable."""
from __future__ import annotations

from .god_log import GodLog, LogEntry
from .truth import Oracle

__all__ = ["GodLog", "LogEntry", "Oracle"]
