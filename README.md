# Supervision d'infrastructure — Monitoring & ELK

**École :** LiveCampus - ESDID-26.2  
**Étudiant :** [Antoine MASIA](https://github.com/MasiaAntoine) - Full-Stack Developer  
**Intervenant :** [Tarik LF](https://github.com/TarikLF) - Formateur Cybersécurité & Infrastructures

---

## Structure du dépôt

```
tp-monitoring/
├── README.md
├── .env / .env.example
├── docs/                 # énoncés, réponses, captures, fiche révision
├── monitoring/           # configs & scripts TP Monitoring (TP1–TP5)
└── elk/                  # configs & pipelines stack ELK (à venir)
```

---

## 📝 [Fiche de Révision](docs/fiche-revision.md)

**Pour comprendre rapidement tous les concepts du projet :**

- 🏗️ Modèle pull Prometheus & métriques `/metrics`
- 🎨 Dashboards Grafana (astreinte)
- 🔧 Alertmanager, inhibit rules & silences
- 📡 SNMP, MRTG & LibreNMS
- 🛡️ auditd, Fail2ban & scripts (sudo / horloge)
- 🚀 SLA, Uptime Kuma, status page & rapports d'incident
- 📦 Stack ELK (à venir)

👉 **[Voir la fiche de révision complète](docs/fiche-revision.md)**

---

<div align="center">

<table>
  <tr>
    <td align="center" width="50%">
      <a href="https://github.com/MasiaAntoine">
        <img src="https://avatars.githubusercontent.com/u/115811899?v=4" alt="Antoine MASIA" width="100">
      </a>
      <br/>
      <strong>Antoine MASIA</strong>
      <br/>
      <em>Étudiant</em>
    </td>
    <td align="center" width="50%">
      <a href="https://github.com/TarikLF">
        <img src="https://avatars.githubusercontent.com/u/208114033?v=4" alt="Tarik LF" width="100">
      </a>
      <br/>
      <strong>Tarik LF</strong>
      <br/>
      <em>Intervenant</em>
    </td>
  </tr>
</table>

<br>

<em>Projet réalisé dans le cadre du module "Monitoring"</em>

</div>

---

## Description du Projet

Mise en place d'une **chaîne de supervision complète** : métriques système, visualisation, alerting, SNMP, détection de sécurité et suivi de disponibilité / SLA.

📄 **Énoncés :**
- [cahier_tp_monitoring.md](docs/cahier_tp_monitoring.md) — Module Monitoring (TP1–TP5)
- [cahier_tp_elk.md](docs/cahier_tp_elk.md) — Installation stack ELK 8.x

---

## Travaux pratiques — Monitoring

Configs : [`monitoring/`](monitoring/)

### TP1 — Supervision système (Prometheus, Node Exporter, Grafana)

Collecte des métriques OS via Node Exporter, configuration Prometheus (modèle pull), dashboards Grafana dont une **Vue Astreinte**.

- 📘 [Énoncé](docs/cahier_tp_monitoring.md#tp1--supervision-système-avec-prometheus-node-exporter-et-grafana)
- ✅ [Réponses](docs/reponses_tp1.md)

### TP2 — Alerting temps réel (Alertmanager, Telegram / Discord)

Règles d'alerte Prometheus, Alertmanager (routes, inhibit, silences) et notifications IM via webhook / bot.

- 📘 [Énoncé](docs/cahier_tp_monitoring.md#tp2--alerting-temps-réel-avec-alertmanager-et-notifications-discordtelegram)
- ✅ [Réponses](docs/reponses_tp2.md)

### TP3 — Supervision réseau SNMP (Net-SNMP, LibreNMS, MRTG)

Agent SNMP, interrogation OID/MIB, historisation MRTG et supervision centralisée LibreNMS.

- 📘 [Énoncé](docs/cahier_tp_monitoring.md#tp3--supervision-réseau-via-snmp-avec-net-snmp-librenms-et-mrtg)
- ✅ [Réponses](docs/reponses_tp3.md)

### TP4 — Détection d'intrusions (auditd, Fail2ban, scripts)

Journalisation, surveillance sudo, règles auditd, anti brute-force SSH et scripts de dérive d'horloge / quotas.

- 📘 [Énoncé](docs/cahier_tp_monitoring.md#tp4--détection-dintrusions-et-dérives-système-avec-auditd-fail2ban-et-scripts-maison)
- ✅ [Réponses](docs/reponses_tp4.md)

### TP5 — Disponibilité & SLA (Uptime Kuma)

Moniteurs externes, page de statut, calcul de SLA et rapport d'incident (post-mortem) en anglais.

- 📘 [Énoncé](docs/cahier_tp_monitoring.md#tp5--disponibilité-sla-et-rédaction-de-rapports-dincident-avec-uptime-kuma)
- ✅ [Réponses](docs/reponses_tp5.md)
- 📄 [Rapport d'incident (EN)](docs/incident_report_tp5.md)

---

## Travaux pratiques — ELK

Configs : [`elk/`](elk/)

### Installation stack ELK (Elasticsearch, Logstash, Kibana 8.x)

Dépôt officiel Elastic, config lab (sécurité désactivée), services `systemctl`, pipeline Logstash de test.

- 📘 [Énoncé / guide](docs/cahier_tp_elk.md)
- ✅ [Réponses](docs/reponses_tp_elk.md)
- 📁 [Configs Docker](elk/)
