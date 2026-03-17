import requests
import matplotlib.pyplot as plt

YEAR = 2021
URL = f"http://localhost:8000/api/analytics/top-unemployment?year={YEAR}&limit=10"

response = requests.get(URL)
data = response.json()

if not isinstance(data, list):
    raise ValueError(f"Ожидался список, получено: {data}")

regions = [item["region_name"] for item in data]
values = [item["unemployment_rate"] for item in data]

plt.figure(figsize=(10, 6))
plt.barh(regions, values)
plt.xlabel("Уровень безработицы, %")
plt.title(f"Топ-10 регионов с самой низкой безработицей ({YEAR})")
plt.grid(True)

plt.subplots_adjust(left=0.35)
plt.savefig("top_unemployment.png", dpi=300)
plt.close()
