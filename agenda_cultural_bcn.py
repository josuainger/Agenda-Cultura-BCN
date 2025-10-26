#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agenda_cultural_bcn.py
Script en català que recull la programació de diverses webs i genera AgendaCulturalBCN.ics
Rang temporal: pròximes 2 setmanes.
Sortida: AgendaCulturalBCN.ics
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, time
from dateutil import parser as dateparser
from icalendar import Calendar, Event, vCalAddress, vText
import pytz
import re

# ------- CONFIGURACIÓ -------
TZ = pytz.timezone('Europe/Madrid')
OUTPUT_ICS = "AgendaCulturalBCN.ics"
RANG_DIES = 14  # pròximes 2 setmanes

# Fonts (afegir més si cal)
SOURCES = [
    ("Zumzeig", "https://zumzeigcine.coop/es/cine/calendari/"),
    ("Sala Beckett", "https://www.salabeckett.cat/espectacles/"),
    ("Renoir Floridablanca", "https://www.cinesrenoir.com/cine/renoir-floridablanca/cartelera/"),
    ("CCCB", "https://www.cccb.org/ca/programa"),
]

# ------- FUNCIONS D'AJUT -------
def get_soup(url, timeout=15):
    headers = {"User-Agent": "AgendaCulturalBCN/1.0 (+https://github.com/)"}
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")

def normalize_dt(date_obj):
    """Assegura que l'objecte datetime té timezone."""
    if date_obj.tzinfo is None:
        return TZ.localize(date_obj)
    return date_obj.astimezone(TZ)

def within_range(dt):
    now = datetime.now(TZ)
    end = now + timedelta(days=RANG_DIES)
    return now <= dt <= end

def try_parse_time(date_str, fallback_time=time(20,0)):
    """Intenta parsejar una data/hora; si només hi ha hora, l'aplica a data actual."""
    try:
        dt = dateparser.parse(date_str, dayfirst=True)
        return dt
    except Exception:
        # si no es pot, retornar None per tractar-ho a cada parser
        return None

# ------- PARSERS PER CADA FONT -------
def parse_zumzeig(url):
    """Retorna llista d'esdeveniments: dict(titol, dt_start, dt_end, lloc, link, desc)"""
    events = []
    soup = get_soup(url)
    # Observació: la web del Zumzeig presenta un calendari per dies; busquem articles o entrades
    # Estratègia: buscar elements amb classe que continguin 'session' o 'movie' i extreure titol, data, hora.
    # **Aquest parser pot caldre ajustar segons HTML real.**
    for card in soup.select(".cartelera__element, .entry, article, .film"):  # selectors alternatius
        try:
            title = None
            # títol
            t = card.select_one("h2, h3, .title, .film-title")
            if t:
                title = t.get_text(strip=True)
            # link
            a = card.select_one("a")
            link = a['href'] if a and a.has_attr('href') else url
            # data i hora - provar trobar text amb un patró 'dd/mm/yyyy' o 'Dia, 20:00'
            text = card.get_text(" ", strip=True)
            # cerca d'hora tipus 20:00
            m = re.search(r'(\d{1,2}[:h]\d{2})', text)
            hour_str = m.group(1).replace('h', ':') if m else None
            # cerca de data (format dia mes o dd/mm)
            # intentem extreure prop de l'element .date si existeix
            date_el = card.select_one(".date, .fecha, .session-date")
            if date_el:
                date_txt = date_el.get_text(" ", strip=True)
                dt_try = try_parse_time(f"{date_txt} {hour_str}" if hour_str else date_txt)
            else:
                # buscar una data al text
                mdate = re.search(r'(\d{1,2}/\d{1,2}/\d{2,4})', text) or re.search(r'(\d{1,2} de [A-Za-z]+ de \d{4})', text)
                if mdate:
                    date_txt = mdate.group(1)
                    dt_try = try_parse_time(f"{date_txt} {hour_str}" if hour_str else date_txt)
                else:
                    dt_try = None
            if dt_try:
                dt = normalize_dt(dt_try)
                if within_range(dt):
                    events.append({
                        "title": title or "Projecció Zumzeig",
                        "start": dt,
                        "end": dt + timedelta(hours=2),  # durada per defecte 2h (ajustable)
                        "place": "Cine Zumzeig",
                        "link": link,
                        "desc": text
                    })
        except Exception:
            continue
    return events

def parse_sala_beckett(url):
    events = []
    soup = get_soup(url)
    # La Sala Beckett té una llista d'espectacles; cada element normalment conté títol i dates.
    for item in soup.select(".espectacle, .item, article"):  # selectors genèrics
        try:
            title_el = item.select_one("h2, h3, .title")
            title = title_el.get_text(strip=True) if title_el else "Espectacle Beckett"
            link_el = item.select_one("a")
            link = link_el['href'] if link_el and link_el.has_attr('href') else url
            text = item.get_text(" ", strip=True)
            # buscar data/hora dins el text
            m_date = re.search(r'(\d{1,2}\s*(de)?\s*[A-Za-z]+(?:\s*de\s*\d{4})?)', text)
            m_time = re.search(r'(\d{1,2}[:h]\d{2})', text)
            if m_date:
                date_txt = m_date.group(1)
                dt_try = try_parse_time(f"{date_txt} {m_time.group(1).replace('h',':') if m_time else ''}")
                if dt_try:
                    dt = normalize_dt(dt_try)
                    if within_range(dt):
                        events.append({
                            "title": title,
                            "start": dt,
                            "end": dt + timedelta(hours=2),
                            "place": "Sala Beckett",
                            "link": link,
                            "desc": text
                        })
        except Exception:
            continue
    return events

