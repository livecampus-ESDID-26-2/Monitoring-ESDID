#!/usr/bin/env python3
"""Relais Alertmanager → Discord webhook (stdlib, sans Flask)."""

import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

DISCORD_WEBHOOK = os.environ.get(
    "DISCORD_WEBHOOK_URL",
    "VOTRE_WEBHOOK_DISCORD",
)


def send_discord(content: str) -> None:
    data = json.dumps({"content": content}).encode("utf-8")
    req = urllib.request.Request(
        DISCORD_WEBHOOK,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "tp-monitoring-relay/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        resp.read()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path != "/alert":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            data = {}
        for a in data.get("alerts", []):
            statut = a.get("status", "unknown").upper()
            nom = a.get("labels", {}).get("alertname", "inconnue")
            instance = a.get("labels", {}).get("instance", "?")
            severity = a.get("labels", {}).get("severity", "?")
            description = a.get("annotations", {}).get("description", "")
            emoji = "🔴" if statut == "FIRING" else "🟢"
            content = (
                f"{emoji} **[{statut}] {nom}** ({severity})\n"
                f"Instance : `{instance}`\n"
                f"{description}"
            )
            try:
                send_discord(content)
                print(f"Envoyé: [{statut}] {nom}")
            except Exception as exc:
                print(f"Erreur Discord: {exc}")
        self.send_response(200)
        self.end_headers()

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    if "VOTRE_WEBHOOK" in DISCORD_WEBHOOK or not DISCORD_WEBHOOK:
        print("⚠️  Configure DISCORD_WEBHOOK_URL dans .env avant de lancer.")
        raise SystemExit(1)
    print("Relais Discord sur http://0.0.0.0:5000/alert")
    HTTPServer(("0.0.0.0", 5000), Handler).serve_forever()
