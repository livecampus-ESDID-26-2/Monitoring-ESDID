# Fiche de révision — Module Monitoring

Synthèse rapide des concepts (TP1 → TP5).  
Statut : **TP1 ✅** · **TP2 ✅** · TP3–TP5 à venir.

---

## 🏗️ Modèle pull Prometheus (TP1)

Prometheus **interroge** périodiquement les cibles (`scrape_interval: 15s`) sur `/metrics`.  
Les exporters **exposent** les métriques ; ils n’envoient rien d’eux-mêmes (≠ push).

| Type | Sens | Exemple |
|------|------|---------|
| `counter` | Cumul (ne redescend jamais) | `node_cpu_seconds_total` |
| `gauge` | Instantané (monte/descend) | `node_memory_MemAvailable_bytes`, `node_filesystem_avail_bytes` |
| `histogram` / `summary` | Distributions / quantiles | latences |

**PromQL CPU (%) :**
```promql
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)
```
- `rate(...[1m])` → part de temps idle sur la fenêtre  
- `100 - …` → % d’occupation  
⚠️ Une fenêtre trop longue (ex. `[5m]`) dilue un `stress` court → l’alerte ne part pas.

**Fichiers / ports utiles :**

| Élément | Détail |
|---------|--------|
| Config | `prometheus/prometheus.yml` |
| Node Exporter | `:9100` (systemd sur l’hôte) |
| Prometheus | `:9090` — Targets, Graph, Alerts |
| Accès hôte depuis Docker | `host.docker.internal` + `--add-host=host-gateway` |

---

## 🎨 Visualisation Grafana (TP1)

- Datasource = Prometheus (`http://<ip>:9090`)
- Dashboard communautaire **Node Exporter Full** (id **1860**)
- Dashboard métier **Vue Astreinte** : jauge CPU (seuils vert &lt;70 / orange &lt;90 / rouge ≥90), disque `/`, réseau, uptime (`stat`)
- Login défaut : `admin` / `admin` → à changer

**Panels d’astreinte prioritaires :** CPU, RAM disponible, espace disque `/`.

---

## 🔧 Alerting Alertmanager + Discord (TP2)

### Chaîne

```
Règles (alert_rules.yml)
    → Prometheus évalue (Inactive → Pending → Firing)
        → Alertmanager (:9093)
            → webhook → relay.py (:5000)
                → Discord
```

### Règles mises en place

| Alerte | Sévérité | Idée |
|--------|----------|------|
| `CPUEleve` | warning | CPU &gt; 85 % pendant `for: 1m` |
| `DisqueCritique` | critical | &lt; 10 % libre sur `/` |
| `InstanceDown` | critical | `up == 0` |

États Prometheus : **Inactive** → **Pending** (condition vraie, `for` pas écoulé) → **Firing**.

### Concepts Alertmanager

| Concept | Rôle |
|---------|------|
| `route` / `receiver` | Qui reçoit quoi (warning vs critical) |
| `group_wait` | Attente avant 1ʳᵉ notif (regrouper) |
| `repeat_interval` | Resoumission si toujours active |
| `send_resolved: true` | Notifie aussi le retour à la normale |
| `resolve_timeout` | Délai avant de considérer l’alerte résolue côté AM (lab : 30 s) |
| **`inhibit_rules`** | Critical inhibe warning **même `instance`** → moins de bruit |
| **Silence** | Mute temporaire tracé (`Creator` + `Comment`) — audit SOC |

### Relais Discord (`relay.py`)

- Alertmanager envoie du JSON Alertmanager (pas le format Discord natif) → besoin d’un relais
- Discord exige souvent un header **`User-Agent`** sinon **403**
- Secrets dans `.env` (`DISCORD_WEBHOOK_URL`) — **jamais** committer
- Test charge : `stress --cpu 2 --timeout 180` puis `pkill stress`

**Silence ≠ mute Discord client :** centralisé, horodaté, justifiable en post-incident.

---

## 🔐 SNMP & sécurité système (TP3–TP4)

- **SNMP** : équipements sans agent Prometheus (OID / MIB)
- **SNMPv3** : `noAuthNoPriv` → `authNoPriv` → `authPriv`
- **auditd** : règles persistantes dans `/etc/audit/rules.d/` (`auditctl` seul = volatile)
- **Fail2ban** : ban IP après N échecs SSH
- **Scripts** : `sudo_watch.py`, dérive NTP / quotas disque

---

## 🚀 Disponibilité & SLA (TP5)

- **Uptime Kuma** : moniteurs externes (HTTP, TCP, Ping) ≠ métriques internes Prometheus
- SLA **99,9 %** ≈ **43 min 50 s** d’indispo / mois max
- Page de statut publique ≠ dashboard d’astreinte (masquer IPs, détails internes)
- Rapports d’incident en **UTC**

---

## Chaîne complète

```
Node Exporter (:9100)
        ↓ scrape
   Prometheus (:9090) ──→ Grafana (:3000)
        │
        └── règles ──→ Alertmanager (:9093)
                            ↓
                       relay.py (:5000) ──→ Discord

(+ SNMP → MRTG / LibreNMS | + auditd / Fail2ban | + Uptime Kuma)
```

## Ports à retenir

| Service | Port |
|---------|------|
| Prometheus | 9090 |
| Grafana | 3000 |
| Node Exporter | 9100 |
| Alertmanager | 9093 |
| Relais Discord | 5000 |
| LibreNMS | 8000 |
| Uptime Kuma | 3001 |
