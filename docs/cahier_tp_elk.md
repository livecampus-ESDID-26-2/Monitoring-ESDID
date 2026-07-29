# Stack ELK

**Elasticsearch · Logstash · Kibana**  
Guide d'installation pour débutants — Ubuntu / Debian — Version **8.x**

---

## Bienvenue

Ce guide est conçu pour vous accompagner étape par étape, même si c'est la première fois que vous utilisez un terminal Linux. Chaque commande est expliquée. Lisez bien les encadrés « Attention » avant d'exécuter une commande.

---

## 1. C'est quoi la stack ELK ?

La stack ELK est un ensemble de trois logiciels open source qui fonctionnent ensemble pour collecter, analyser et afficher des données (notamment des journaux système, appelés « logs »).

Imaginez une chaîne de traitement :

- **Logstash** reçoit les données brutes (logs, fichiers, flux réseau…) et les nettoie.
- **Elasticsearch** stocke et indexe ces données pour les rendre très rapidement consultables.
- **Kibana** affiche tout ça dans un navigateur web, sous forme de tableaux de bord et de graphiques.

| Composant | Port | Ce qu'il fait simplement |
|-----------|------|--------------------------|
| Elasticsearch | 9200 | Stocke et cherche les données — c'est la « base de données » |
| Logstash | 5044 | Collecte et transforme les données avant de les envoyer à Elasticsearch |
| Kibana | 5601 | Interface web pour visualiser les données stockées dans Elasticsearch |

---

## 2. Avant de commencer

### 2.1 Ce dont vous avez besoin

Vérifiez que votre machine répond à ces exigences minimales avant de démarrer :

- **Système d'exploitation :** Ubuntu 20.04, 22.04 LTS, ou Debian 11/12
- **Mémoire RAM :** au minimum 4 Go (8 Go recommandé pour que tout tourne confortablement)
- **Espace disque :** au moins 20 Go de disponibles
- **Connexion internet** pour télécharger les paquets

> **Bon à savoir**  
> Vous n'avez pas besoin d'installer Java manuellement. Les paquets Elastic embarquent leur propre version de Java.

### 2.2 Comprendre le terminal et sudo

Toutes les commandes de ce guide se tapent dans un terminal (aussi appelé « console » ou « invite de commandes »). Pour l'ouvrir sous Ubuntu : faites `Ctrl + Alt + T`.

Vous verrez souvent `sudo` au début des commandes. Cela signifie que vous demandez les droits administrateur pour exécuter la commande. Le système vous demandera votre mot de passe la première fois.

> **Attention**  
> Ne copiez-collez jamais une commande depuis internet sans l'avoir lue et comprise. Dans ce guide, chaque commande est expliquée.

---

## 3. Étape 1 — Mettre à jour le système

Avant toute installation, il faut s'assurer que le système est à jour. Cela évite les conflits de versions.

Ouvrez un terminal et tapez la commande suivante, puis appuyez sur Entrée :

```bash
sudo apt-get update && sudo apt-get upgrade -y
```

**Que fait cette commande ?**

- `apt-get update` : télécharge la liste des mises à jour disponibles
- `apt-get upgrade -y` : installe toutes les mises à jour (le `-y` répond « oui » automatiquement)

> **Patience !**  
> Cette commande peut prendre quelques minutes. C'est normal, attendez qu'elle se termine (vous reverrez le symbole `$` à la fin).

---

## 4. Étape 2 — Ajouter le dépôt officiel Elastic

Un « dépôt » est un serveur de téléchargement. Nous allons indiquer à Ubuntu/Debian où télécharger les logiciels Elastic. Cette étape ne se fait qu'une seule fois.

### 4.1 Installer les outils nécessaires

Ces outils permettent de télécharger des fichiers et de gérer les clés de sécurité :

```bash
sudo apt-get install -y apt-transport-https curl gnupg
```

### 4.2 Importer la clé de sécurité

Les logiciels téléchargés sont signés numériquement. Cette commande importe la clé qui permet de vérifier que les fichiers sont authentiques :

```bash
curl -fsSL https://artifacts.elastic.co/GPG-KEY-elasticsearch \
  | sudo gpg --dearmor -o /usr/share/keyrings/elastic-keyring.gpg
```

