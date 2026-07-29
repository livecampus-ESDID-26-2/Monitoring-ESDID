# Fiche de révision — Module Monitoring

Synthèse rapide des concepts (TP1 → TP5).  
Statut : **TP1 ✅** · **TP2 ✅** · **TP3 ✅** · **TP4 ✅** · **TP5 ✅**

Énoncé : [`cahier_tp_monitoring.md`](cahier_tp_monitoring.md)

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
| Config | `monitoring/prometheus/prometheus.yml` |
| Relais Discord | `monitoring/relay.py` |
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

## 📡 Supervision SNMP — MRTG / LibreNMS (TP3)

Équipements **sans** agent Prometheus → interrogation **SNMP** (OID / MIB).

| Concept | À retenir |
|---------|-----------|
| SNMPv2c | Communauté en clair (`tp-master-ro`) — OK lab, pas prod |
| SNMPv3 | `noAuthNoPriv` → `authNoPriv` → **`authPriv`** (recommandé prod) |
| OID utiles | `sysName` `1.3.6.1.2.1.1.5.0` ; `hrProcessorLoad` `1.3.6.1.2.1.25.3.3.1.2` |
| Inventaire auto | LibreNMS découvre CPU, interfaces, OS via snmpwalk (pas saisi à la main) |
| MRTG | Graphiques trafic interface (`ens18`) |
| Alerte | Port ≥ **80 %** (`macros.port_usage_perc`) |

**Stack lab :** `snmpd` sur la VM + LibreNMS en **Docker Compose** (`:8000`).  
Transport Discord LibreNMS : souvent bloqué par SSL lab → règle native quand même livrable.

Fichier : `monitoring/snmp/snmpd.conf` (communautés adaptées au réseau lab + Docker).

---

## 🛡️ Détection & dérives système (TP4)

| Outil | Rôle |
|-------|------|
| `journalctl --list-boots` | Liste des redémarrages (ex. 7 derniers jours) |
| `monitoring/scripts/sudo_watch.py` | Alerte si `sudo` hors whitelist ; option Discord via `.env` |
| **auditd** | Règles dans `/etc/audit/rules.d/` (`auditctl` seul = volatile au reboot) |
| **Fail2ban** | Ban IP après échecs SSH (`monitoring/fail2ban/jail.local`) |
| `monitoring/scripts/derive_horloge.py` | Surveille la dérive NTP ; cron toutes les **30 min** |

**Pourquoi la dérive d’horloge est un risque sécu :**

1. Corrélation de logs faussée entre machines  
2. Certificats TLS invalides (`NotBefore` / `NotAfter`)  
3. Kerberos / JWT / MFA basés sur le temps cassés  

Fichiers : `monitoring/audit/audit.rules`, `monitoring/fail2ban/jail.local`, `monitoring/scripts/`.

---

## 🚀 Disponibilité, SLA & incidents (TP5)

**Uptime Kuma** (`:3001`) = supervision **externe** (blackbox) ≠ métriques internes Prometheus.

| Sonde | Type | Cible typique |
|-------|------|----------------|
| HTTP-Apache | HTTP | `http://10.31.10.41` |
| Ping-Gateway | Ping | gateway / IP joignable (lab) |
| TCP-SSH | TCP | `10.31.10.41:22` |

### SLA

- Mois 30 j = **43 200 min**
- Budget **99,9 %** ≈ **43,2 min** d’indispo max
- Exemple cahier : 127 min → **≈ 99,706 %** → engagement **non respecté**

### Status page vs dashboard d’astreinte

| Public (clients) | Interne (Ops) |
|------------------|---------------|
| Up/Down + message d’incident | Latence, erreurs, config, runbooks |
| Transparence contractuelle | Diagnostic / action |

**Masquer au public :** IPs internes, ports, erreurs brutes, webhooks, credentials.

### Incident

- Notif Discord + panne simulée (`iptables` DROP TCP/22)
- Rapport post-mortem en **anglais** (`incident_report_tp5.md`)
- Timeline en **UTC** (évite confusion Paris vs New York sur « 10:33 »)

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

snmpd ──→ MRTG / LibreNMS (:8000)
auditd + Fail2ban + scripts (sudo / horloge)
Uptime Kuma (:3001) ──→ Discord + status page + SLA / post-mortem
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
| Elasticsearch *(ELK à venir)* | 9200 |
| Kibana *(ELK à venir)* | 5601 |
| Logstash *(ELK à venir)* | 5044 |

---

## Prochain module — ELK

Guide d’install : [`cahier_tp_elk.md`](cahier_tp_elk.md)  
Configs Docker : `elk/docker-compose.yml` (ES `:9200`, Kibana `:5601`, Logstash `:5044`)  
Réponses : [`reponses_tp_elk.md`](reponses_tp_elk.md)

| Composant | Rôle |
|-----------|------|
| **Elasticsearch** | Stocke / indexe les logs |
| **Logstash** | Collecte + transforme → ES |
| **Kibana** | UI web sur les données ES |

Lab : `xpack.security.enabled: false` — **jamais** en prod exposée.
