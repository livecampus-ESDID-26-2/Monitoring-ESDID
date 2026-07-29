#!/usr/bin/env python3
"""Dérive d'horloge NTP + quotas disque /home (TP4)."""

import os
import re
import subprocess

SEUIL_DERIVE_SECONDES = 2
SEUIL_QUOTA_MO = 5000
REPERTOIRES_UTILISATEURS = "/home"


def verifie_derive_horloge():
    try:
        sortie = subprocess.run(
            ["ntpdate", "-q", "0.fr.pool.ntp.org"],
            capture_output=True,
            text=True,
            timeout=30,
        ).stdout
    except FileNotFoundError:
        # Fallback si ntpdate absent (Debian moderne)
        sortie = subprocess.run(
            ["chronyc", "tracking"],
            capture_output=True,
            text=True,
            timeout=30,
        ).stdout
        correspondance = re.search(r"System time\s*:\s*([\-0-9.]+)", sortie)
        if correspondance:
            derive = abs(float(correspondance.group(1)))
            if derive > SEUIL_DERIVE_SECONDES:
                print(f"[ALERTE] Dérive horloge de {derive:.2f}s détectée, vérifier NTP/chrony")
            else:
                print(f"[OK] Dérive horloge : {derive:.2f}s")
            return
        print("[WARN] Impossible de mesurer la dérive (ntpdate/chronyc)")
        return

    correspondance = re.search(r"offset ([\-0-9.]+)", sortie)
    if correspondance:
        derive = abs(float(correspondance.group(1)))
        if derive > SEUIL_DERIVE_SECONDES:
            print(f"[ALERTE] Dérive horloge de {derive:.2f}s détectée, vérifier le service NTP local")
        else:
            print(f"[OK] Dérive horloge : {derive:.2f}s")
    else:
        print(f"[WARN] Sortie ntpdate non parsée:\n{sortie}")


def verifie_quotas_utilisateurs():
    if not os.path.isdir(REPERTOIRES_UTILISATEURS):
        print(f"[WARN] {REPERTOIRES_UTILISATEURS} introuvable")
        return
    for utilisateur in os.listdir(REPERTOIRES_UTILISATEURS):
        chemin = os.path.join(REPERTOIRES_UTILISATEURS, utilisateur)
        if os.path.isdir(chemin):
            taille = subprocess.run(
                ["du", "-sm", chemin], capture_output=True, text=True
            ).stdout.split()[0]
            if int(taille) > SEUIL_QUOTA_MO:
                print(f"[ALERTE] {utilisateur} dépasse le quota : {taille} Mo")
            else:
                print(f"[OK] {utilisateur} : {taille} Mo")


if __name__ == "__main__":
    verifie_derive_horloge()
    verifie_quotas_utilisateurs()
