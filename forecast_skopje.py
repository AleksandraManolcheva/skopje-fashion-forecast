import csv
import json
import urllib.error
import urllib.request
from datetime import datetime

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

# Definiranje na kategorii, sliki i opisi spored uslovite
def get_outfit_category(temp_max, cloud_cover, wind_speed):
    if temp_max >= 22:
        return {
            "title": "Leto suvo sonch tiv",
            "img": "images/leto_suvo.jpg"
        }
    elif temp_max >= 12:
        if cloud_cover > 60 and wind_speed > 15:
            return {
                "title": "Esen VpnezhlivoVet",
                "img": "images/esen_vrnezlivovet.jpg"
            }
        elif cloud_cover > 60:
            return {
                "title": "Esen Vlazh Oblach Tiv",
                "img": "images/esen_vlazh_oblach.jpg"
            }
        elif wind_speed > 15:
            return {
                "title": "Esen VlazhnoSonchVet",
                "img": "images/esen_vlazhno_sonch.jpg"
            }
        else:
            return {
                "title": "Esen suvo sonch tiv",
                "img": "images/esen_suvo.jpg"
            }
    else:
        if wind_speed > 15:
            return {
                "title": "Zima VrnezhlivoVet",
                "img": "images/zima_vrnezlivovet.jpg"
            }
        else:
            return {
                "title": "Zima VrnezhlivoTiv",
                "img": "images/zima_vrnezlivotiv.jpg"
            }

def main():
    print("Prevzemam prognoza...")
    request = urllib.request.Request(API_URL, headers={"User-Agent": "SkopjeWeatherScript/1.0"})
    
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Greshka pri prevzemanje: {exc}")

    # Grupiranje na podatocite po denovi za CSV i HTML
    daily = data["daily"]
    hourly = data["hourly"]
    
    daily_summary = {}
    for i, date in enumerate(daily["time"]):
        daily_summary[date] = {
            "date": date,
            "max_temp": daily["temperature_2m_max"][i],
            "min_temp": daily["temperature_2m_min"][i],
            "hours": []
        }

    for i, timestamp in enumerate(hourly["time"]):
        date, time = timestamp.split("T")
        if time in TARGET_HOURS and date in daily_summary:
            daily_summary[date]["hours"].append({
                "time": time,
                "temp": hourly["temperature_2m"][i],
                "cloud": hourly["cloud_cover"][i],
                "wind": hourly["wind_speed_10m"][i],
                "humidity": hourly["relative_humidity_2m"][i],
                "pressure": hourly["pressure_msl"][i]
            })

    # Zacuvanje na CSV fajlot
    csv_rows = []
    for date, info in daily_summary.items():
        for h in info["hours"]:
            csv_rows.append({
                "date": date,
                "time": h["time"],
                "temperature_c": h["temp"],
                "daily_max_temperature_c": info["max_temp"],
                "daily_min_temperature_c": info["min_temp"],
                "cloud_cover_percent": h["cloud"],
                "relative_humidity_percent": h["humidity"],
                "wind_speed_kmh": h["wind"],
                "pressure_msl_hpa": h["pressure"]
            })

    fieldnames = [
        "date", "time", "temperature_c", "daily_max_temperature_c",
        "daily_min_temperature_c", "cloud_cover_percent",
        "relative_humidity_percent", "wind_speed_kmh", "pressure_msl_hpa"
    ]
    
    with open("forecast_skopje.csv", "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    # Generiranje na HTML moden kalendar
    generate_html_calendar(daily_summary)

def generate_html_calendar(daily_summary):
    today = datetime.now()
    month_year = today.strftime("%B %Y").upper()

    html_cards = ""
    for date, info in daily_summary.items():
        dt = datetime.strptime(date, "%Y-%m-%d")
        day_str = dt.strftime("%d.%m")
        
        # Presmetka na prosecna oblacnost i vetar za denot
        avg_cloud = sum(h["cloud"] for h in info["hours"]) / max(len(info["hours"]), 1)
        avg_wind = sum(h["wind"] for h in info["hours"]) / max(len(info["hours"]), 1)
        
        outfit = get_outfit_category(info["max_temp"], avg_cloud, avg_wind)
        
        html_cards += f"""
        <div class="day-card">
            <img src="{outfit['img']}" alt="{outfit['title']}" onerror="this.src='https://via.placeholder.com/100x150?text=Outfit'">
            <div class="day-label">{day_str}</div>
            <div class="temp-label">{info['max_temp']}°C / {info['min_temp']}°C</div>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="mk">
<head>
    <meta charset="UTF-8">
    <title>MODEN-VREME kalendar Skopje</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #eceff1; padding: 20px; text-align: center; }}
        .header {{ background: #ffeb3b; padding: 15px; font-weight: bold; font-size: 20px; border-radius: 5px; margin-bottom: 20px; color: #b71c1c; }}
        .calendar-grid {{ display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; }}
        .day-card {{ background: white; border: 2px solid #333; padding: 5px; width: 110px; text-align: center; border-radius: 4px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); }}
        .day-card img {{ width: 100%; height: 140px; object-fit: cover; border-bottom: 1px solid #ccc; }}
        .day-label {{ font-weight: bold; margin-top: 5px; font-size: 14px; }}
        .temp-label {{ font-size: 11px; color: #555; }}
        .legend {{ margin-top: 30px; background: #fff; padding: 15px; border-radius: 5px; display: inline-block; text-align: left; }}
    </style>
</head>
<body>
    <div class="header">
        MODEN-VREME kalendar Skopje, {month_year}
    </div>
    <div class="calendar-grid">
        {html_cards}
    </div>
</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Uspeshno generiran index.html kalendar!")

if __name__ == "__main__":
    main()
