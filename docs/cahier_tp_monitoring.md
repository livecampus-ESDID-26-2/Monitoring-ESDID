# Module Monitoring — Cahier de Travaux Pratiques

**Master Cybersécurité & Infrastructures — Semaine de supervision**

| | |
|---|---|
| **Pré-requis** | Infrastructures Linux/Windows, notions de Python, PowerShell et Shell |
| **Modalité** | Travail individuel ou en binôme, restitution en fin de séance |
| **Environnement** | Machines virtuelles Linux (Debian/Ubuntu) ou conteneurs Docker, accès root/sudo requis |
| **Évaluation** | Exercices notés + mise en place d'un système de suivi et d'alertes fonctionnel en contrôle continu |

Ce cahier regroupe cinq travaux pratiques indépendants, chacun mobilisant des outils open source différents, couvrant l'ensemble du périmètre du module : supervision graphique, alerting temps réel, supervision réseau via SNMP, détection d'anomalies de sécurité système, et gestion de SLA / rédaction de rapports d'incident.

Chaque TP est conçu pour être réalisé en autonomie à partir d'un énoncé. Les corrigés ne sont pas fournis dans ce document et seront distribués séance par séance.

---

## Sommaire

- [TP1 — Supervision système avec Prometheus, Node Exporter et Grafana](#tp1--supervision-système-avec-prometheus-node-exporter-et-grafana)
- [TP2 — Alerting temps réel avec Alertmanager et notifications Discord/Telegram](#tp2--alerting-temps-réel-avec-alertmanager-et-notifications-discordtelegram)
- [TP3 — Supervision réseau via SNMP avec Net-SNMP, LibreNMS et MRTG](#tp3--supervision-réseau-via-snmp-avec-net-snmp-librenms-et-mrtg)
- [TP4 — Détection d'intrusions et dérives système avec auditd, Fail2ban et scripts maison](#tp4--détection-dintrusions-et-dérives-système-avec-auditd-fail2ban-et-scripts-maison)
- [TP5 — Disponibilité, SLA et rédaction de rapports d'incident avec Uptime Kuma](#tp5--disponibilité-sla-et-rédaction-de-rapports-dincident-avec-uptime-kuma)

---

# TP1 — Supervision système avec Prometheus, Node Exporter et Grafana

| | |
|---|---|
| **Durée estimée** | 6 heures |
| **Outils** | Prometheus, Node Exporter, Grafana, Docker / Docker Compose |
| **Compétences visées** | Superviser, mesurer les performances et la disponibilité de l'infrastructure et en présenter les résultats |
| **Livrable** | Dashboard Grafana fonctionnel + capture d'écran + fichier `prometheus.yml` commenté |

## 1. Contexte

Vous intervenez comme alternant chez un hébergeur qui souhaite mettre en place une supervision centralisée de son parc de serveurs Linux. La direction technique a retenu la stack Prometheus / Grafana pour sa gratuité, sa robustesse et l'étendue de son écosystème d'exporters. Vous devez livrer un prototype fonctionnel sur une machine de test avant un déploiement à plus grande échelle.

## 2. Objectifs pédagogiques

- Comprendre le modèle pull de Prometheus et le format des métriques exposées en `/metrics`
- Installer et configurer un Node Exporter pour exposer les métriques systèmes (cpu, ram, disque, réseau)
- Écrire un fichier de configuration `prometheus.yml` avec plusieurs cibles (targets)
- Construire un dashboard Grafana exploitable par une équipe d'astreinte

## 3. Préparation de l'environnement

Sur votre VM Debian/Ubuntu, créez l'arborescence de travail suivante :

```bash
mkdir -p ~/tp-monitoring/prometheus
mkdir -p ~/tp-monitoring/grafana
cd ~/tp-monitoring
```

Vous utiliserez Docker Compose afin de pouvoir reproduire l'environnement facilement. Vérifiez que Docker est installé :

```bash
docker --version
docker compose version
```

## 4. Étape 1 — Déploiement du Node Exporter

Le Node Exporter expose les métriques matérielles et OS d'une machine Linux sur le port 9100. Installez-le directement sur l'hôte (et non en conteneur) afin qu'il remonte les métriques réelles de la VM :

```bash
cd /tmp
wget https://github.com/prometheus/node_exporter/releases/download/v1.8.2/node_exporter-1.8.2.linux-amd64.tar.gz
tar xvfz node_exporter-1.8.2.linux-amd64.tar.gz
sudo mv node_exporter-1.8.2.linux-amd64/node_exporter /usr/local/bin/
node_exporter --version
```

Créez ensuite un service systemd dédié afin que le Node Exporter démarre automatiquement :

```bash
sudo useradd --no-create-home --shell /usr/sbin/nologin node_exporter
sudo tee /etc/systemd/system/node_exporter.service <<'EOF'
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
ExecStart=/usr/local/bin/node_exporter
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now node_exporter
curl http://localhost:9100/metrics | head -n 20
```

**Question 1 :**  
Identifiez dans la sortie de `/metrics` trois familles de métriques liées au CPU, à la mémoire et au système de fichiers. Pour chacune, indiquez son nom exact et le type Prometheus associé (counter, gauge, histogram, summary).

## 5. Étape 2 — Installation et configuration de Prometheus

Créez le fichier de configuration `~/tp-monitoring/prometheus/prometheus.yml` :

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node_exporter'
    static_configs:
      - targets: ['host.docker.internal:9100']
        labels:
          environment: 'tp-master'
          role: 'web-server'
```

Lancez Prometheus via Docker :

```bash
docker run -d --name prometheus \
  --add-host=host.docker.internal:host-gateway \
  -p 9090:9090 \
  -v ~/tp-monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

Rendez-vous sur `http://<ip_vm>:9090/targets` et vérifiez que la cible `node_exporter` apparaît à l'état **UP**.

**Question 2 :**  
Dans l'interface Prometheus (onglet Graph), exécutez la requête PromQL suivante et expliquez ce qu'elle calcule :

```promql
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

## 6. Étape 3 — Mise en place de Grafana

```bash
docker run -d --name grafana -p 3000:3000 grafana/grafana-oss
```

Connectez-vous sur `http://<ip_vm>:3000` (identifiants par défaut `admin`/`admin`), ajoutez Prometheus comme source de données (URL : `http://<ip_vm>:9090`), puis importez le dashboard communautaire officiel **Node Exporter Full** (identifiant **1860**) depuis le menu Import.

**Question 3 :**  
Le dashboard importé contient une vingtaine de panels. Sélectionnez-en trois que vous jugez prioritaires pour une équipe d'astreinte de nuit, et justifiez votre choix en deux ou trois phrases par panel.

## 7. Étape 4 — Personnalisation

Créez un nouveau dashboard **Vue Astreinte** contenant au minimum :

- Une jauge (gauge) du taux d'utilisation CPU avec seuils de couleur (vert < 70%, orange < 90%, rouge ≥ 90%)
- Un graphique de l'espace disque disponible sur la partition racine
- Un graphique du trafic réseau entrant/sortant sur l'interface principale
- Un panel de type **stat** affichant l'uptime du serveur

## 8. Livrables attendus

- Le fichier `prometheus.yml` finalisé et commenté
- Une capture d'écran du dashboard **Vue Astreinte**
- Les réponses aux questions 1 à 3 dans un fichier `reponses_tp1.md`

## 9. Pour aller plus loin (optionnel)

Ajoutez un second exporter au choix (`mysqld_exporter`, `blackbox_exporter` pour tester la disponibilité HTTP d'un site, ou `cadvisor` pour superviser des conteneurs Docker) et intégrez-le à votre Prometheus.

---

# TP2 — Alerting temps réel avec Alertmanager et notifications Discord/Telegram

| | |
|---|---|
| **Durée estimée** | 6 heures |
| **Outils** | Prometheus, Alertmanager, un bot Telegram ou un webhook Discord, Python (optionnel) |
| **Compétences visées** | Superviser l'infrastructure ; mise en place d'alertes (mail, sms, IM, pagerduty) |
| **Pré-requis** | TP1 réalisé (stack Prometheus/Grafana opérationnelle) |

## 1. Contexte

La supervision mise en place au TP1 permet de visualiser l'état du parc mais ne réveille personne en cas de panne à 3h du matin. Votre mission est de brancher un système d'alerting capable de notifier automatiquement l'équipe d'astreinte sur une messagerie instantanée dès qu'un seuil critique est franchi, avec un système d'acquittement des alertes.

## 2. Étape 1 — Installation d'Alertmanager

```bash
docker run -d --name alertmanager \
  -p 9093:9093 \
  -v ~/tp-monitoring/alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml \
  prom/alertmanager
```

## 3. Étape 2 — Création des règles d'alerte Prometheus

Créez `~/tp-monitoring/prometheus/alert_rules.yml` :

```yaml
groups:
  - name: regles-systeme
    rules:
      - alert: CPUEleve
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 85
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Charge CPU élevée sur {{ $labels.instance }}"
          description: "CPU > 85% depuis plus de 2 minutes (valeur actuelle : {{ $value | printf \"%.1f\" }}%)"

      - alert: DisqueCritique
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 10
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Espace disque critique sur {{ $labels.instance }}"
          description: "Moins de 10% d'espace libre sur la partition racine"

      - alert: InstanceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "{{ $labels.instance }} est injoignable"
          description: "La cible ne répond plus aux scrapes Prometheus depuis 1 minute"
```

Référencez ce fichier dans `prometheus.yml` :

```yaml
rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['host.docker.internal:9093']
```

Redémarrez Prometheus et vérifiez dans l'onglet **Alerts** que les trois règles apparaissent à l'état **Inactive**.

## 4. Étape 3 — Création d'un bot Telegram (ou webhook Discord)

**Option A — Telegram :** depuis l'application Telegram, contactez `@BotFather`, envoyez `/newbot`, suivez les instructions et récupérez le token du bot. Créez ensuite un groupe, ajoutez votre bot, et récupérez le `chat_id` via :

```bash
curl https://api.telegram.org/bot<TOKEN>/getUpdates
```

**Option B — Discord :** dans les paramètres d'un salon textuel, onglet Intégrations > Webhooks, créez un nouveau webhook et copiez son URL.

## 5. Étape 4 — Configuration d'Alertmanager

Exemple de configuration `alertmanager.yml` utilisant un webhook intermédiaire (un petit script Python qui relaie vers Telegram) :

```yaml
route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 30s
  repeat_interval: 1h
  receiver: 'notif-telegram'
  routes:
    - match:
        severity: critical
      receiver: 'notif-telegram-urgent'
      repeat_interval: 15m

receivers:
  - name: 'notif-telegram'
    webhook_configs:
      - url: 'http://host.docker.internal:5000/alert'
        send_resolved: true
  - name: 'notif-telegram-urgent'
    webhook_configs:
      - url: 'http://host.docker.internal:5000/alert'
        send_resolved: true

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['instance']
```

**Question 1 :**  
Expliquez avec vos propres mots le rôle de la section `inhibit_rules` ci-dessus. Pourquoi est-il pertinent d'inhiber une alerte warning quand une alerte critical est déjà active sur la même instance ?

## 6. Étape 5 — Script relais Python vers Telegram

Créez `relay.py`, un micro-serveur Flask qui reçoit les webhooks d'Alertmanager au format JSON et les reformate en message Telegram lisible :

```python
from flask import Flask, request
import requests

app = Flask(__name__)
TELEGRAM_TOKEN = "VOTRE_TOKEN"
CHAT_ID = "VOTRE_CHAT_ID"

@app.route("/alert", methods=["POST"])
def relay():
    data = request.get_json()
    for a in data.get("alerts", []):
        statut = a["status"].upper()
        nom = a["labels"].get("alertname", "inconnue")
        instance = a["labels"].get("instance", "?")
        description = a["annotations"].get("description", "")
        emoji = "🔴" if statut == "FIRING" else "🟢"
        message = f"{emoji} [{statut}] {nom}\nInstance : {instance}\n{description}"
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message}
        )
    return "", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

Lancez-le (`pip install flask requests` au préalable), puis générez artificiellement une charge CPU pour déclencher l'alerte `CPUEleve` :

```bash
sudo apt install stress -y
stress --cpu 4 --timeout 180
```

**Question 2 :**  
Vérifiez que vous recevez bien le message sur Telegram/Discord, puis la notification de résolution une fois la charge retombée. Capturez les deux messages (firing et resolved) et insérez les captures dans votre rendu.

## 7. Étape 6 — Le système d'acquittement (silences)

Depuis l'interface web d'Alertmanager (`http://<ip_vm>:9093`), créez un silence d'une heure sur l'alerte `CPUEleve` en argumentant un motif (« maintenance planifiée »). Observez que les notifications cessent pendant la durée du silence.

**Question 3 :**  
Dans un contexte de SOC, pourquoi est-il important de tracer qui a créé un silence et pourquoi (champ « comment ») plutôt que de simplement couper les notifications côté client de messagerie ?

## 8. Livrables attendus

- `alert_rules.yml` et `alertmanager.yml` finalisés
- `relay.py` (ou équivalent webhook Discord direct)
- Captures d'écran des notifications firing/resolved
- Réponses aux questions 1 à 3

---

# TP3 — Supervision réseau via SNMP avec Net-SNMP, LibreNMS et MRTG

| | |
|---|---|
| **Durée estimée** | 6 heures |
| **Outils** | Net-SNMP (snmpd, snmpwalk), MRTG, LibreNMS (ou Cacti au choix) |
| **Compétences visées** | Administrer et sécuriser le réseau d'entreprise ; suivi de métriques avec le protocole SNMP |
| **Pré-requis** | Notions de base sur les OID et la MIB |

## 1. Contexte

Le parc à superviser comprend également des équipements réseau (switches, routeurs, imprimantes) qui ne supportent ni agent Prometheus ni script personnalisé, mais qui exposent tous une interface SNMP. Vous devez démontrer la capacité à brancher un outil de supervision sur une source SNMP, condition imposée dans le cahier des charges du client.

## 2. Étape 1 — Installation et configuration de l'agent SNMP

Sur la VM faisant office d'équipement à superviser :

```bash
sudo apt update && sudo apt install snmpd snmp -y
```

Éditez `/etc/snmp/snmpd.conf` pour définir une communauté en lecture seule (à des fins pédagogiques uniquement ; en production, préférez SNMPv3 avec authentification et chiffrement) :

```
rocommunity tp-master-ro  10.0.0.0/24
syslocation  "Salle TP - Master Cyber"
syscontact   admin@tp-local.fr
sysservices  72
```

```bash
sudo systemctl restart snmpd
sudo systemctl enable snmpd
```

**Question 1 :**  
SNMPv1 et SNMPv2c transmettent la communauté en clair sur le réseau. Recherchez et expliquez en quelques lignes les trois niveaux de sécurité apportés par SNMPv3 (`noAuthNoPriv`, `authNoPriv`, `authPriv`).

## 3. Étape 2 — Interrogation manuelle avec snmpwalk

```bash
snmpwalk -v2c -c tp-master-ro localhost system
snmpget -v2c -c tp-master-ro localhost 1.3.6.1.2.1.1.5.0
snmpwalk -v2c -c tp-master-ro localhost 1.3.6.1.2.1.25.3.3.1.2
```

**Question 2 :**  
Identifiez à quoi correspond l'OID `1.3.6.1.2.1.1.5.0` et l'OID `1.3.6.1.2.1.25.3.3.1.2` en vous appuyant sur la MIB-2 standard. Donnez la branche complète (`iso.org.dod.internet...`) pour l'un des deux.

## 4. Étape 3 — Historisation avec MRTG

```bash
sudo apt install mrtg -y
sudo cfgmaker --output=/etc/mrtg.cfg tp-master-ro@localhost
sudo mkdir -p /var/www/html/mrtg
sudo env LANG=C mrtg /etc/mrtg.cfg
sudo env LANG=C mrtg /etc/mrtg.cfg   # exécuter 2 fois pour amorcer l'historique
sudo indexmaker /etc/mrtg.cfg > /var/www/html/mrtg/index.html
```

Ajoutez une tâche cron pour une exécution toutes les 5 minutes :

```
*/5 * * * * env LANG=C /usr/bin/mrtg /etc/mrtg.cfg
```

Vérifiez l'apparition des graphiques de trafic interface par interface sur `http://<ip_vm>/mrtg/`.

## 5. Étape 4 — Supervision centralisée avec LibreNMS

Plutôt qu'une installation complète depuis les sources (longue), utilisez l'image Docker officielle pour ce TP :

```bash
docker run -d --name librenms \
  -p 8000:8000 \
  -e TZ=Europe/Paris \
  -v librenms_data:/data \
  librenms/librenms
```

Une fois l'interface accessible sur `http://<ip_vm>:8000`, ajoutez votre équipement via **Devices > Add Device**, en renseignant l'adresse IP et la communauté SNMP définie à l'étape 1.

**Question 3 :**  
Après découverte automatique, LibreNMS affiche un inventaire des interfaces, capteurs de température éventuels, et services détectés. Listez trois informations remontées automatiquement que vous n'aviez pas explicitement configurées, et expliquez par quel mécanisme SNMP elles ont pu être découvertes.

## 6. Étape 5 — Mise en place d'une alerte SNMP

Dans LibreNMS, configurez une règle d'alerte native sur le taux d'utilisation d'une interface réseau (**Alert Rules > Add Rule**), avec un seuil à 80% de bande passante sur 5 minutes, puis associez-y un transport de notification e-mail ou webhook.

## 7. Livrables attendus

- Le fichier `snmpd.conf` commenté
- Une capture des graphiques MRTG
- Une capture de l'inventaire LibreNMS pour l'équipement ajouté
- Réponses aux questions 1 à 3

---

# TP4 — Détection d'intrusions et dérives système avec auditd, Fail2ban et scripts maison

| | |
|---|---|
| **Durée estimée** | 6 heures |
| **Outils** | auditd, Fail2ban, AppArmor, journalctl, Python ou PowerShell |
| **Compétences visées** | Mesurer et analyser le niveau de sécurité de l'infrastructure |
| **Pré-requis** | Connaissance des journaux systèmes Linux (syslog, journald) et Windows (Observateur d'événements) |

## 1. Contexte

Au-delà de la performance, la supervision doit couvrir le volet sécurité : détecter les tentatives de connexion suspectes, les redémarrages non planifiés, les élévations de privilèges anormales, ou encore une dérive de l'horloge système qui invaliderait des preuves d'horodatage en cas d'investigation. Ce TP combine outils dédiés et scripts maison, comme demandé dans le cahier des charges (« métriques spécifiques basées sur des scripts en Python ou PowerShell »).

## 2. Étape 1 — Suivi des journaux système avec journalctl

```bash
journalctl -p err -b
journalctl -u ssh --since "1 hour ago"
journalctl _SYSTEMD_UNIT=systemd-logind.service | grep -i boot
```

**Question 1 :**  
Donnez la commande `journalctl` permettant de lister uniquement les événements de démarrage (boot) des sept derniers jours, avec leur date précise.

## 3. Étape 2 — Surveillance des élévations de privilèges (sudo)

Tout appel à `sudo` est journalisé. Affichez l'historique :

```bash
grep 'sudo:' /var/log/auth.log | tail -n 30
```

Écrivez un script Python `sudo_watch.py` qui surveille en continu ce fichier (à la manière de `tail -f`) et déclenche une alerte console lorsqu'une commande sudo est exécutée par un utilisateur ne figurant pas dans une liste blanche :

```python
import time

WHITELIST = {"admin", "deploy"}
LOGFILE = "/var/log/auth.log"

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
                    print(f"[ALERTE] Commande sudo par utilisateur non autorisé : {utilisateur}")
                    print(f"  -> {ligne.strip()}")

if __name__ == "__main__":
    surveille()
```

**Question 2 :**  
Testez votre script en exécutant une commande sudo depuis un compte hors liste blanche. Proposez une évolution du script pour qu'il envoie l'alerte vers le webhook Telegram/Discord construit au TP2 plutôt que de l'afficher en console.

## 4. Étape 3 — auditd pour la traçabilité fine

```bash
sudo apt install auditd audispd-plugins -y
sudo systemctl enable --now auditd
```

Ajoutez une règle de surveillance sur le fichier `/etc/passwd` et sur les exécutions de la commande `su` :

```bash
sudo auditctl -w /etc/passwd -p wa -k surveillance_passwd
sudo auditctl -w /usr/bin/su -p x -k surveillance_su
sudo auditctl -l
```

Provoquez un événement (par exemple `sudo nano /etc/passwd` puis quittez sans enregistrer), puis consultez les traces :

```bash
sudo ausearch -k surveillance_passwd | tail -n 20
```

**Question 3 :**  
Rendez ces règles persistantes au redémarrage en les ajoutant dans `/etc/audit/rules.d/audit.rules`. Expliquez pourquoi `auditctl` seul ne suffit pas pour une configuration durable.

## 5. Étape 4 — Fail2ban contre le brute-force SSH

```bash
sudo apt install fail2ban -y
```

Créez `/etc/fail2ban/jail.local` :

```ini
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 4
findtime = 300
bantime = 1800
```

```bash
sudo systemctl restart fail2ban
sudo fail2ban-client status sshd
```

Depuis une autre machine (ou un autre terminal), tentez plusieurs connexions SSH avec un mauvais mot de passe afin de déclencher le bannissement, puis vérifiez :

```bash
sudo fail2ban-client status sshd
sudo iptables -L -n | grep DROP
```

## 6. Étape 5 — Détection de dérive d'horloge et d'espace disque (mesure manuelle)

Conformément au syllabus, mettez en place une mesure de performance manuelle simple : un script qui compare l'heure locale à une source de temps fiable et alerte en cas de dérive, ainsi qu'un contrôle de l'espace disque consommé dans les répertoires utilisateurs.

```python
#!/usr/bin/env python3
import subprocess
import re
import os

SEUIL_DERIVE_SECONDES = 2
SEUIL_QUOTA_MO = 5000
REPERTOIRES_UTILISATEURS = "/home"

def verifie_derive_horloge():
    sortie = subprocess.run(
        ["ntpdate", "-q", "0.fr.pool.ntp.org"],
        capture_output=True, text=True
    ).stdout
    correspondance = re.search(r"offset ([\-0-9.]+)", sortie)
    if correspondance:
        derive = abs(float(correspondance.group(1)))
        if derive > SEUIL_DERIVE_SECONDES:
            print(f"[ALERTE] Dérive horloge de {derive:.2f}s détectée, vérifier le service NTP local")
        else:
            print(f"[OK] Dérive horloge : {derive:.2f}s")

def verifie_quotas_utilisateurs():
    for utilisateur in os.listdir(REPERTOIRES_UTILISATEURS):
        chemin = os.path.join(REPERTOIRES_UTILISATEURS, utilisateur)
        if os.path.isdir(chemin):
            taille = subprocess.run(
                ["du", "-sm", chemin], capture_output=True, text=True
            ).stdout.split()[0]
            if int(taille) > SEUIL_QUOTA_MO:
                print(f"[ALERTE] {utilisateur} dépasse le quota : {taille} Mo")

if __name__ == "__main__":
    verifie_derive_horloge()
    verifie_quotas_utilisateurs()
```

Planifiez son exécution toutes les 30 minutes via cron, en redirigeant la sortie vers un fichier de log dédié.

**Question 4 :**  
Pourquoi une dérive d'horloge non maîtrisée pose-t-elle un problème de sécurité, notamment pour la corrélation de logs entre plusieurs machines et pour la validité de certificats TLS ?

## 7. Livrables attendus

- `sudo_watch.py` et `derive_horloge.py`
- Les règles auditd persistées (`audit.rules`)
- La configuration `jail.local` et une capture du bannissement Fail2ban
- Réponses aux questions 1 à 4

---

# TP5 — Disponibilité, SLA et rédaction de rapports d'incident avec Uptime Kuma

| | |
|---|---|
| **Durée estimée** | 6 heures |
| **Outils** | Uptime Kuma, Docker, tableur ou script Python pour le calcul de SLA |
| **Compétences visées** | Superviser la disponibilité de l'infrastructure ; rapports et SLA ; rédaction de rapports d'incident en anglais |
| **Pré-requis** | TP1 à TP4 (la stack de supervision doit déjà exister) |

## 1. Contexte

Le client final a signé un contrat avec un engagement de disponibilité de 99,9% sur ses services exposés en ligne. Votre rôle est double : mettre en place un outil de suivi de disponibilité externe (Uptime Kuma, complémentaire de Prometheus qui supervise l'intérieur des machines), puis produire la documentation contractuelle et opérationnelle associée à un incident simulé.

## 2. Étape 1 — Comprendre le calcul de SLA

Un SLA (*Service Level Agreement*) exprime un engagement de disponibilité en pourcentage sur une période donnée. Le tableau ci-dessous donne la correspondance temps d'indisponibilité tolérée / pourcentage, base de calcul classique en hébergement :

| SLA | Indisponibilité / an | Indisponibilité / mois |
|-----|----------------------|------------------------|
| 99% | 3,65 jours | 7h 18min |
| 99,9% | 8h 45min | 43min 50s |
| 99,95% | 4h 22min | 21min 55s |
| 99,99% | 52min 35s | 4min 23s |

**Question 1 :**  
Un service a connu trois incidents sur le dernier mois (30 jours) : 12 minutes, 1h47, et 8 minutes d'indisponibilité totale. Calculez le pourcentage de disponibilité réel sur le mois et indiquez si l'engagement contractuel de 99,9% est respecté.

## 3. Étape 2 — Déploiement d'Uptime Kuma

```bash
docker run -d --name uptime-kuma \
  -p 3001:3001 \
  -v uptime-kuma:/app/data \
  louislam/uptime-kuma:1
```

Accédez à `http://<ip_vm>:3001`, créez votre compte administrateur, puis ajoutez au moins trois moniteurs distincts :

- Un moniteur **HTTP(s)** sur un site public (ex. votre propre serveur web de TP, ou un site de test)
- Un moniteur **TCP Port** sur le port SSH (22) de votre VM
- Un moniteur **Ping** sur l'adresse de la passerelle réseau

Pour chacun, définissez un intervalle de vérification de 60 secondes et un seuil de tentatives avant passage en « Down » de 2.

## 4. Étape 3 — Branchement des notifications

Réutilisez le bot Telegram ou le webhook Discord du TP2 : dans Uptime Kuma, rendez-vous dans **Settings > Notifications**, ajoutez une notification de type Telegram (ou Webhook générique pointant vers Discord), et associez-la à vos trois moniteurs.

Simulez une panne en arrêtant le service web ou en bloquant le port SSH via iptables, puis vérifiez la réception de la notification et la bascule du statut sur le dashboard public d'Uptime Kuma.

```bash
sudo iptables -A INPUT -p tcp --dport 22 -j DROP
# attendre la détection puis :
sudo iptables -D INPUT -p tcp --dport 22 -j DROP
```

## 5. Étape 4 — Page de statut publique

Depuis le menu **Status Pages**, créez une page publique « Statut des services » regroupant vos trois moniteurs, avec un message d'incident manuel rédigé pour la période de panne simulée.

**Question 2 :**  
Quelle différence faites-vous entre la page de statut destinée aux clients et le dashboard interne d'astreinte ? Quelles informations doivent, selon vous, être masquées au public ?

## 6. Étape 5 — Rédaction du rapport d'incident en anglais

À partir de l'incident simulé (coupure SSH ou web), rédigez un rapport d'incident (« incident report » / « post-mortem ») en anglais, structuré selon le format suivant, standard dans la majorité des équipes SRE/Ops internationales :

- **Incident summary** (1 paragraph, plain language)
- **Severity and impact** (affected services, affected users, duration)
- **Timeline** (UTC timestamps, detection, escalation, mitigation, resolution)
- **Root cause analysis**
- **Resolution steps taken**
- **Action items / preventive measures** (owner + due date for each)

Exemple de structure de timeline attendue :

| Time (UTC) | Status | Event |
|------------|--------|-------|
| 14:02 | Detected | Uptime Kuma alert fired: SSH port unreachable on srv-tp-01 |
| 14:05 | Acknowledged | On-call engineer acknowledged the Telegram alert |
| 14:18 | Mitigated | Firewall rule identified and reverted |
| 14:20 | Resolved | Monitor confirmed service back to UP status |

**Question 3 :**  
Pourquoi les rapports d'incident internationaux utilisent-ils systématiquement l'heure UTC plutôt que l'heure locale du rédacteur ? Donnez un exemple concret de confusion que cela permet d'éviter.

## 7. Livrables attendus

- Une capture du dashboard Uptime Kuma et de la page de statut publique
- Le calcul détaillé du SLA mensuel (question 1)
- Le rapport d'incident complet rédigé en anglais (format libre : Markdown ou Word)
- Réponses aux questions 2 et 3

## 8. Synthèse de la semaine

À l'issue des cinq TP, vous disposez d'une chaîne de supervision complète et représentative d'un environnement professionnel : collecte de métriques (Prometheus), visualisation (Grafana), alerting temps réel (Alertmanager + IM), supervision réseau (SNMP/LibreNMS), détection de sécurité (auditd/Fail2ban), et pilotage de la disponibilité contractuelle (Uptime Kuma + SLA).

L'évaluation finale du module portera sur la mise en place d'un système de suivi et d'alertes fonctionnel, démontré en contrôle continu sur votre environnement de TP.
