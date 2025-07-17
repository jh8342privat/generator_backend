import requests
from bs4 import BeautifulSoup
import re
import io
import pdfplumber
from collections import defaultdict
import xml.etree.ElementTree as ET
from collections import defaultdict
import os
import math
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import random


MAX_WIDTH = 70
COLUMN_COUNT = 4
PADDING = 12
LINE_HEIGHT = 35
ICON_SIZE = 32
REC_SIZE = 10
FONT_PATH = "PTSansProCondRg.OTF"  # oder "arial.ttf"
FONT2 = "PTSansProXBd.OTF"
FONT_SIZE = 28
FONT_SIZE2 = 42
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Pfad zum backend-Ordner
LOGO_PATH = os.path.join(BASE_DIR, "logos") 
COL_WIDTH = 270

COLOR_MAP = {
    "ja": "green",
    "nein": "red",
    "enthaltung": "orange",
    "nicht_abgestimmt": "grey"
}


# URL der Webseite, die du auslesen willst
url = 'https://www.europarl.europa.eu/plenary/en/votes.html?tab=votes#banner_session_live'  # ← Ersetze das mit deiner Ziel-URL


parteireihenfolge = [
            "Grune", "CDU", "CSU", "AfD", "SPD", "FDP",
            "Linke", "fw", 'BSW', "Volt", "Die Partei", "Piratenpartei",
            "ODP", "Tierschutzpartei", "Sonstige"
        ]

FRANKTIONSKÜRZEL = {
    "Fraktion der Progressiven Allianz der Sozialdemokraten im Europäischen Parlament": "S&D",
    "Fraktion Renew Europe": "Renew",
    "Fraktion der Europäischen Volkspartei (Christdemokraten)": "PPE",
    "Fraktion Patrioten für Europa": "PfE",
    "Fraktion der Europäischen Konservativen und Reformer": "ECR",
    "Fraktion Europa der Souveränen Nationen": "ESN",
    "Fraktion Die Linke im Europäischen Parlament - GUE/NGL": "The Left",
    "Fraktion der Grünen / Freie Europäische Allianz": "Verts/ALE",
    "Fraktionslos": "NI"
}

PARTEI_ABKÜRZUNGEN = {
    "Bündnis 90/Die Grünen": "Grune",
    "Sozialdemokratische Partei Deutschlands": "SPD",
    "Christlich Demokratische Union Deutschlands": "CDU",
    "Christlich-Soziale Union in Bayern e.V.": "CSU",
    "Freie Demokratische Partei": "FDP",
    "DIE LINKE.": "Linke",
    "Alternative für Deutschland": "AfD",
    'Partei Mensch Umwelt Tierschutz': 'Tierschutz',
    'Bündnis Sahra Wagenknecht – Vernunft und Gerechtigkeit': 'BSW',
    'Die PARTEI': 'Die Partei',
    'Freie Wähler': 'fw',
    'Ökologisch-Demokratische Partei': "ODP",
    'Familien-Partei Deutschlands': 'Familien Partei',
    'Partei des Fortschritts': 'PDF'
}

def read_website_text(url):
    response = requests.get(url)

    print('lolololo')
    # Prüfen, ob die Seite erreichbar war
    if response.status_code == 200:
        # HTML parsen
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Skripte und Styles entfernen
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()
        
        # Nur den reinen Text extrahieren
        text = soup.get_text()
        
        # Zeilen säubern
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return clean_text
    else:
        print(f"Fehler beim Abrufen der Seite: {response.status_code}")



# Dein kompletter Text als String (z. B. aus Datei oder Web Scraping)

def get_weeks_from_text(text):

    # Regulärer Ausdruck, um Woche + Ort zu erfassen
    pattern = re.compile(
        r"((?:Monday|Tuesday|Wednesday|Thursday|Friday), \d{1,2} \w+ 2025 - (?:Monday|Tuesday|Wednesday|Thursday|Friday), \d{1,2} \w+ 2025)\n(Strasbourg|Brussels)"
    )

    # Alle passenden Tupel extrahieren: (Woche, Ort)
    wochen = pattern.findall(text)

    return wochen


