"""Rate limiter sencillo en memoria (ventana deslizante) para endpoints sensibles
(login/registro). Suficiente para un MVP de una sola instancia; en producción
multi-instancia se movería a Redis.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque

_hits: dict[str, deque[float]] = defaultdict(deque)


def allow(key: str, max_hits: int, window_s: float) -> bool:
    """Devuelve True si la acción para `key` está dentro del límite; False si lo supera."""
    now = time.monotonic()
    dq = _hits[key]
    while dq and dq[0] <= now - window_s:
        dq.popleft()
    if len(dq) >= max_hits:
        return False
    dq.append(now)
    return True
