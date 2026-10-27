"""Native OAuth authentication and OS-keychain credential storage."""

import base64
from collections.abc import Callable, Generator
from contextlib import contextmanager
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import secrets
import socket
import time
from typing import Any
from urllib.parse import parse_qs, urlencode, urlsplit
import webbrowser

from filelock import FileLock, Timeout
import httpx
import keyring
from keyring.backend import KeyringBackend
from keyring.backends.chainer import ChainerBackend
from platformdirs import user_cache_path
from pydantic import BaseModel, Field, ValidationError

CLIENT_ID = "495516e90ed83a0b2ea7de54ff22818a"
REDIRECT_URI = "http://localhost:8765/oauth/callback"
AUTHORIZE_URL = "https://linear.app/oauth/authorize"
TOKEN_URL = "https://api.linear.app/oauth/token"
REVOKE_URL = "https://api.linear.app/oauth/revoke"
KEYRING_SERVICE = "linear-app"
KEYRING_ACCOUNT = "oauth"


class AuthError(Exception):
    """Authentication or secure-storage failure safe to display to the user."""


class Credentials(BaseModel):
    """One saved OAuth login; tokens are excluded from representations."""

    access_token: str = Field(min_length=1, repr=False)
    refresh_token: str = Field(min_length=1, repr=False)
    expires_at: float = Field(gt=0, allow_inf_nan=False)


@contextmanager
def _credential_lock() -> Generator[None]:
    # Only a lock file goes on disk; credentials live exclusively in the keychain.
    try:
        directory = user_cache_path("linear-app")
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        with FileLock(directory / "oauth.lock", timeout=35):
            yield
    except (OSError, Timeout) as exc:
        raise AuthError("Could not lock saved credentials. Try again shortly.") from exc


def _secure_keyring() -> KeyringBackend:
    backend = keyring.get_keyring()
    candidates = backend.backends if isinstance(backend, ChainerBackend) else [backend]
    # Do not accidentally use keyrings.alt's plaintext storage on headless hosts.
    secure_modules = {
        "keyring.backends.macOS",
        "keyring.backends.Windows",
        "keyring.backends.SecretService",
        "keyring.backends.libsecret",
        "keyring.backends.kwallet",
    }
    for candidate in candidates:
        if type(candidate).__module__ in secure_modules and candidate.priority > 0:
            return candidate
    raise AuthError(
        "No supported OS keychain is available. Configure macOS Keychain, Windows "
        "Credential Locker, Secret Service, or KWallet; or use LINEAR_API_KEY."
    )


def _load_credentials() -> Credentials | None:
    try:
        raw = _secure_keyring().get_password(KEYRING_SERVICE, KEYRING_ACCOUNT)
    except Exception as exc:
        raise AuthError(
            "Cannot read the OS keychain. Unlock/configure your keychain, "
            "or use LINEAR_API_KEY for headless environments."
        ) from exc
    if raw is None:
        return None
    try:
        return Credentials.model_validate_json(raw)
    except ValidationError as exc:
        raise AuthError("Saved login is invalid. Run `linear login` again.") from exc


def _save_credentials(credentials: Credentials) -> None:
    try:
        _secure_keyring().set_password(
            KEYRING_SERVICE, KEYRING_ACCOUNT, credentials.model_dump_json()
        )
    except Exception as exc:
        raise AuthError(
            "Cannot save credentials in the OS keychain. Unlock/configure your "
            "keychain and try again. No plaintext fallback is used."
        ) from exc


def save_credentials(credentials: Credentials) -> None:
    """Save a validated login in the OS keychain under an exclusive lock.

    Args:
        credentials: OAuth tokens and their expiry time.

    Raises:
        AuthError: If secure storage is unavailable.
    """
    with _credential_lock():
        _save_credentials(credentials)


def _token_request(data: dict[str, str]) -> Credentials:
    try:
        response = httpx.post(TOKEN_URL, data=data, timeout=30.0)
    except httpx.RequestError as exc:
        raise AuthError(
            "Cannot reach Linear to obtain OAuth tokens. Try again."
        ) from exc
    if response.status_code >= 400:
        # Never display token endpoint response bodies: they can contain secrets.
        raise AuthError(
            f"Linear rejected the OAuth token request (HTTP {response.status_code}). "
            "Try `linear login` again."
        )
    try:
        payload = response.json()
        if str(payload.get("token_type", "")).lower() != "bearer":
            raise ValueError("Unsupported token type")
        expires_in = float(payload["expires_in"])
        if expires_in <= 0:
            raise ValueError("Invalid lifetime")
        return Credentials(
            access_token=payload["access_token"],
            refresh_token=payload["refresh_token"],
            expires_at=time.time() + expires_in,
        )
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        raise AuthError("Linear returned an invalid OAuth token response.") from exc


