from __future__ import annotations

from typing import Any
import threading


def _best_effort_close(obj: Any) -> None:
    """Attempt to gracefully close/stop common client resources.

    This tries common method names on the object itself and on likely
    attributes (e.g. websocket/http session clients and threads).
    Failures are swallowed intentionally to avoid masking CLI output.
    """
    if obj is None:
        return

    # Try common terminators on the object itself
    for meth in ("close", "shutdown", "disconnect", "stop"):
        try:
            candidate = getattr(obj, meth, None)
            if callable(candidate):
                candidate()
        except Exception:
            pass

    # Try closing likely sub-components (websockets, sessions, clients)
    likely_attrs = []
    try:
        likely_attrs = [
            name
            for name in dir(obj)
            if any(k in name.lower() for k in ("ws", "socket", "session", "client", "http"))
        ]
    except Exception:
        likely_attrs = []

    for name in likely_attrs:
        try:
            sub = getattr(obj, name)
        except Exception:
            continue
        for meth in ("close", "shutdown", "disconnect", "stop"):
            try:
                candidate = getattr(sub, meth, None)
                if callable(candidate):
                    candidate()
            except Exception:
                pass

    # Join any obvious background threads to let process exit
    try:
        for name in dir(obj):
            if "thread" in name.lower():
                try:
                    t = getattr(obj, name)
                    if isinstance(t, threading.Thread):
                        t.join(timeout=0.5)
                except Exception:
                    pass
    except Exception:
        pass


def cleanup_clients(*objs: Any) -> None:
    """Best-effort cleanup for any number of client-like objects."""
    for o in objs:
        try:
            _best_effort_close(o)
        except Exception:
            # Never let cleanup raise
            pass