def parse_renoir_floridablanca(url):
    events = []
    soup = get_soup(url)
    # Renoir sol mostrar sessions per dia; buscarem elements de cartelera
    for film in soup.select(".pelicula, .movie, .card"):
        try:
            title_el = film.select_one(".title, h2, h3")
            title = title_el.get_text(strip=True) if title_el else "Sessió Renoir"
            # Horaris dins del bloc
            text = film.get_text(" ", strip=True)
            times = re.findall(r'(\d{1,2}[:h]\d{2})', text)
            # intentar extreure la data general de la pàgina (si és per dia)
            # si la pàgina inclou seccions per data, agafar la data del parent
            parent_date = None
            parent = film.find_parent()
            if parent:
                date_el = parent.select_one(".date, .dia, .cartelera-date")
                if date_el:
                    parent_date = date_el.get_text(strip=True)
            # si hi ha times, crear esdeveniments per cada hora propera dins de les dues setmanes
            for t in times:
                tnorm = t.replace('h',':')
                # si hi ha parent_date, fer parse
                dt_try = None
                if parent_date:
                    dt_try = try_parse_time(f"{parent_date} {tnorm}")
                else:
                    # intentar parsejar text que contingui data pròxima
                    # com a fallback, assignar a avui + buscar properes 14 dies
                    # Aquí assumim que si no hi ha data, la sessió és avui; s'ha d'ajustar manualment si cal
                    dt_try = try_parse_time(tnorm)
                if dt_try:
                    dt = normalize_dt(dt_try)
                    if within_range(dt):
                        link_el = film.select_one("a")
                        link = link_el['href'] if link_el and link_el.has_attr('href') else url
                        events.append({
                            "title": title,
                            "start": dt,
                            "end": dt + timedelta(hours=2),
                            "place": "Cine Renoir Floridablanca",
                            "link": link,
                            "desc": text
                        })
        except Exception:
            continue
    return events

def parse_cccb(url):
    events = []
    soup = get_soup(url)
    # CCCB té una llista de programació amb dates ben marcades
    for item in soup.select(".item, .programa, .card"):
        try:
            title_el = item.select_one("h3, h2, .title")
            title = title_el.get_text(strip=True) if title_el else "Activitat CCCB"
            link_el = item.select_one("a")
            link = link_el['href'] if link_el and link_el.has_attr('href') else url
            text = item.get_text(" ", strip=True)
            # CCCB sol tenir una data clara; busquem yyyy-mm-dd o formats dd/mm/yyyy o '15 octubre 2025'
            m = re.search(r'(\d{1,2}\s+[A-Za-z]+(?:\s+\d{4})?)', text)
            time_m = re.search(r'(\d{1,2}[:h]\d{2})', text)
            if m:
                date_txt = m.group(1)
                dt_try = try_parse_time(f"{date_txt} {time_m.group(1).replace('h',':') if time_m else ''}")
                if dt_try:
                    dt = normalize_dt(dt_try)
                    if within_range(dt):
                        events.append({
                            "title": title,
                            "start": dt,
                            "end": dt + timedelta(hours=2),
                            "place": "CCCB",
                            "link": link,
                            "desc": text
                        })
        except Exception:
            continue
    return events

# ------- AGREGACIÓ I CREACIÓ ICS -------
def generar_ics(events, output_path=OUTPUT_ICS):
    cal = Calendar()
    cal.add('prodid', '-//Agenda Cultural BCN//github.com//')
    cal.add('version', '2.0')
    cal.add('X-WR-CALNAME', 'Agenda Cultural BCN')
    cal.add('X-WR-TIMEZONE', str(TZ))

    for ev in events:
        try:
            e = Event()
            e.add('summary', ev['title'])
            e.add('dtstart', ev['start'])
            e.add('dtend', ev['end'])
            e.add('description', f"{ev.get('desc','')}\n\nEnllaç: {ev.get('link','')}")
            e.add('location', ev.get('place',''))
            # UID únic (títol + start a ISO)
            uid = f"{re.sub(r'[^a-zA-Z0-9]','',ev['title'])}-{ev['start'].strftime('%Y%m%dT%H%M%S')}"
            e.add('uid', uid)
            cal.add_component(e)
        except Exception as ex:
            print("Error creant esdeveniment:", ex)
            continue

    with open(output_path, 'wb') as f:
        f.write(cal.to_ical())
    print(f"Fitxer .ics creat: {output_path} amb {len(events)} esdeveniments.")

# ------- FLUX PRINCIPAL -------
def main():
    tots = []
    print("Iniciant recollida d'esdeveniments...")
    # Zumzeig
    try:
        print("-> Zumzeig")
        tots += parse_zumzeig(SOURCES[0][1])
    except Exception as e:
        print("Error Zumzeig:", e)
    # Beckett
    try:
        print("-> Sala Beckett")
        tots += parse_sala_beckett(SOURCES[1][1])
    except Exception as e:
        print("Error Beckett:", e)
    # Renoir
    try:
        print("-> Renoir Floridablanca")
        tots += parse_renoir_floridablanca(SOURCES[2][1])
    except Exception as e:
        print("Error Renoir:", e)
    # CCCB
    try:
        print("-> CCCB")
        tots += parse_cccb(SOURCES[3][1])
    except Exception as e:
        print("Error CCCB:", e)

    # Ordenar per data
    tots_sorted = sorted(tots, key=lambda x: x['start'])
    # Filtrar duplicats simples (mateix títol i hora)
    unique = []
    seen = set()
    for e in tots_sorted:
        key = (e['title'], e['start'].strftime('%Y%m%d%H%M'))
        if key not in seen:
            seen.add(key)
            unique.append(e)

    generar_ics(unique)
    print("Finalitzat.")

if __name__ == "__main__":
    main()
