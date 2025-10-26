from ics import Calendar, Event
from datetime import datetime

# Crear calendario
calendar = Calendar()

# Datos de prueba: películas y sesiones por día
peliculas_por_dia = {
    "2025-10-26": {
        "Downton Abbey: El Gran Final": ["16:00", "20:30"],
        "La Deuda": ["18:00", "21:00"],
        "Los Domingos": ["16:15", "19:15"],
    },
    "2025-10-27": {
        "Downton Abbey: El Gran Final": ["16:00", "20:30"],
        "La Vida de Chuck": ["15:45", "19:00"],
        "Los Domingos": ["16:15", "19:15"],
    }
}

# Añadir eventos
for fecha, peliculas in peliculas_por_dia.items():
    for titulo, horas in peliculas.items():
        for hora in horas:
            e = Event()
            e.name = titulo
            e.begin = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
            e.location = "Cines Renoir Floridablanca"
            calendar.events.add(e)

# Guardar archivo .ics
with open("agenda-renoir.ics", "w", encoding="utf-8") as f:
    f.writelines(calendar)

print("✅ Archivo 'agenda-renoir.ics' generado con todas las sesiones.")
