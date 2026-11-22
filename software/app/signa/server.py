"""HTTP local para a extensão de navegador: só 127.0.0.1, exige X-Signa-Token e Host local
(barra DNS rebinding). Sem CORS: a extensão MV3 tem host_permissions para a porta e não precisa."""
from __future__ import annotations

import hmac
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import store
from .states import NAMES

WEB_SOURCES = {"chatgpt-web", "claude-web", "grok-web"}


def make_handler(token: str, port: int, status_fn):
    allowed_hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _auth(self) -> bool:
            if self.headers.get("Host", "") not in allowed_hosts:
                return False
            return hmac.compare_digest(self.headers.get("X-Signa-Token", ""), token)

        def _send(self, code: int, obj) -> None:
            body = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if not self._auth():
                return self._send(403, {"erro": "token"})
            if self.path == "/v1/status":
                return self._send(200, status_fn())
            self._send(404, {})

        def do_POST(self):
            if not self._auth():
                return self._send(403, {"erro": "token"})
            try:
                n = min(int(self.headers.get("Content-Length", "0")), 4096)
                d = json.loads(self.rfile.read(n) or b"{}")
            except (ValueError, json.JSONDecodeError):
                return self._send(400, {"erro": "json"})
            if self.path == "/v1/ai":
                src = str(d.get("source", ""))
                if src not in WEB_SOURCES:
                    return self._send(400, {"erro": "fonte"})
                sess = str(d.get("session", ""))[:64]
                if d.get("state") == "remove":
                    store.set_ai(src, None, sess)
                    return self._send(200, {"ok": True})
                st = NAMES.get(str(d.get("state", "")))
                if st is None or not st.is_ia:
                    return self._send(400, {"erro": "estado"})
                store.set_ai(src, st, sess)
                return self._send(200, {"ok": True})
            self._send(404, {})

    return H


def serve(port: int, token: str, status_fn) -> ThreadingHTTPServer:
    srv = ThreadingHTTPServer(("127.0.0.1", port), make_handler(token, port, status_fn))
    threading.Thread(target=srv.serve_forever, daemon=True, name="signa-http").start()
    return srv