def tage_ausgeben(ausgewaehlte_woche, text):
        pattern = re.compile(
            re.escape(ausgewaehlte_woche) + r"\n(Strasbourg|Brussels)\n(.*?)(?=\n(?:Monday|Tuesday|Wednesday|Thursday|Friday))",
            re.DOTALLxx
        )

        match = pattern.search(text)

        if match:
            wocheninhalt = match.group(2)  # Das Textstück, das nur zu dieser Woche gehört

            # Finde alle Einzeltage in diesem Block
            tage = re.findall(r"(Monday|Tuesday|Wednesday|Thursday|Friday), \d{1,2} \w+ \d{4}", wocheninhalt)

            print("Ausgewählte Woche:")
            print(ausgewaehlte_woche)
            print("\nTage:")
            for tag in tage:
                print(tag)
            return tage
        else:
            print("Woche nicht gefunden oder Format stimmt nicht.")

def tage_ausgeben(ausgewaehlte_woche, text):

    # Muster: finde den Textabschnitt für die ausgewählte Woche + Ort
    pattern = re.compile(
        re.escape(ausgewaehlte_woche) + r"\n(Strasbourg|Brussels)\n(.*?)(?=\n(?:Monday|Tuesday|Wednesday|Thursday|Friday), \d{1,2} \w+ 2025 -|$)",
        re.DOTALL
    )

    match = pattern.search(text)

    if match:
        wocheninhalt = match.group(2)  # Textblock dieser Woche

        # Alle Einzeltage mit Datum (z.B. "Thursday, 13 March 2025") finden
        tage = re.findall(r"(Monday|Tuesday|Wednesday|Thursday|Friday), \d{1,2} \w+ 2025", wocheninhalt)
        
        # Das vorherige findall gibt nur die Wochentage zurück, wir ändern die Regex:
        tage_mit_datum = re.findall(r"(?:Monday|Tuesday|Wednesday|Thursday|Friday), \d{1,2} \w+ 2025", wocheninhalt)

        print("Ausgewählte Woche:")
        print(ausgewaehlte_woche)
        print("\nTage mit Datum:")
        for tag in tage_mit_datum:
            print(tag)
        return tage_mit_datum
    else:
        print("Woche nicht gefunden.")
        return []
        print("Woche nicht gefunden oder Format stimmt nicht.")

def pdf_finden(url, gesuchtes_datum):
    # Seite laden und parsen
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Datum finden
    datum_tag = None
    for tag in soup.find_all(string=gesuchtes_datum):
        datum_tag = tag.parent
        break

    if not datum_tag:
        print(f"Datum {gesuchtes_datum} nicht gefunden.")
        return None

    # Suche nach dem nächsten <ul>, darin nach .pdf-Links
    next_ul = datum_tag.find_next_sibling("ul")
    if next_ul:
        pdf_link = None
        for a_tag in next_ul.find_all("a", href=True):
            if a_tag["href"].lower().endswith(".pdf"):
                pdf_link = a_tag["href"]
                break
        for a_tag in next_ul.find_all("a", href=True):
            if a_tag["href"].lower().endswith(".xml"):
                xml_link = a_tag["href"]
                break

        if pdf_link:
            print(f"Gefundener PDF-Link für {gesuchtes_datum}: {pdf_link}")
            return pdf_link, xml_link
        else:
            print("Kein PDF-Link in der nächsten <ul>-Liste gefunden.")
    else:
        print("Kein <ul>-Element nach dem Datum gefunden.")

    return None

def read_pdf_with_pdfplumber(pdf_url):
    response = requests.get(pdf_url)
    response.raise_for_status()

    all_text = []

    with pdfplumber.open(io.BytesIO(response.content)) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:  # Nur nicht-leere Seiten
                all_text.append(text)

    return "\n\n".join(all_text)
    

