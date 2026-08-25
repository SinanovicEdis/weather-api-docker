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

