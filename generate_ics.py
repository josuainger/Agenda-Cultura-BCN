import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime

# Crear un objeto Calendar
calendar = Calendar()

# URL de la página de calendario de Zumzeig
url = "https://zumzeigcine.coop/es/cine/calendari/"

# Realizar la solicitud HTTP para obtener el contenido de la página
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Buscar todos los elementos que contienen las sesiones
sessions = soup.find_all('div', class_='calendari_item')

# Iterar sobre cada sesión y extraer la información
for session in sessions:
    # Extraer el título de la película
    title = session.find('span', class_='calendari_titol').get_text(strip=True)
    
    # Extraer la fecha y hora de la sesión
    datetime_str = session.find('span', class_='calendari_datahora').get_text(strip=True)
    session_datetime = datetime.strptime(datetime_str, '%d.%m.%y (%a) %H:%M')
    
    # Crear un evento para el calendario
    event = Event()
    event.name = title
    event.begin = session_datetime
    event.location = "Zumzeig Cinecoop"
    event.url = url
    
    # Añadir el evento al calendario
    calendar.events.add(event)

# Guardar el calendario en un archivo .ics
with open('agenda-cultural-bcn.ics', 'w', encoding='utf-8') as f:
    f.writelines(calendar)

print("✅ Calendario generado: agenda-cultural-bcn.ics")