def parse_inhaltsverzeichnis(text):
    struktur = defaultdict(list)
    current_key = None

    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Entferne Punkte und Seitenzahlen am Ende
        line = re.sub(r'\.{3,}\s*\d+$', '', line).strip()

        # Hauptpunkt erkennen (z.B. "1. Some Title")
        match_haupt = re.match(r'^(\d+)\.\s+(.*)$', line)
        if match_haupt:
            nummer = match_haupt.group(1)
            titel = match_haupt.group(2).strip()
            current_key = f"{nummer}. {titel}"
            struktur[current_key] = []
            continue

        # Unterpunkt erkennen (z.B. "1.1 Subtitle")
        match_unter = re.match(r'^(\d+\.\d+)\s+(.*)$', line)
        if match_unter and current_key:
            unter_titel = f"{match_unter.group(1)} {match_unter.group(2).strip()}"
            struktur[current_key].append(unter_titel)

    return dict(struktur)

def parse_vote_results_from_url(xml_url):
    response = requests.get(xml_url)
    response.raise_for_status()
    xml_content = response.content

    root = ET.fromstring(xml_content)
    results_dict = {}

    for vote in root.findall(".//RollCallVote.Result"):
        description = vote.findtext("RollCallVote.Description.Text")
        if not description:
            continue
        description = description.strip()
        vote_result = defaultdict(list)

        for result_type in ['For', 'Against', 'Abstention']:
            result_tag = vote.find(f"./Result.{result_type}")
            if result_tag is not None:
                for group in result_tag.findall("Result.PoliticalGroup.List"):
                    for member in group.findall("PoliticalGroup.Member.Name"):
                        name = member.text.strip()
                        pers_id = member.attrib.get("PersId")
                        vote_result[result_type].append({
                            "name": name,
                            "id": pers_id
                        })
                        
        intentions = vote.find("Intentions")
        if intentions is not None:
            for intention_result_type in ['For', 'Against', 'Abstention']:
                intention_tag = intentions.find(f"Intentions.Result.{intention_result_type}")
                if intention_tag is not None:
                    for member in intention_tag.findall("Member.Name"):
                        name = member.text.strip()
                        pers_id = member.attrib.get("PersId")

                        # Entferne aus allen bisherigen Kategorien
                        for key in vote_result:
                            vote_result[key] = [
                                m for m in vote_result[key]
                                if m["id"] != pers_id
                            ]

                        # Füge in neue Kategorie hinzu
                        vote_result[intention_result_type].append({
                            "name": name,
                            "id": pers_id
                        })

        results_dict[description] = dict(vote_result)

    return results_dict

def parse_meps_from_url(xml_url):
    response = requests.get(xml_url)
    response.raise_for_status()
    xml_content = response.content

    root = ET.fromstring(xml_content)
    mep_dict = {}

    for mep in root.findall(".//mep"):
        mep_id = mep.findtext("id")
        full_name = mep.findtext("fullName", "").strip()
        political_group = mep.findtext("politicalGroup", "").strip()
        national_group = mep.findtext("nationalPoliticalGroup", "").strip()

        mep_dict[mep_id] = {
            "full_name": full_name,
            "political_group": political_group,
            "national_political_group": national_group
        }

    return mep_dict

def normalize_partei(name):
    return PARTEI_ABKÜRZUNGEN.get(name, name)

