#!/usr/bin/env python3
"""Surveillance des commandes sudo hors whitelist (TP4)."""

import json
import os
import time
import urllib.request

WHITELIST = {"admin", "deploy"}
# Debian classique : /var/log/auth.log (nécessite rsyslog)
# Fallback possible : journalctl -f SYSLOG_FACILITY=4 / _COMM=sudo
LOGFILE = os.environ.get("AUTH_LOGFILE", "/var/log/auth.log")

# Optionnel : même webhook Discord que le TP2 (via .env)
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK_URL", "")


def alerte(utilisateur: str, ligne: str) -> None:
    msg = (
        f"[ALERTE] Commande sudo par utilisateur non autorisé : {utilisateur}\n"
        f"  -> {ligne.strip()}"
    )
    print(msg)
    if DISCORD_WEBHOOK and "VOTRE_WEBHOOK" not in DISCORD_WEBHOOK:
        data = json.dumps({"content": f"🛡️ {msg}"}).encode("utf-8")
        req = urllib.request.Request(
            DISCORD_WEBHOOK,
            data=data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "tp-monitoring-sudo-watch/1.0",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp.read()
        except Exception as exc:
            print(f"(Discord non envoyé: {exc})")


def surveille():
    with open(LOGFILE, "r") as f:
        f.seek(0, 2)  # se positionner à la fin du fichier
        while True:
            ligne = f.readline()
            if not ligne:
                time.sleep(1)
                continue
            if "sudo:" in ligne and "COMMAND=" in ligne:
                utilisateur = ligne.split("sudo:")[1].strip().split(" ")[0]
                if utilisateur not in WHITELIST:
                    alerte(utilisateur, ligne)


if __name__ == "__main__":
    print(f"Surveillance de {LOGFILE} (whitelist={WHITELIST})")
    surveille()
