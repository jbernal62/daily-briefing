"""Open-Meteo API — best weather in European cities (free, no key)."""

import httpx

# Lat/lon for European cities
CITY_COORDS = {
    "Barcelona": (41.39, 2.17),
    "Lisbon": (38.72, -9.14),
    "Athens": (37.98, 23.73),
    "Rome": (41.90, 12.50),
    "Nice": (43.71, 7.26),
    "Dubrovnik": (42.65, 18.09),
    "Malaga": (36.72, -4.42),
    "Split": (43.51, 16.44),
    "Valencia": (39.47, -0.38),
    "Palermo": (38.12, 13.36),
    "Heraklion": (35.34, 25.13),
    "Faro": (37.02, -7.94),
}


async def fetch_weather(cities: list[str]) -> list[dict]:
    """Fetch today's weather for European cities and rank by best conditions."""
    city_weather = []

    async with httpx.AsyncClient(timeout=15) as client:
        for city in cities:
            coords = CITY_COORDS.get(city)
            if not coords:
                continue
            try:
                resp = await client.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={
                        "latitude": coords[0],
                        "longitude": coords[1],
                        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
                        "timezone": "Europe/Amsterdam",
                        "forecast_days": 1,
                    },
                )
                resp.raise_for_status()
                data = resp.json().get("daily", {})
                temp_max = data.get("temperature_2m_max", [0])[0]
                temp_min = data.get("temperature_2m_min", [0])[0]
                precip = data.get("precipitation_sum", [0])[0]
                code = data.get("weathercode", [0])[0]

                # Weather code to description
                weather_desc = _weather_code(code)

                # Score: higher temp + low precip = better
                score = temp_max - (precip * 5)

                city_weather.append({
                    "city": city,
                    "temp_max": temp_max,
                    "temp_min": temp_min,
                    "precip": precip,
                    "weather": weather_desc,
                    "score": score,
                })
            except httpx.HTTPError:
                continue

    # Sort by best weather score
    city_weather.sort(key=lambda x: x["score"], reverse=True)

    # Return top 3 as a single item
    if city_weather:
        top = city_weather[:3]
        lines = []
        for c in top:
            lines.append(f"{c['city']}: {c['temp_max']:.0f}C, {c['weather']}, {c['precip']:.1f}mm rain")
        return [{
            "category": "weather",
            "title": f"Best weather in Europe: {top[0]['city']} ({top[0]['temp_max']:.0f}C, {top[0]['weather']})",
            "description": " | ".join(lines),
            "source": "Open-Meteo",
            "url": "https://open-meteo.com",
            "published": "",
        }]
    return []


def _weather_code(code: int) -> str:
    codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Rime fog", 51: "Light drizzle", 53: "Drizzle",
        55: "Heavy drizzle", 61: "Light rain", 63: "Rain", 65: "Heavy rain",
        71: "Light snow", 73: "Snow", 75: "Heavy snow", 80: "Light showers",
        81: "Showers", 82: "Heavy showers", 95: "Thunderstorm",
    }
    return codes.get(code, "Unknown")
