# Stack ELK — Elasticsearch · Logstash · Kibana 8.x

Installation lab via **Docker Compose** (mêmes ports et config que le [cahier](../docs/cahier_tp_elk.md) ; pas besoin de `sudo apt`).

## Démarrage

```bash
cd elk
docker compose up -d
```

## Vérifications

```bash
curl http://localhost:9200
curl http://localhost:9200/_cat/indices?v
# Kibana : http://<IP_VM>:5601
docker compose ps
```

## Fichiers

| Fichier | Rôle |
|---------|------|
| `docker-compose.yml` | ES + Kibana + Logstash 8.15 |
| `elasticsearch/elasticsearch.yml` | Config lab (security off) |
| `kibana/kibana.yml` | Bind `0.0.0.0:5601` |
| `logstash/pipeline/test.conf` | Pipeline test → index `logstash-test` |

> `xpack.security.enabled: false` = **lab uniquement**, jamais en production exposée.
