# Module Monitoring — configs & scripts

Configs Prometheus, Alertmanager, Grafana, SNMP, LibreNMS, auditd, Fail2ban et scripts du module Monitoring (TP1–TP5).

| Dossier / fichier | Rôle |
|-------------------|------|
| `prometheus/` | `prometheus.yml`, `alert_rules.yml` |
| `alertmanager/` | `alertmanager.yml` |
| `grafana/dashboard_import/` | Dashboards JSON (Vue Astreinte, Node Exporter Full) |
| `relay.py` | Relais Alertmanager → Discord |
| `librenms/` | `docker-compose.yml` LibreNMS |
| `snmp/` | `snmpd.conf` |
| `audit/` | Règles auditd |
| `fail2ban/` | `jail.local` |
| `scripts/` | `sudo_watch.py`, `derive_horloge.py` |
| `logs/` | Sortie cron / scripts (gitignoré) |

Docs & captures : [`../docs/`](../docs/)  
Énoncé : [`../docs/cahier_tp_monitoring.md`](../docs/cahier_tp_monitoring.md)