def get_access_token() -> str:
    """Get the saved access token, refreshing and persisting rotation if needed.

    Returns:
        A currently valid OAuth access token.

    Raises:
        AuthError: If no login exists, refresh fails, or storage is unavailable.
    """
    # Serialize read/refresh/write across concurrent CLI processes so a stale
    # refresh response cannot overwrite newer rotated credentials.
    with _credential_lock():
        credentials = _load_credentials()
        if credentials is None:
            raise AuthError("Not logged in. Run `linear login` or set LINEAR_API_KEY.")
        if credentials.expires_at <= time.time() + 60:
            credentials = _token_request(
                {
                    "grant_type": "refresh_token",
                    "client_id": CLIENT_ID,
                    "refresh_token": credentials.refresh_token,
                }
            )
            _save_credentials(credentials)
        return credentials.access_token


class _CallbackServer(HTTPServer):
    # Bound both the callback wait and individual local connections.
    def get_request(self) -> tuple[socket.socket, Any]:
        connection, address = super().get_request()
        connection.settimeout(1.0)
        return connection, address


def _callback_handler(
    state: str, result: dict[str, str]
) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            # Request URLs contain authorization codes and must not be logged.
            pass

        def do_GET(self) -> None:
            parsed = urlsplit(self.path)
            params = parse_qs(parsed.query)
            if parsed.path != "/oauth/callback":
                self._reply(404, "Not found.")
                return
            states = params.get("state", [])
            if len(states) != 1 or not secrets.compare_digest(
                states[0].encode("utf-8"), state.encode("utf-8")
            ):
                self._reply(400, "Invalid OAuth state. Return to the terminal.")
                return
            if "error" in params:
                result["error"] = (
                    "Authorization was denied. Run `linear login` to retry."
                )
                self._reply(400, "Authorization failed. Return to the terminal.")
                return
            codes = params.get("code", [])
            if len(codes) != 1 or not codes[0]:
                self._reply(400, "Missing authorization code.")
                return
            result["code"] = codes[0]
            self._reply(200, "Authorization received. You can return to the terminal.")

        def _reply(self, status: int, message: str) -> None:
            body = message.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()
            try:
                self.wfile.write(body)
            except OSError:
                pass

    return Handler


def browser_login(show_url: Callable[[str], None], timeout: int = 180) -> Credentials:
    """Authorize through the browser using PKCE-S256 and a loopback callback.

    Args:
        show_url: Displays the authorization URL for manual browser opening.
        timeout: Maximum seconds to wait for browser authorization.

    Returns:
        Unsaved credentials to validate before replacing an existing login.

    Raises:
        AuthError: If binding, authorization, or the token exchange fails.
    """
    verifier = secrets.token_urlsafe(64)
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest())
        .rstrip(b"=")
        .decode("ascii")
    )
    state = secrets.token_urlsafe(32)
    url = (
        AUTHORIZE_URL
        + "?"
        + urlencode(
            {
                "client_id": CLIENT_ID,
                "redirect_uri": REDIRECT_URI,
                "response_type": "code",
                "scope": "read,write",
                "actor": "user",
                "state": state,
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "prompt": "consent",
            }
        )
    )
    result: dict[str, str] = {}
    try:
        server = _CallbackServer(("127.0.0.1", 8765), _callback_handler(state, result))
    except OSError as exc:
        raise AuthError(
            "Cannot listen on localhost:8765. Close the app using that port and retry."
        ) from exc
    with server:
        show_url(url)
        try:
            webbrowser.open(url)
        except webbrowser.Error:
            pass  # The displayed URL still allows opening the browser manually.
        deadline = time.monotonic() + timeout
        while not result and time.monotonic() < deadline:
            server.timeout = min(1.0, max(0.0, deadline - time.monotonic()))
            server.handle_request()
    if "error" in result:
        raise AuthError(result["error"])
    if "code" not in result:
        raise AuthError(
            "Login timed out waiting for the browser. Run `linear login` again."
        )
    return _token_request(
        {
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "code": result["code"],
            "code_verifier": verifier,
        }
    )


def logout() -> tuple[bool, bool]:
    """Revoke the saved OAuth grant and remove local tokens even if offline.

    Returns:
        Whether a saved login existed and whether remote revocation succeeded.

    Raises:
        AuthError: If local credential storage cannot be accessed or cleared.
    """
    with _credential_lock():
        # Read the raw record so even corrupt credentials can be removed.
        try:
            raw = _secure_keyring().get_password(KEYRING_SERVICE, KEYRING_ACCOUNT)
        except Exception as exc:
            raise AuthError("Cannot read the OS keychain to log out.") from exc
        if raw is None:
            return False, False
        revoked = False
        try:
            credentials = Credentials.model_validate_json(raw)
            response = httpx.post(
                REVOKE_URL,
                data={
                    "token": credentials.refresh_token,
                    "token_type_hint": "refresh_token",
                },
                timeout=30.0,
            )
            revoked = response.status_code == 200
        except (ValidationError, httpx.RequestError):
            pass
        try:
            _secure_keyring().delete_password(KEYRING_SERVICE, KEYRING_ACCOUNT)
        except Exception as exc:
            raise AuthError(
                "Cannot remove saved credentials from the OS keychain."
            ) from exc
        return True, revoked
