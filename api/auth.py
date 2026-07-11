"""Supabase JWT/session verification for protected Synapse API routes."""
from __future__ import annotations

import hashlib
import os
import threading
import time
from dataclasses import dataclass

import requests
from fastapi import Header, HTTPException

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://oybxogkpkkzywmmivkzy.supabase.co").rstrip("/")
SUPABASE_KEY = os.environ.get(
    "SUPABASE_PUBLISHABLE_KEY",
    "sb_publishable_Sz8R-hi_ccyAXoSjSeJu4g_xmv17UeE",
)
AUTH_REQUIRED = os.environ.get("AUTH_REQUIRED", "true").lower() in {"1", "true", "yes"}
_CACHE_TTL = int(os.environ.get("AUTH_CACHE_TTL_SECONDS", "60"))
_cache: dict[str, tuple[float, "Identity"]] = {}
_cache_lock = threading.Lock()


@dataclass(frozen=True)
class Identity:
    user_id: str
    email: str
    role: str
    approved: bool


def _deny(status: int, detail: str) -> None:
    raise HTTPException(status_code=status, detail=detail)


def _verify(access_token: str) -> Identity:
    digest = hashlib.sha256(access_token.encode()).hexdigest()
    now = time.monotonic()
    with _cache_lock:
        cached = _cache.get(digest)
        if cached and cached[0] > now:
            return cached[1]

    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(f"{SUPABASE_URL}/auth/v1/user", headers=headers, timeout=5)
    except requests.RequestException as exc:
        _deny(503, f"Authentication service unavailable: {type(exc).__name__}")
    if response.status_code != 200:
        _deny(401, "Invalid or expired session")
    user = response.json()
    user_id = str(user.get("id") or "")
    if not user_id:
        _deny(401, "Session has no user identity")

    role, approved = "maintenance", True
    try:
        profile = requests.get(
            f"{SUPABASE_URL}/rest/v1/profiles",
            headers=headers,
            params={"id": f"eq.{user_id}", "select": "role,approved", "limit": "1"},
            timeout=4,
        )
        if profile.status_code == 200 and profile.json():
            row = profile.json()[0]
            role, approved = str(row.get("role") or role), bool(row.get("approved", False))
    except (requests.RequestException, ValueError, KeyError, IndexError):
        pass
    if not approved:
        _deny(403, "Your Synapse account is awaiting approval")

    identity = Identity(user_id=user_id, email=str(user.get("email") or ""), role=role, approved=approved)
    with _cache_lock:
        _cache[digest] = (now + _CACHE_TTL, identity)
        if len(_cache) > 512:
            for key, value in list(_cache.items()):
                if value[0] <= now:
                    _cache.pop(key, None)
    return identity


def require_user(authorization: str | None = Header(default=None)) -> Identity:
    if not AUTH_REQUIRED:
        return Identity(user_id="development", email="", role="admin", approved=True)
    if not authorization or not authorization.lower().startswith("bearer "):
        _deny(401, "Sign in to use Synapse")
    return _verify(authorization.split(" ", 1)[1].strip())
