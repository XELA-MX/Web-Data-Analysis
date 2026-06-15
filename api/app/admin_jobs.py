"""Ejecuta un "refresco" (scraper Go + procesador Python) en segundo plano y
expone su estado EN VIVO: paso actual, progreso y un log de eventos legibles.

Lee el stdout/stderr de cada subproceso línea a línea y lo traduce a mensajes
amigables. Single-instance / un trabajo a la vez (MVP).

Seguridad: los comandos son fijos (listas de args, sin shell) → sin inyección.
"""

from __future__ import annotations

import os
import re
import socket
import subprocess
import threading
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

# /api/app/admin_jobs.py → repo root = parents[2]
_REPO = Path(__file__).resolve().parents[2]
_SCRAPER_DIR = _REPO / "scraper"
_PROCESSOR_DIR = _REPO / "processor"
_PROCESSOR_PY = _PROCESSOR_DIR / ".venv" / "bin" / "python"

_lock = threading.Lock()
_log: deque[str] = deque(maxlen=14)
_state: dict = {
    "status": "idle",
    "step": None,
    "progress": 0,
    "message": None,
    "started_at": None,
    "finished_at": None,
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _set(**kw) -> None:
    with _lock:
        _state.update(kw)


def _emit(msg: str) -> None:
    with _lock:
        _log.append(msg)
        _state["message"] = msg


def get_state() -> dict:
    with _lock:
        return {**_state, "log": list(_log)}


def start_refresh(full: bool = False) -> bool:
    """Lanza un refresco en background. Devuelve False si ya hay uno en curso."""
    with _lock:
        if _state["status"] == "running":
            return False
        _log.clear()
        _state.update(
            status="running", step="Iniciando", progress=3, message="Preparando la búsqueda…",
            started_at=_now(), finished_at=None,
        )
    threading.Thread(target=_run, args=(full,), daemon=True).start()
    return True


def _has_internet(host: str = "www.getmanfred.com", port: int = 443, timeout: float = 4.0) -> bool:
    """Comprobación rápida de conectividad (evita esperar a que fallen los reintentos)."""
    try:
        socket.create_connection((host, port), timeout=timeout).close()
        return True
    except OSError:
        return False


def _run(full: bool) -> None:
    try:
        # Precheck: si no hay internet, fallar rápido y claro (no se pierde nada).
        _set(step="Comprobando conexión", progress=5)
        _emit("Comprobando la conexión a internet…")
        if not _has_internet():
            raise RuntimeError("Sin conexión a internet. Conéctate y vuelve a intentarlo.")

        details = "true" if full else "false"
        _set(step="Rastreando fuentes", progress=10)
        _emit("Conectando con las fuentes de empleo…")
        _stream(["go", "run", "./cmd/scraper", "-sink=postgres", f"-manfred-details={details}"], _SCRAPER_DIR, "scraper", 900)

        _set(step="Procesando ofertas", progress=70)
        _emit("Limpiando y enriqueciendo las ofertas…")
        _stream([str(_PROCESSOR_PY), "-m", "processor"], _PROCESSOR_DIR, "processor", 600)

        _set(status="done", step="Completado", progress=100, finished_at=_now())
        _emit("¡Listo! Ofertas actualizadas correctamente.")
    except Exception as e:  # noqa: BLE001 — reportamos cualquier fallo al admin
        _set(status="error", step="Error", finished_at=_now())
        _emit(f"{str(e)[:240]} — puedes reintentar; lo ya guardado no se pierde.")


def _stream(cmd: list[str], cwd: Path, kind: str, timeout: int) -> None:
    proc = subprocess.Popen(
        cmd,
        cwd=str(cwd),
        env=os.environ.copy(),  # incluye DATABASE_URI (cargada por dotenv)
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    raw_tail: deque[str] = deque(maxlen=6)
    persisted = 0
    try:
        assert proc.stdout is not None
        for raw in proc.stdout:
            line = raw.strip()
            if not line:
                continue
            raw_tail.append(line)
            friendly = _friendly(line, kind)
            if friendly:
                _emit(friendly)
            if kind == "scraper" and "persistidos" in line:
                persisted += 1
                _set(progress=min(65, 15 + persisted * 12))
            elif kind == "processor" and "acumulado" in line:
                _set(progress=min(95, max(75, _state.get("progress", 75) + 4)))
        proc.wait(timeout=timeout)
    finally:
        if proc.poll() is None:
            proc.kill()
    if proc.returncode != 0:
        raise RuntimeError(f"{kind} falló: " + " | ".join(list(raw_tail)[-3:]))


_MSG_RE = re.compile(r'msg="([^"]+)"')
_SRC_RE = re.compile(r"source=(\S+)")
_JOBS_RE = re.compile(r"jobs=(\d+)")
_ACC_RE = re.compile(r"acumulado (\d+)")


def _friendly(line: str, kind: str) -> str | None:
    """Traduce una línea de log técnica a un mensaje legible (o None si se ignora)."""
    if kind == "scraper":
        m = _MSG_RE.search(line)
        if not m:
            return None
        msg = m.group(1)
        src = _SRC_RE.search(line)
        jobs = _JOBS_RE.search(line)
        if msg == "fuente ok" and src:
            extra = f" ({jobs.group(1)} ofertas)" if jobs else ""
            return f"Leída la fuente «{src.group(1)}»{extra}"
        if msg == "fuente falló" and src:
            return f"⚠ No se pudo leer «{src.group(1)}» (se omite, el resto sigue)"
        if msg == "raw_jobs persistidos" and src:
            return f"Guardadas las ofertas de «{src.group(1)}»"
        if msg == "resumen fuentes":
            ok = re.search(r"ok=(\d+)", line)
            fail = re.search(r"fallidas=(\d+)", line)
            if ok and fail:
                return f"Fuentes: {ok.group(1)} OK, {fail.group(1)} con error"
        if msg == "scrape completado":
            return "Todas las fuentes rastreadas ✓"
        return None
    # processor
    acc = _ACC_RE.search(line)
    if acc:
        return f"Procesadas {acc.group(1)} ofertas…"
    if "deduplicación" in line:
        return "Quitando duplicados…"
    if "procesado completado" in line:
        return "Procesado terminado ✓"
    return None
