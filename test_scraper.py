import requests
import base64
import json

url = "http://127.0.0.1:8000/scrape"
headers = {"x-api-key": "scraping_secret_key_2025"}
data = {
    "username": "will",
    "password": "will",
    "target_url": "https://suite8demo.suiteondemand.com/#/Login"
}

print("Enviando petición...")
response = requests.post(url, headers=headers, json=data)
result = response.json()

if result["status"] == "error" and result.get("screenshot"):
    print(f"Error detectado: {result['detail']}")
    with open("debug_screenshot.jpg", "wb") as f:
        f.write(base64.b64decode(result["screenshot"]))
    print("Screenshot guardada como debug_screenshot.jpg")
else:
    print("Resultado:")
    print(json.dumps(result, indent=2))
