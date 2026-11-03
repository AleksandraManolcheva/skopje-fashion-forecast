# forecast_skopje.py
# Uses only Python standard library; no pip installation required.
# Run: python forecast_skopje.py

import csv
import json
import urllib.error
import urllib.request

API_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=41.9981"
    "&longitude=21.4254"
    "&hourly=temperature_2m,relative_humidity_2m,cloud_cover,wind_speed_10m,pressure_msl"
    "&daily=temperature_2m_max,temperature_2m_min"
    "&forecast_days=7"
    "&timezone=Europe%2FSkopje"
    "&wind_speed_unit=kmh"
)

TARGET_HOURS = {"07:00", "14:00", "21:00"}

def main():
    print("Prevzemam prognoza")

    request = urllib.request.Request(
        API_URL,
        headers={"User-Agent": "SkopjeWeatherScript/1.0"}
    )
    
    print("ok 1")

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"API HTTP грешка: {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Мрежна грешка: {exc.reason}") from exc
        
    print("ok 2")

    if data.get("error"):
        raise RuntimeError(data.get("reason", "Open-Meteo врати грешка."))
        
        
    print("ok 3")

    daily_by_date = {}
    daily = data["daily"]
    for i, date in enumerate(daily["time"]):
        daily_by_date[date] = {
            "daily_max_temperature_c": daily["temperature_2m_max"][i],
            "daily_min_temperature_c": daily["temperature_2m_min"][i],
        }

    hourly = data["hourly"]
    rows = []

    for i, timestamp in enumerate(hourly["time"]):
        date, time = timestamp.split("T")
        if time not in TARGET_HOURS:
            continue

        day_values = daily_by_date.get(date, {})
        rows.append({
            "date": date,
            "time": time,
            "temperature_c": hourly["temperature_2m"][i],
            "daily_max_temperature_c": day_values.get("daily_max_temperature_c"),
            "daily_min_temperature_c": day_values.get("daily_min_temperature_c"),
            "cloud_cover_percent": hourly["cloud_cover"][i],
            "relative_humidity_percent": hourly["relative_humidity_2m"][i],
            "wind_speed_kmh": hourly["wind_speed_10m"][i],
            "pressure_msl_hpa": hourly["pressure_msl"][i],
        })

    fieldnames = [
        "date", "time", "temperature_c",
        "daily_max_temperature_c", "daily_min_temperature_c",
        "cloud_cover_percent", "relative_humidity_percent",
        "wind_speed_kmh", "pressure_msl_hpa",
    ]
    print("ok 4")

    # utf-8-sig makes the CSV easier to open correctly in Excel.
    with open("forecast_skopje.csv", "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print("ok 6")

    print(f"len(rows) merenja vo forecast_skopje.csv")
    
    print("ok 7")
    for row in rows:
        print(1)

if __name__ == "__main__":
    main()
