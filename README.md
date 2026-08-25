## 1. Avtomatizacija in dockerizacija

Skripta `script/fetch_weather.py` pokliče Open-Meteo API (brezplačen, brez ključa) za trenutno vreme v Ljubljani, izlušči izbrane podatke in jih zapiše v `output/weather.json`. Uporablja samo standardno Python knjižnico (urllib, json), nobenih dodatnih odvisnosti.

### Docker

Dockerfile je na root nivoju in temelji na `python:3.12-alpine` (majhen image, brez nepotrebnih stvari). Container ne poganja skripte avtomatsko (možna izboljšava). Ob zagonu dobiš shell in skripto poženeš ročno, kot pišejo navodila (zaženeš container, iz containerja zaženeš skripto).

```bash
docker build -t weather-fetcher .
docker run --rm -it -v "$(pwd)/output:/app/output" weather-fetcher
```

Znotraj containerja:

```sh
python fetch_weather.py
```

Datoteka je zaradi volume mounta dostopna tudi na hostu:

```bash
cat output/weather.json
```

Isto gre tudi preko docker-compose:

```bash
docker compose build
docker compose run --rm weather-fetcher python fetch_weather.py
```

ali z containerjem, ki teče v ozadju:

```bash
docker compose up -d
docker compose exec weather-fetcher python fetch_weather.py
docker compose down
```
## 2. Cloud in IaC

Nazadnje sem s Terraformom postavljal OpenVAS (orodje za vulnerability scanning) na AWS ECS Fargate (ARM64/Graviton). Na kratko arhitektura: custom VPC z javnimi in privatnimi subnet-i, ALB v javnih subnet-ih z avtentikacijo prek Google OIDC (`authenticate-oidc` na listenerju), ki forwarda na ECS task. Task ima dva containerja: "OpenVAS" in pred njim sidecar (nginx + majhna Python storitev), ki preveri JWT, ki ga podpiše ALB (`x-amzn-oidc-data`). Podatki (Postgres, feed, poročila) so na EFS, admin gesla so v Secrets Manager, IAM execution/task role sta ločena. Ker se orodje ne uporablja stalno, sem dodal EventBridge Scheduler, ki servis mesečno zbudi (`desired_count` 0 → 1), kar zniža stroške v primerjavi s stalno tekočim containerjem.

**Zakaj taka arhitektura?**
OpenVAS je interno orodje (vulnerability scanner), zato ni smel biti javno dostopen brez avtentikacije. ALB + Google OIDC mi je dal centralizirano prijavo. Sidecar z validacijo JWT sem dodal, če bi kdo kdaj dosegel task mimo ALB-ja (napačna security group, notranji promet...), bi brez tega preverjanja to pomenilo dostop brez avtentikacije. Fargate namesto EC2/EKS, ker gre za en sam servis in ni smisla vzdrževati clustra ali gonilnih node-ov zanj. EFS namesto RDS, ker OpenVAS interno uporablja svoj Postgres in feed podatke na disku s tem je lažje persistirati celotno mapo kot app predelovati.

**Kaj bi spremenil, če bi jo danes snoval še enkrat?**
Dodal bi še scheduled stop (trenutno imam samo start cron, stop je bolj ročen), premislil bi o Fargate Spot za ta non-critical, periodičen workload (capacity provider je že pripravljen, samo strategy bi obrnil), in dodal osnovni CloudWatch alarm na health ECS servisa/EFS throughput, ker trenutno ni nobenega monitoringa razen logov.

**Kaj bi spremenil, če bi se promet povečal na 10x?**
Tu bi bil največji problem to, da je OpenVAS/Postgres na EFS en sam stateful container. Ne morem ga preprosto horizontalno skalirati z več ECS taski, ker bi si delili isto podatkovno bazo na EFS. Pri 10x večji uporabi (več sočasnih scanov) bi ločil bazo (RDS) od compute dela (zahteva arhitekturni redesign community openvas image-a) in scan job-e razdelil prek queue-a (SQS) na več worker containerjev, ki bi scale-ali neodvisno.

