import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime, timedelta

# Crear calendario
calendar = Calendar()

# --- ZUMZEIG ---
try:
    url = "https://zumzeigcine.coop/es/cine/calendari/"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    events = soup.select(".calendari_item")  # selector Zumzeig (puede cambiar)
    
    for item in events:
        title = item.get_text(strip=True)
        date = datetime.now() + timedelta(days=1)  # día de prueba (puedes ajustar)
        e = Event()
        e.name = f"Zumzeig – {title}"
        e.begin = date.strftime("%Y-%m-%d 19:00:00")  # hora fija de ejemplo
        e.location = "Zumzeig Cinecoop"
        e.url = url
        calendar.events.add(e)
except Exception as ex:
    print("Error Zumzeig:", ex)

# Guardar calendario
with open("agenda-cultural-bcn.ics", "w", encoding="utf-8") as f:
    f.writelines(calendar)

print("✅ Calendario generado: agenda-cultural-bcn.ics")
