import requests
import matplotlib.pyplot as plt

REGION_ID = 122
URL = f"http://localhost:8000/api/analytics/region/{REGION_ID}"

response = requests.get(URL)
data = response.json()

if not isinstance(data, list):
    raise ValueError(f"Ожидался список, получено: {data}")

years = [
    item["year"]
    for item in data
    if item.get("population") is not None
]

population = [
    item["population"]
    for item in data
    if item.get("population") is not None
]

plt.figure()
plt.plot(years, population)
plt.xlabel("Год")
plt.ylabel("Численность населения")
plt.title("Динамика численности населения")
plt.grid(True)

plt.savefig("population.png")
plt.close()