> **Astuce**  
> Le `\` en fin de ligne signifie que la commande continue sur la ligne suivante. Vous pouvez tout copier d'un coup.

### 4.3 Ajouter le dépôt à la liste des sources

```bash
echo "deb [signed-by=/usr/share/keyrings/elastic-keyring.gpg] \
  https://artifacts.elastic.co/packages/8.x/apt stable main" \
  | sudo tee /etc/apt/sources.list.d/elastic-8.x.list
```

Puis mettez à jour la liste des paquets pour prendre en compte le nouveau dépôt :

```bash
sudo apt-get update
```

---

## 5. Étape 3 — Installer Elasticsearch

Elasticsearch est le cœur de la stack. C'est lui qui stocke et indexe toutes vos données. Installez-le en premier.

### 5.1 Installation

```bash
sudo apt-get install -y elasticsearch
```

> **Important : notez votre mot de passe !**  
> À la fin de l'installation, un mot de passe pour l'utilisateur « elastic » est affiché dans le terminal. Notez-le sur papier ou dans un fichier texte maintenant — il ne sera plus affiché.

### 5.2 Démarrer le service

Ces trois commandes activent et démarrent Elasticsearch :

```bash
sudo systemctl daemon-reload
sudo systemctl enable elasticsearch
sudo systemctl start elasticsearch
```

**Explication :**

- `daemon-reload` : recharge la liste des services système
- `enable` : fait en sorte qu'Elasticsearch démarre automatiquement à chaque redémarrage de la machine
- `start` : démarre le service maintenant

### 5.3 Vérifier que ça fonctionne

Pour vérifier l'état du service :

```bash
sudo systemctl status elasticsearch
```

Cherchez la ligne qui contient `active (running)` — elle doit être en vert. Si vous voyez `failed` ou `inactive`, lisez la section dépannage (section 9).

Vous pouvez aussi faire un test rapide en interrogeant Elasticsearch :

```bash
curl -X GET http://localhost:9200
```

Si tout va bien, vous obtenez une réponse JSON qui contient `"You Know, for Search"`. C'est bon signe !

### 5.4 Configuration pour les TPs

Par défaut, Elasticsearch active la sécurité (chiffrement + authentification). Pour simplifier les TPs, nous allons la désactiver. Ouvrez le fichier de configuration :

```bash
sudo nano /etc/elasticsearch/elasticsearch.yml
```

> **Comment utiliser nano**  
> `nano` est un éditeur de texte dans le terminal. Utilisez les flèches pour naviguer. `Ctrl+O` pour sauvegarder, puis Entrée. `Ctrl+X` pour quitter.

Trouvez les lignes suivantes et modifiez-les (ou ajoutez-les si elles n'existent pas) :

```yaml
cluster.name: elk-tp
node.name: node-1
network.host: 0.0.0.0
http.port: 9200
xpack.security.enabled: false
xpack.security.http.ssl.enabled: false
```

> **Attention**  
> `xpack.security.enabled: false` désactive toute authentification. À utiliser **UNIQUEMENT** en salle de TP sur une machine locale, jamais en production ou sur un serveur accessible depuis internet.

Sauvegardez (`Ctrl+O`, Entrée, `Ctrl+X`), puis redémarrez Elasticsearch pour appliquer les changements :

```bash
sudo systemctl restart elasticsearch
```

---

## 6. Étape 4 — Installer Kibana

Kibana est l'interface web qui permet de visualiser les données stockées dans Elasticsearch. Vous l'utilisez depuis un navigateur.

### 6.1 Installation

```bash
sudo apt-get install -y kibana
```

### 6.2 Configuration

Ouvrez le fichier de configuration de Kibana :

```bash
sudo nano /etc/kibana/kibana.yml
```

Ajoutez ou modifiez ces lignes :

```yaml
server.port: 5601
server.host: "0.0.0.0"
elasticsearch.hosts: ["http://localhost:9200"]
```

Sauvegardez et quittez nano (`Ctrl+O`, Entrée, `Ctrl+X`).

### 6.3 Démarrer Kibana

```bash
sudo systemctl enable kibana
sudo systemctl start kibana
```

Kibana peut prendre 30 à 60 secondes à démarrer la première fois. Patientez, puis ouvrez un navigateur web et allez à l'adresse :

[http://localhost:5601](http://localhost:5601)

(Sur une VM distante : `http://<IP_VM>:5601`, ex. `http://10.31.10.41:5601`.)