def verarbeite_deutsche_abstimmungen(abstimmungen, deutsche_meps, parteireihenfolge, punkt, abstimmungstitel):
    result = {
        "titel_abstimmung": abstimmungstitel,
        "For": [],
        "Against": [],
        "Abstention": [],
        "not_voted": []
    }

    # IDs der bereits gewerteten deutschen Abgeordneten
    gewertete_ids = set()

    temp = abstimmungen[punkt]
    print(temp.keys())
    for entscheidung in temp.keys():
        fraktion_list = temp[entscheidung]
        print(entscheidung)
        for abgeordneter in fraktion_list:
                mep_id = abgeordneter.get("id")
                if mep_id in deutsche_meps:
                    info = deutsche_meps[mep_id]

                    national_party = normalize_partei(info["national_political_group"])

                    parts = info["full_name"].split()
                    nachnamen_teile = [teil.capitalize() for teil in parts if teil.isupper()]
                    vornamen_teile = [teil.capitalize() for teil in parts if not teil.isupper()]

                    if not nachnamen_teile:
                        nachname = parts[-1]
                        vorname = " ".join(parts[:-1])
                    else:
                        nachname = " ".join(nachnamen_teile)
                        vorname = " ".join(vornamen_teile)

                    if nachname == "Strack-zimmermann":
                        nachname = "Strack-Zimmermann"


                    result[entscheidung].append({
                        "name": nachname,
                        "vorname": vorname,
                        "partei": national_party,
                        "political_group": info["political_group"]
                    })
                    gewertete_ids.add(mep_id)

    # Jetzt bestimmen wir alle, die nicht abgestimmt haben
    for mep_id, info in deutsche_meps.items():
        if mep_id not in gewertete_ids:
            national_party = normalize_partei(info["national_political_group"])

            parts = info["full_name"].split()
            nachnamen_teile = [teil.capitalize() for teil in parts if teil.isupper()]
            vornamen_teile = [teil.capitalize() for teil in parts if not teil.isupper()]

            if not nachnamen_teile:
                nachname = parts[-1]
                vorname = " ".join(parts[:-1])
            else:
                nachname = " ".join(nachnamen_teile)
                vorname = " ".join(vornamen_teile)

            if nachname == "Strack-zimmermann":
                nachname = "Strack-Zimmermann"  

            result['not_voted'].append({
                        "name": nachname,
                        "vorname": vorname,
                        "partei": national_party,
                        "political_group": info["political_group"]
                    })

    # Hilfsfunktion zur Sortierung nach Partei + Alphabet
    def sort_key(mep):
        partei_index = parteireihenfolge.index(mep["partei"]) if mep["partei"] in parteireihenfolge else len(parteireihenfolge)
        return (partei_index, mep["name"].lower())

    for entscheidung in ["For", "Against", "Abstention", "not_voted"]:
        result[entscheidung].sort(key=sort_key)

    return result
def draw_block(img, draw, persons, label, y_offset, icon_color, font, font2, font3, logos):
    draw.rectangle([PADDING, y_offset - 2, PADDING + 10, y_offset + ICON_SIZE ], fill=icon_color)
    draw.text((PADDING + REC_SIZE + 13, y_offset), label, fill=icon_color, font=font2)
    
    #y_offset += LINE_HEIGHT
    persons.insert(0, {'name': '', 'vorname': '', 'partei': ''}) 
    rows = math.ceil(len(persons) / COLUMN_COUNT)

    for col in range(COLUMN_COUNT):
            for row in range(rows):

                index = row + rows * col 
                if index >= len(persons):
                    continue
                person = persons[index]

                if index == 0:
                    name = ''
                else:
                    name = f"{person['name']} {person['vorname'][0]}."
                if True:
                    if person['name'] == "Von Der Schulenburg":
                        name = "v. d. Schulenburg M."
                    
                    if person['name'] == "Strack-Zimmermann":
                        name = "Strack-Zimmermann M.-A."
                    
                    if person['name'] == "Warnke":
                        name = "Warnke J.-P."
                    
                    if person['name'] == "Oetjen":
                        name = "Oetjen J.-C."
                logo = logos.get(person["partei"], None)

                x = PADDING + col * COL_WIDTH
                y = y_offset + row * LINE_HEIGHT

                    # Rechteck (Zustimmungsindikator)
                draw.rectangle([x, y -2, x + 10, y + ICON_SIZE + 2], fill=icon_color)

                    # Text
                if name == "Strack-Zimmermann M.-A.":
                    draw.text((x + REC_SIZE + 13, y+3), name, fill="black", font=font3)
                else:
                    draw.text((x + REC_SIZE + 13, y), name, fill="black", font=font)

                    # Logo
                if logo:
                    img.paste(logo, (x + REC_SIZE + 250 - logo.width, y), logo)
                    

    return y_offset + rows * LINE_HEIGHT + LINE_HEIGHT

