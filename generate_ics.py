import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime

calendar = Calendar()

# --- Función auxiliar ---
def add_event(title, date, url, location):
    e = Event()
    e.name = title
    e.begin = date
    e.url = url
    e.location = location
    calendar.events.add(e)

# --- ZUMZEIG ---
try:
    res = requests.get("https://zumzeigcine.coop/es/cine/calendari/")
    soup = BeautifulSoup(res.text, "html.parser")
    for item in soup.select(".event-item"):
        title = item.get_text(strip=True)
        date = datetime.now().strftime("%Y-%m-%d")
        add_event(f"Zumzeig – {title}", date, "https://zumzeigcine.coop/es/cine/calendari/", "Zumzeig Cinecoop")
except Exception as e:
    print("Error Zumzeig:", e)

# --- SALA BECKETT ---
try:
    res = requests.get("https://www.salabeckett.cat/espectacles/")
    soup = BeautifulSoup(res.text, "html.parser")
    for item in soup.select(".event-item, .listing__item"):
        title = item.get_text(strip=True)
        date = datetime.now().strftime("%Y-%m-%d")
        add_event(f"Sala Beckett – {title}", date, "https://www.salabeckett.cat/espectacles/", "Sala Beckett")
except Exception as e:
    print("Error Beckett:", e)

# --- FLORIDABLANCA ---
try:
    res = requests.get("https://www.cinesrenoir.com/cine/renoir-floridablanca/cartelera/")
    soup = BeautifulSoup(res.text, "html.parser")
    for item in soup.select(".movie-item h3, .movie-title"):
        title = item.get_text(strip=True)
        date = datetime.now().strftime("%Y-%m-%d")
        add_event(f"Renoir Floridablanca – {title}", date, "https://www.cinesrenoir.com/cine/renoir-floridablanca/cartelera/", "Renoir Floridablanca")
except Exception as e:
    print("Error Floridablanca:", e)

# --- CCCB ---
try:
    res = requests.get("https://www.cccb.org/ca/programa")
    soup = BeautifulSoup(res.text, "html.parser")
    for item in soup.select(".program__title"):
        title = item.get_text(strip=True)
        date = datetime.now().strftime("%Y-%m-%d")
        add_event(f"CCCB – {title}", date, "https://www.cccb.org/ca/programa", "CCCB")
except Exception as e:
    print("Error CCCB:", e)

# --- GUARDAR ICS ---
with open("agenda-cultural-bcn.ics", "w", encoding="utf-8") as f:
    f.writelines(calendar)

print("✅ Calendari generat: agenda-cultural-bcn.ics")
