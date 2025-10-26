import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime

calendar = Calendar()
url = "https://zumzeigcine.coop/es/cine/calendari/"
res = requests.get(url)
soup = BeautifulSoup(res.text, "html.parser")

for day_section in soup.select(".calendari_dia"):
    day_str = day_section.select_one(".calendari_data").get_text(strip=True)
    day_date = datetime.strptime(day_str, "%d.%m.%y").date()

    for item in day_section.select(".calendari_item"):
        title = item.select_one(".calendari_titol").get_text(strip=True)
        time_str = item.select_one(".calendari_hora").get_text(strip=True)
        dt = datetime.strptime(f"{day_date} {time_str}", "%Y-%m-%d %H:%M")

        e = Event()
        e.name = title
        e.begin = dt
        e.location = "Zumzeig Cinecoop"
        e.url = url
        calendar.events.add(e)

with open("agenda-cultural-bcn.ics", "w", encoding="utf-8") as f:
    f.writelines(calendar)

print("✅ Calendario generado: agenda-cultural-bcn.ics")


print("✅ Calendario generado: agenda-cultural-bcn.ics")