def load_logos():
    logos = {}
    for fname in os.listdir(LOGO_PATH):
        if fname.endswith(".png"):
            partei = fname.replace(".png", "")


            original_logo = Image.open(os.path.join(LOGO_PATH, fname)).convert("RGBA")
            # Calculate aspect ratio
            aspect_ratio = original_logo.width / original_logo.height
            new_width = int(ICON_SIZE * aspect_ratio)

            # Resize while preserving proportions
            logo = original_logo.resize((new_width, ICON_SIZE), Image.LANCZOS)

            # If it exceeds max width, scale it down again
            if logo.width > MAX_WIDTH:
                scale_ratio = MAX_WIDTH / logo.width
                new_width = MAX_WIDTH
                new_height = int(logo.height * scale_ratio)
                logo = logo.resize((new_width, new_height), Image.LANCZOS)
            
            logos[partei] = logo
    return logos

def wrap_text(text, font, max_width, draw):
    lines = []
    words = text.split()
    line = ""

    for word in words:
        test_line = line + word + " "
        bbox = font.getbbox(test_line)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            line = test_line
        else:
            lines.append(line.strip())
            line = word + " "

    if line:
        lines.append(line.strip())

    return lines




def generate_image_bytes(data):
    size4 = 42
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    font4 = ImageFont.truetype(FONT2, size4)
    font2 = ImageFont.truetype(FONT2, round(FONT_SIZE*0.9))
    font3 = ImageFont.truetype(FONT_PATH, round(FONT_SIZE *0.8))
    logos = load_logos()

    total_people = sum(len(data[k]) for k in ["ja", "nein", "enthaltung"])
    estimated_height = 1200 
    img = Image.new("RGBA", (1200, estimated_height), "white")
    draw = ImageDraw.Draw(img)

    wrapped_lines = wrap_text(data['title'], font4, img.width - 2 * PADDING, draw)
    y = PADDING 

    for line in wrapped_lines:
        bbox = draw.textbbox((0, 0), line, font=font4)
        line_width = bbox[2] - bbox[0]
        x1 = (img.width - line_width) // 2
        draw.text((x1, y), line, fill="black", font=font4)
        y += LINE_HEIGHT + round(size4 / 4)

    y = (PADDING + round(size4 / 2.8)) * len(wrapped_lines) + LINE_HEIGHT * 2 
    y = draw_block(img, draw, data["ja"], "DAFÜR", y, COLOR_MAP["ja"], font, font2, font3, logos)
    y = draw_block(img, draw, data["nein"], "DAGEGEN", y, COLOR_MAP["nein"], font, font2, font3, logos)
    y = draw_block(img, draw, data["enthaltung"], "ENTHALTEN", y, COLOR_MAP["enthaltung"], font, font2, font3, logos)
    y = draw_block(img, draw, data["nicht_abgestimmt"], "NICHT ABGESTIMMT", y, COLOR_MAP["nicht_abgestimmt"], font, font2, font3, logos)

    img = img.crop((0, 0, img.width, y + 2 * LINE_HEIGHT))  # Bild kürzen

    # 📌 Bild als Bytes zurückgeben:
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def übersetze_keys(abstimmungs_dict):
    key_mapping = {
        "titel_abstimmung": "title",
        "For": "ja",
        "Against": "nein",
        "Abstention": "enthaltung",
        "not_voted": "nicht_abgestimmt"
    }

    return {
        key_mapping.get(k, k): v for k, v in abstimmungs_dict.items()
    }

def process_abstimmung(punkt, tag, titel):
    xml_link = pdf_finden(url, tag)[1]
    vote_results = parse_vote_results_from_url(xml_link)
    mep_link = "https://www.europarl.europa.eu/meps/de/download/advanced/xml?countryCode=DE"
    mep_dict = parse_meps_from_url(mep_link)

    s = re.sub(r'^\d+\.\d+\s+', '', punkt)
    ergebnis = verarbeite_deutsche_abstimmungen(
        abstimmungen=vote_results,
        deutsche_meps=mep_dict,
        parteireihenfolge=parteireihenfolge,
        punkt = s.strip(),
        abstimmungstitel=titel.strip()
    )
    auswertung = übersetze_keys(ergebnis)

    # Rückgabe als Byte-Stream statt Dateipfad
    return generate_image_bytes(auswertung)

