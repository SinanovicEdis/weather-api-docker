import json
import os
import sys
from datetime import datetime, timezone
from urllib.error import URLError, HTTPError
from urllib.request import urlopen

API_URL = "https://api.open-meteo.com/v1/forecast"

CITY_NAME = "Ljubljana"
LATITUDE = 46.0569
LONGITUDE = 14.5058

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "weather.json")


def fetch_weather():
    params = (
        f"?latitude={LATITUDE}&longitude={LONGITUDE}"
        "&current_weather=true&timezone=UTC"
    )
    with urlopen(API_URL + params, timeout=10) as response:
        return json.load(response)


def process_weather(raw_data):
    current = raw_data["current_weather"]
    return {
        "city": CITY_NAME,
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "temperature_c": current["temperature"],
        "windspeed_kmh": current["windspeed"],
        "winddirection_deg": current["winddirection"],
        "observed_at": current["time"] + "+00:00",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def save_data(data):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Podatki shranjeni v: {OUTPUT_FILE}")


def main():
    try:
        raw = fetch_weather()
    except (URLError, HTTPError) as exc:
        print(f"Napaka pri klicu API-ja: {exc}", file=sys.stderr)
        sys.exit(1)

    processed = process_weather(raw)
    save_data(processed)
    print(json.dumps(processed, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
