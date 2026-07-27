# Fiche de révision — Module Monitoring

Synthèse rapide des concepts de la semaine de supervision (TP1 → TP5).

---

## 🏗️ Modèle pull Prometheus

Prometheus **interroge** périodiquement les cibles (`scrape_interval`) sur `/metrics`.  
Les exporters (ex. Node Exporter) **exposent** les métriques ; ils n'envoient rien d'eux-mêmes.

| Type | Sens |
|------|------|
| `counter` | Valeur cumulée (ne redescend jamais) |
| `gauge` | Valeur instantanée (peut monter/descendre) |
| `histogram` / `summary` | Distributions / quantiles |

**PromQL utile :**  
`100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)` → % CPU utilisé.

---

## 🎨 Visualisation Grafana

- Source de données = Prometheus
- Dashboard communautaire **Node Exporter Full** (id **1860**)
- Dashboard métier **Vue Astreinte** : jauge CPU (seuils), disque `/`, réseau, uptime

---

## 🔧 Alerting (Alertmanager)

1. Règles dans `alert_rules.yml` (Prometheus évalue)
2. Alertmanager groupe, route, inhibe, silence
3. Notifications via webhook → Telegram / Discord

**`inhibit_rules`** : une alerte *critical* masque les *warning* de la même instance → moins de bruit.

**Silence** : acquittement temporaire tracé (qui / pourquoi) — indispensable en SOC.

---

## 🔐 SNMP & sécurité système

- **SNMP** : supervision d'équipements sans agent Prometheus (OID / MIB)
- **SNMPv3** : `noAuthNoPriv` → `authNoPriv` → `authPriv` (auth + chiffrement)
- **auditd** : traçabilité fine (`/etc/passwd`, `su`) — règles persistantes dans `rules.d/`
- **Fail2ban** : ban IP après N échecs SSH
- **Scripts maison** : `sudo_watch.py`, dérive NTP / quotas disque

---

## 🚀 Disponibilité & SLA (Uptime Kuma)

- Supervision **externe** (HTTP, TCP, Ping) complémentaire à Prometheus
- SLA 99,9% ≈ **43 min 50 s** d'indispo / mois max
- Page de statut publique ≠ dashboard d'astreinte (masquer IPs, détails internes)
- Rapports d'incident en **UTC** pour éviter les ambiguïtés de fuseaux

---

## Chaîne complète

```
Node Exporter / SNMP / scripts
        ↓
   Prometheus (+ règles)
        ↓
  Grafana | Alertmanager | LibreNMS | Uptime Kuma
        ↓
   Astreinte (IM) + SLA / post-mortem
```