Vous devriez voir l'interface Kibana. Félicitations !

---

## 7. Étape 5 — Installer Logstash

Logstash est le composant qui collecte et transforme les données avant de les envoyer à Elasticsearch. Pour ce premier TP, nous allons juste vérifier qu'il fonctionne.

### 7.1 Installation

```bash
sudo apt-get install -y logstash
```

### 7.2 Créer un pipeline de test

Un « pipeline » est un fichier de configuration qui décrit comment Logstash doit traiter les données. Créez un fichier de test :

```bash
sudo nano /etc/logstash/conf.d/test.conf
```

Copiez exactement ce contenu dans le fichier :

```
input {
  stdin { }
}

filter {
  mutate {
    add_field => { "source" => "test-tp" }
  }
}

output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "logstash-test"
  }
  stdout { codec => rubydebug }
}
```

Ce pipeline signifie : lire depuis le clavier (`stdin`), ajouter un champ « source », envoyer à Elasticsearch ET afficher dans le terminal (`stdout`).

Sauvegardez et démarrez Logstash :

```bash
sudo systemctl enable logstash
sudo systemctl start logstash
```

---

## 8. Vérification finale

### 8.1 Vérifier les trois services en une commande

```bash
sudo systemctl status elasticsearch kibana logstash
```

Les trois services doivent afficher `active (running)`. Si l'un d'eux est en erreur, consultez la section suivante.

### 8.2 Checklist finale

- [ ] Elasticsearch répond sur [http://localhost:9200](http://localhost:9200)
- [ ] Kibana est accessible sur [http://localhost:5601](http://localhost:5601)
- [ ] Les trois services sont en état `active (running)`
- [ ] Vous voyez l'interface Kibana dans votre navigateur

> **Installation réussie !**  
> Bravo ! Si tous ces points sont validés, votre stack ELK est opérationnelle.

---

## 9. Que faire si ça ne marche pas ?

Voici les problèmes les plus courants et comment les résoudre :

| Symptôme | Solution |
|----------|----------|
| Le service affiche « failed » | Lisez les logs d'erreur : `sudo journalctl -u elasticsearch -n 50` — cherchez une ligne qui commence par `ERROR` ou `Exception`. |
| `curl` renvoie « connexion refusée » | Le service n'est pas encore démarré ou a planté. Essayez : `sudo systemctl restart elasticsearch` |
| Kibana affiche une page blanche ou erreur 503 | Kibana n'arrive pas à joindre Elasticsearch. Vérifiez qu'Elasticsearch tourne et que `kibana.yml` contient bien : `elasticsearch.hosts: ["http://localhost:9200"]` |
| « Permission denied » dans le terminal | Vous avez oublié `sudo` devant la commande. Relancez-la avec `sudo` au début. |
| Mémoire insuffisante (OutOfMemory) | Elasticsearch nécessite au moins 1 Go de RAM rien que pour lui. Fermez d'autres applications ou augmentez la RAM de votre VM. |

En cas de doute, la commande universelle pour lire les logs est :

```bash
sudo journalctl -u NOM_DU_SERVICE -f

# Exemples :
sudo journalctl -u elasticsearch -f
sudo journalctl -u kibana -f
sudo journalctl -u logstash -f
```

L'option `-f` affiche les logs en temps réel. Appuyez sur `Ctrl+C` pour arrêter.

---

## 10. Mémo — Commandes à retenir

```bash
# ── Démarrer / arrêter / redémarrer un service ──
sudo systemctl start    elasticsearch   # démarrer
sudo systemctl stop     elasticsearch   # arrêter
sudo systemctl restart  elasticsearch   # redémarrer
sudo systemctl status   elasticsearch   # voir l'état

# (remplacez elasticsearch par kibana ou logstash)

# ── Tester Elasticsearch ──
curl http://localhost:9200                 # santé du serveur
curl http://localhost:9200/_cat/indices?v  # lister les index

# ── Lire les logs ──
sudo journalctl -u elasticsearch -f
```

> **Conseil avant de continuer**  
> Une fois l'installation terminée et vérifiée, prenez un **snapshot** de votre machine virtuelle. Vous pourrez ainsi revenir à cet état propre si quelque chose se passe mal lors des prochains TPs.
