import matplotlib.pyplot as plt
import requests

REGION_ID = 122

response = requests.get(
    f"http://localhost:8000/api/analytics/region/{REGION_ID}"
)

data = response.json()

if not isinstance(data, list):
    raise ValueError(f"Ожидался список, получено: {data}")

years = [
    item["year"]
    for item in data
    if item.get("unemployment_rate") is not None
]

values = [
    item["unemployment_rate"]
    for item in data
    if item.get("unemployment_rate") is not None
]

plt.figure()
plt.plot(years, values)
plt.xlabel("Год")
plt.ylabel("Уровень безработицы, %")
plt.title("Динамика уровня безработицы")
plt.grid(True)

plt.savefig("unemployment.png")
plt.close()
