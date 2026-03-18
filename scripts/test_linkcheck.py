from __future__ import annotations

import os
import socket
import subprocess
import sys
import threading
import time
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


SCRIPT = Path(__file__).with_name("linkcheck.py")


def run_cli(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class LinkHandler(BaseHTTPRequestHandler):
    def do_HEAD(self) -> None:  # noqa: N802
        if self.path == "/ok":
            self.send_response(200)
        else:
            self.send_response(404)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return


class HangingServer:
    def __init__(self) -> None:
        self.port = free_port()
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._ready = threading.Event()
        self._stop = threading.Event()

    def __enter__(self) -> "HangingServer":
        self._thread.start()
        self._ready.wait(timeout=2)
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self._stop.set()
        try:
            with socket.create_connection(("127.0.0.1", self.port), timeout=0.2):
                pass
        except OSError:
            pass
        self._thread.join(timeout=2)

    def _serve(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("127.0.0.1", self.port))
            sock.listen()
            self._ready.set()
            while not self._stop.is_set():
                try:
                    sock.settimeout(0.2)
                    conn, _ = sock.accept()
                except socket.timeout:
                    continue
                threading.Thread(target=self._hang_connection, args=(conn,), daemon=True).start()

    def _hang_connection(self, conn: socket.socket) -> None:
        with conn:
            while not self._stop.is_set():
                time.sleep(0.05)


def test_reports_ok_and_broken_links(tmp_path: Path) -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), LinkHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        markdown = tmp_path / "README.md"
        markdown.write_text(
            "\n".join(
                [
                    f"[ok](http://127.0.0.1:{server.server_port}/ok)",
                    f"[missing](<http://127.0.0.1:{server.server_port}/missing>)",
                ]
            ),
            encoding="utf-8",
        )

        result = run_cli(str(markdown))

        assert result.returncode == 1
        assert result.stdout.splitlines() == [
            f"✅ OK http://127.0.0.1:{server.server_port}/ok",
            f"❌ BROKEN http://127.0.0.1:{server.server_port}/missing",
        ]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_reports_timeout_without_marking_broken(tmp_path: Path) -> None:
    with HangingServer() as server:
        markdown = tmp_path / "README.md"
        markdown.write_text(
            f"[slow](http://127.0.0.1:{server.port}/slow)\n",
            encoding="utf-8",
        )
        env = os.environ.copy()
        env["LINKCHECK_TIMEOUT"] = "0.2"

        result = run_cli(str(markdown), env=env)

        assert result.returncode == 0
        assert result.stdout.splitlines() == [
            f"⚠️ TIMEOUT http://127.0.0.1:{server.port}/slow",
        ]


def test_rejects_missing_file() -> None:
    result = run_cli("missing.md")

    assert result.returncode != 0
    assert "File not found: missing.md" in result.stderr
