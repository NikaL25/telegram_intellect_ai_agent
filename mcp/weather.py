import requests


class WeatherClient:
    """Клиент для работы с OpenWeatherMap API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city: str):
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
            "lang": "ru"
        }
        try:
            response = requests.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            return {
                "success": True,
                "city": data.get("name"),
                "weather": data["weather"][0]["description"],
                "temp": data["main"]["temp"]
            }
        except requests.HTTPError as http_exc:
            return {"success": False, "error": f"HTTP error: {http_exc}"}
        except requests.RequestException as req_exc:
            return {"success": False, "error": f"Request failed: {req_exc}"}
        except Exception as exc:
            return {"success": False, "error": f"Unexpected error: {exc}"}
