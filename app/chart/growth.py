import requests
import matplotlib.pyplot as plt

REGION_ID = 122
URL = f"http://localhost:8000/api/analytics/region/{REGION_ID}/growth"

response = requests.get(URL)
data = response.json()

if not isinstance(data, list):
    raise ValueError(f"Ожидался список, получено: {data}")

years = [item["year"] for item in data]

population_growth = [
    item["population_growth_pct"]
    for item in data
]

unemployment_growth = [
    item["unemployment_growth_pct"]
    for item in data
]

plt.figure()
plt.plot(years, population_growth, label="Население")
plt.plot(years, unemployment_growth, label="Безработица")
plt.xlabel("Год")
plt.ylabel("Темп роста, %")
plt.title("Темпы роста населения и безработицы")
plt.legend()
plt.grid(True)

plt.savefig("growth_rates.png")
plt.close()
