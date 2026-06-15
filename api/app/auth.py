"""Endpoints de autenticación (Fase 4.5) y la dependencia get_current_user.

Seguridad aplicada (ver documentación/V1/09-seguridad.md):
- argon2id para contraseñas; errores de login genéricos (anti-enumeración).
- Sesión server-side: cookie httpOnly + SameSite (+ Secure en prod); token solo en cookie.
- Rate limit por IP en registro y login (anti fuerza bruta).
- Autorización por el user_id de la sesión (nunca del cliente).
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status

from . import auth_queries as aq
from . import ratelimit, security
from .db import get_conn
from .models import LoginIn, RegisterIn, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE_NAME = "session"
COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "false").lower() == "true"
SESSION_TTL = timedelta(days=7)

# Límites: nº de intentos por ventana, por IP.
_LOGIN_MAX, _LOGIN_WINDOW = 10, 300.0  # 10 / 5 min
_REGISTER_MAX, _REGISTER_WINDOW = 5, 3600.0  # 5 / hora


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _set_session_cookie(response: Response, conn, user_id: int) -> None:
    token = security.new_session_token()
    expires_at = datetime.now(timezone.utc) + SESSION_TTL
    aq.create_session(conn, security.hash_token(token), user_id, expires_at)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=int(SESSION_TTL.total_seconds()),
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/",
    )


def get_current_user(session: str | None = Cookie(default=None), conn=Depends(get_conn)) -> dict:
    """Dependencia: usuario autenticado o 401. Resuelve el user_id desde la sesión."""
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    user = aq.get_user_by_session(conn, security.hash_token(session))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión inválida o expirada")
    return user


def require_admin(user=Depends(get_current_user)) -> dict:
    """Dependencia: exige sesión Y rol admin (403 si no)."""
    if not user.get("is_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requiere permisos de administrador")
    return user


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(body: RegisterIn, request: Request, response: Response, conn=Depends(get_conn)) -> dict:
    if not ratelimit.allow(f"register:{_client_ip(request)}", _REGISTER_MAX, _REGISTER_WINDOW):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Demasiados intentos, prueba más tarde")

    user = aq.create_user(conn, body.email, security.hash_password(body.password), body.display_name)
    if user is None:
        # No revelamos si el email existe: mensaje genérico.
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se pudo crear la cuenta")

    _set_session_cookie(response, conn, user["id"])
    return user


@router.post("/login", response_model=UserOut)
def login(body: LoginIn, request: Request, response: Response, conn=Depends(get_conn)) -> dict:
    if not ratelimit.allow(f"login:{_client_ip(request)}", _LOGIN_MAX, _LOGIN_WINDOW):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Demasiados intentos, prueba más tarde")

    auth = aq.get_auth_by_email(conn, body.email)
    # Error genérico tanto si el email no existe como si la contraseña falla.
    if not auth or not auth["password_hash"] or not security.verify_password(auth["password_hash"], body.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    aq.touch_last_login(conn, auth["id"])
    _set_session_cookie(response, conn, auth["id"])
    user = aq.get_user_by_id(conn, auth["id"])
    assert user is not None
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, session: str | None = Cookie(default=None), conn=Depends(get_conn)) -> None:
    if session:
        aq.delete_session(conn, security.hash_token(session))
    response.delete_cookie(COOKIE_NAME, path="/")


@router.get("/me", response_model=UserOut)
def me(user=Depends(get_current_user)) -> dict:
    return user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(response: Response, user=Depends(get_current_user), conn=Depends(get_conn)) -> None:
    """Borra la cuenta y todos sus datos en cascada (RGPD)."""
    aq.delete_user(conn, user["id"])
    response.delete_cookie(COOKIE_NAME, path="/")
