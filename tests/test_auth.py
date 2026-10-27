"""Offline OAuth, keychain, client integration, and CLI regressions."""

import base64
import hashlib
import http.client
import json
import os
from pathlib import Path
import tempfile
import threading
import time
from typing import Any
import unittest
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlencode, urlsplit

import httpx
from keyring.backends.fail import Keyring as FailKeyring
from typer.testing import CliRunner

from linear import auth
from linear.api import LinearClient, LinearClientError
from linear.cli import app

_secure_backend = auth._secure_keyring


class AuthTests(unittest.TestCase):
    """Keep credentials, browser callbacks, and HTTP entirely local to tests."""

    def setUp(self) -> None:
        self.runner = CliRunner()
        self.record: str | None = None
        self.backend = Mock()
        self.backend.get_password.side_effect = lambda *_: self.record
        self.backend.set_password.side_effect = self._store
        self.backend.delete_password.side_effect = self._delete
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        for mocked in (
            patch.dict(os.environ, {}, clear=True),
            patch("linear.auth._secure_keyring", return_value=self.backend),
            patch("linear.auth.user_cache_path", return_value=Path(directory.name)),
            patch("httpx.Client.send", side_effect=AssertionError("Unexpected HTTP")),
        ):
            mocked.start()
            self.addCleanup(mocked.stop)

    def _store(self, service: str, account: str, value: str) -> None:
        self.record = value

    def _delete(self, service: str, account: str) -> None:
        self.record = None

    def _credentials(self, *, expired: bool = False) -> auth.Credentials:
        return auth.Credentials(
            access_token="secret-access",
            refresh_token="secret-refresh",
            expires_at=time.time() + (-1 if expired else 3600),
        )

    def _token_response(self, **changes: Any) -> httpx.Response:
        payload = {
            "access_token": "rotated-access",
            "refresh_token": "rotated-refresh",
            "expires_in": 86400,
            "token_type": "Bearer",
        }
        payload.update(changes)
        return httpx.Response(200, json=payload)

    def test_saved_login_and_refresh_rotation(self) -> None:
        auth.save_credentials(self._credentials())
        with patch("linear.auth.httpx.post") as post:
            self.assertEqual(auth.get_access_token(), "secret-access")
            post.assert_not_called()
        auth.save_credentials(self._credentials(expired=True))
        with patch(
            "linear.auth.httpx.post", return_value=self._token_response()
        ) as post:
            self.assertEqual(auth.get_access_token(), "rotated-access")
        self.assertEqual(
            post.call_args.kwargs["data"],
            {
                "grant_type": "refresh_token",
                "client_id": auth.CLIENT_ID,
                "refresh_token": "secret-refresh",
            },
        )
        saved = auth.Credentials.model_validate_json(self.record or "")
        self.assertEqual(saved.refresh_token, "rotated-refresh")
        self.assertNotIn("secret", repr(self._credentials()))

    def test_missing_corrupt_and_unavailable_credentials(self) -> None:
        with self.assertRaisesRegex(auth.AuthError, "linear login"):
            auth.get_access_token()
        self.record = "invalid json"
        with self.assertRaisesRegex(auth.AuthError, "invalid"):
            auth.get_access_token()
        self.backend.get_password.side_effect = RuntimeError("private backend details")
        with self.assertRaisesRegex(auth.AuthError, "keychain") as caught:
            auth.get_access_token()
        self.assertNotIn("private", str(caught.exception))

    def test_keychain_write_failure_has_no_fallback(self) -> None:
        self.backend.set_password.side_effect = RuntimeError("secret")
        with self.assertRaisesRegex(auth.AuthError, "No plaintext fallback"):
            auth.save_credentials(self._credentials())
        self.assertIsNone(self.record)

    def test_secure_backend_rejects_plaintext_and_fail_backends(self) -> None:
        # Call the actual function underneath the test's keychain mock.
        for backend in (FailKeyring(), Mock()):
            with patch("linear.auth.keyring.get_keyring", return_value=backend):
                with self.assertRaisesRegex(auth.AuthError, "No supported OS keychain"):
                    _secure_backend()

    def test_secure_backend_selects_os_keychain_from_chain(self) -> None:
        from keyring.backends.chainer import ChainerBackend

        secure = type(
            "Secure", (), {"__module__": "keyring.backends.macOS", "priority": 1}
        )()
        chain = Mock(spec=ChainerBackend)
        chain.backends = [Mock(), secure]
        with patch("linear.auth.keyring.get_keyring", return_value=chain):
            self.assertIs(_secure_backend(), secure)

    def test_concurrent_commands_refresh_only_once(self) -> None:
        auth.save_credentials(self._credentials(expired=True))
        tokens: list[str] = []
        failures: list[Exception] = []

        def obtain() -> None:
            try:
                tokens.append(auth.get_access_token())
            except Exception as exc:
                failures.append(exc)

        with patch(
            "linear.auth.httpx.post", return_value=self._token_response()
        ) as post:
            workers = [threading.Thread(target=obtain) for _ in range(3)]
            for worker in workers:
                worker.start()
            for worker in workers:
                worker.join(timeout=5)
            self.assertFalse(any(worker.is_alive() for worker in workers))
            post.assert_called_once()
        self.assertFalse(failures, failures)
        self.assertEqual(tokens, ["rotated-access"] * 3)

    def test_refresh_network_and_storage_errors(self) -> None:
        auth.save_credentials(self._credentials(expired=True))
        original = self.record
        with patch("linear.auth.httpx.post", side_effect=httpx.ConnectError("private")):
            with self.assertRaisesRegex(auth.AuthError, "Cannot reach Linear"):
                auth.get_access_token()
        self.assertEqual(self.record, original)
        with patch("linear.auth.httpx.post", return_value=self._token_response()):
            self.backend.set_password.side_effect = RuntimeError("private")
            with self.assertRaisesRegex(auth.AuthError, "Cannot save"):
                auth.get_access_token()
        self.assertEqual(self.record, original)

    def test_refresh_failures_preserve_saved_login_and_redact_errors(self) -> None:
        auth.save_credentials(self._credentials(expired=True))
        old = self.record
        for response in (
            httpx.Response(400, text="secret-refresh"),
            httpx.Response(200, json={}),
            self._token_response(expires_in=-1),
            self._token_response(token_type="unknown"),
            self._token_response(refresh_token=""),
        ):
            with patch("linear.auth.httpx.post", return_value=response):
                with self.assertRaises(auth.AuthError) as caught:
                    auth.get_access_token()
                self.assertNotIn("secret-refresh", str(caught.exception))
                self.assertEqual(self.record, old)

    def test_api_key_precedence_and_oauth_header(self) -> None:
        with patch("linear.api.client.get_access_token", return_value="oauth") as token:
            with patch.dict(os.environ, {"LINEAR_API_KEY": "environment-key"}):
                self.assertEqual(
                    LinearClient().headers["Authorization"], "environment-key"
                )
                self.assertEqual(
                    LinearClient("explicit").headers["Authorization"], "explicit"
                )
                self.assertEqual(
                    LinearClient(access_token="new").headers["Authorization"],
                    "Bearer new",
                )
                token.assert_not_called()
            self.assertEqual(LinearClient().headers["Authorization"], "Bearer oauth")
        with self.assertRaises(LinearClientError):
            LinearClient(api_key="key", access_token="token")

    def test_long_lived_client_refreshes_without_replaying_mutations(self) -> None:
        auth.save_credentials(self._credentials())
        client = LinearClient()
        auth.save_credentials(self._credentials(expired=True))
        response = httpx.Response(401, request=httpx.Request("POST", client.API_URL))
        with (
            patch("linear.auth.httpx.post", return_value=self._token_response()),
            patch("httpx.Client.post", return_value=response) as post,
        ):
            with self.assertRaisesRegex(LinearClientError, "linear login"):
                client.query("mutation { example }")
            self.assertEqual(post.call_count, 1)
            self.assertEqual(
                post.call_args.kwargs["headers"]["Authorization"],
                "Bearer rotated-access",
            )

    def test_logout_removes_tokens_even_offline_or_corrupt(self) -> None:
        for raw in (self._credentials().model_dump_json(), "broken"):
            self.record = raw
            with patch(
                "linear.auth.httpx.post", side_effect=httpx.ConnectError("offline")
            ):
                self.assertEqual(auth.logout(), (True, False))
            self.assertIsNone(self.record)
        self.assertEqual(auth.logout(), (False, False))

    def test_logout_revokes_refresh_token(self) -> None:
        auth.save_credentials(self._credentials())
        with patch("linear.auth.httpx.post", return_value=httpx.Response(200)) as post:
            self.assertEqual(auth.logout(), (True, True))
        self.assertEqual(
            post.call_args.kwargs["data"],
            {
                "token": "secret-refresh",
                "token_type_hint": "refresh_token",
            },
        )

    def _browser_flow(
        self, *, denied: bool = False
    ) -> tuple[auth.Credentials | None, str]:
        server_class = auth._CallbackServer
        servers: list[auth._CallbackServer] = []
        workers: list[threading.Thread] = []
        urls: list[str] = []
        statuses: list[int] = []
        failures: list[Exception] = []

        def make_server(address: tuple[str, int], handler: Any) -> auth._CallbackServer:
            self.assertEqual(address, ("127.0.0.1", 8765))
            server = server_class(("127.0.0.1", 0), handler)
            servers.append(server)
            return server

        def open_browser(url: str) -> bool:
            params = parse_qs(urlsplit(url).query)
            state = params["state"][0]

            def send_callbacks() -> None:
                try:
                    paths = [
                        "/favicon.ico",
                        "/oauth/callback?code=stolen&state=wrong",
                        "/oauth/callback?"
                        + urlencode({"code": "stolen", "state": "☃"}),
                        "/oauth/callback?" + urlencode({"state": state}),
                        "/oauth/callback?"
                        + urlencode(
                            {
                                "state": state,
                                **(
                                    {"error": "access_denied"}
                                    if denied
                                    else {"code": "valid-code"}
                                ),
                            }
                        ),
                    ]
                    for path in paths:
                        connection = http.client.HTTPConnection(
                            "127.0.0.1", servers[0].server_port, timeout=3
                        )
                        try:
                            connection.request("GET", path)
                            response = connection.getresponse()
                            statuses.append(response.status)
                            response.read()
                        finally:
                            connection.close()
                except Exception as exc:
                    failures.append(exc)

            worker = threading.Thread(target=send_callbacks)
            workers.append(worker)
            worker.start()
            return True

        with (
            patch("linear.auth._CallbackServer", side_effect=make_server),
            patch("linear.auth.webbrowser.open", side_effect=open_browser),
            patch(
                "linear.auth.httpx.post", return_value=self._token_response()
            ) as post,
        ):
            credentials = None
            try:
                if denied:
                    with self.assertRaisesRegex(auth.AuthError, "denied"):
                        auth.browser_login(urls.append, timeout=5)
                    post.assert_not_called()
                else:
                    credentials = auth.browser_login(urls.append, timeout=5)
                    data = post.call_args.kwargs["data"]
                    self.assertNotIn("client_secret", data)
                    self.assertEqual(data["code"], "valid-code")
                    expected = (
                        base64.urlsafe_b64encode(
                            hashlib.sha256(data["code_verifier"].encode()).digest()
                        )
                        .rstrip(b"=")
                        .decode()
                    )
                    self.assertEqual(
                        parse_qs(urlsplit(urls[0]).query)["code_challenge"], [expected]
                    )
            finally:
                for worker in workers:
                    worker.join(timeout=5)
            self.assertFalse(failures, failures)
            self.assertEqual(statuses, [404, 400, 400, 400, 400 if denied else 200])
        return credentials, urls[0]

    def test_browser_pkce_and_callback_validation(self) -> None:
        credentials, url = self._browser_flow()
        self.assertIsNotNone(credentials)
        params = parse_qs(urlsplit(url).query)
        self.assertEqual(params["client_id"], [auth.CLIENT_ID])
        self.assertEqual(params["redirect_uri"], [auth.REDIRECT_URI])
        self.assertEqual(params["code_challenge_method"], ["S256"])
        self.assertEqual(params["scope"], ["read,write"])
        self.assertEqual(params["actor"], ["user"])
        self.assertIsNone(self.record)  # Browser flow doesn't save unvalidated tokens.

    def test_browser_denial(self) -> None:
        self._browser_flow(denied=True)

    def test_callback_timeout_and_port_conflict(self) -> None:
        with patch("linear.auth._CallbackServer", side_effect=OSError("in use")):
            with self.assertRaisesRegex(auth.AuthError, "8765"):
                auth.browser_login(lambda _: None)
        server = Mock()
        server.__enter__ = Mock(return_value=server)
        server.__exit__ = Mock()
        with (
            patch("linear.auth._CallbackServer", return_value=server),
            patch("linear.auth.webbrowser.open", return_value=False),
            patch("linear.auth.httpx.post") as post,
        ):
            with self.assertRaisesRegex(auth.AuthError, "timed out"):
                auth.browser_login(lambda _: None, timeout=0)
            post.assert_not_called()
            server.__exit__.assert_called_once()

    def test_cli_login_validates_candidate_despite_env_override(self) -> None:
        viewer = {"id": "user-id", "name": "Colton", "email": "me@example.com"}
        credentials = self._credentials()
        with (
            patch.dict(os.environ, {"LINEAR_API_KEY": "env-key"}),
            patch("linear.commands.auth.browser_login", return_value=credentials),
            patch("linear.commands.auth.LinearClient") as client,
        ):
            client.return_value.get_viewer.return_value = {"viewer": viewer}
            result = self.runner.invoke(app, ["login"])
            self.assertEqual(result.exit_code, 0, result.output)
            client.assert_called_once_with(access_token=credentials.access_token)
            self.assertIn("overrides", result.output)
            self.assertNotIn("secret", result.output)
            self.assertIsNotNone(self.record)

    def test_failed_login_preserves_previous_credentials(self) -> None:
        auth.save_credentials(self._credentials())
        old = self.record
        with (
            patch(
                "linear.commands.auth.browser_login", return_value=self._credentials()
            ),
            patch(
                "linear.commands.auth.LinearClient",
                side_effect=LinearClientError("Invalid login"),
            ),
        ):
            result = self.runner.invoke(app, ["login"])
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(self.record, old)

    def test_cli_status_json_and_logout_override_warning(self) -> None:
        with patch("linear.commands.auth.LinearClient") as client:
            client.return_value.get_viewer.return_value = {
                "viewer": {"id": "id", "name": "Colton", "email": "me@example.com"}
            }
            result = self.runner.invoke(app, ["auth", "status", "--format", "json"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertTrue(json.loads(result.stdout)["authenticated"])
            self.assertNotIn("secret", result.output)
        result = self.runner.invoke(app, ["auth", "status", "--format", "json"])
        self.assertEqual(result.exit_code, 1)
        self.assertFalse(json.loads(result.stdout)["authenticated"])
        with patch.dict(os.environ, {"LINEAR_API_KEY": "env-key"}):
            result = self.runner.invoke(app, ["logout"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("still set", result.output)
