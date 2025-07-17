from fastapi import FastAPI, UploadFile, Response
from fastapi.middleware.cors import CORSMiddleware
from logic import *  # <- Trenne deine Logik in eine andere Datei
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
import uvicorn
from pydantic import BaseModel

class BildRequest(BaseModel):
    punkt: str
    tag: str
    titel: str  # Auch wenn du ihn noch nicht brauchst, fürs Debugging wichtig!


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    #allow_origins=["http://localhost:8001", "http://localhost:5173",
    #"http://127.0.0.1:5173", "https://aldo597.github.io/generator/", "https://aldo597.github.io"],
    allow_origins=["*"],  # Erlaube alle Ursprünge für CORS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/wochen")
def get_wochen():
    # Gibt alle Wochen zurück (Liste)
    print("Hi")
    return {"wochen": get_weeks_from_text(read_website_text('https://www.europarl.europa.eu/plenary/en/votes.html?tab=votes#banner_session_live'))}



@app.get("/tage")
def get_tage(week: str):
    url = "https://www.europarl.europa.eu/plenary/en/votes.html?tab=votes#banner_session_live"
    return {"tage": tage_ausgeben(week, read_website_text(url))}


@app.get("/punkte")
def get_punkte(tag: str):
    # Gibt die Abstimmungspunkte eines Tags zurück
    link, _ = pdf_finden(url, tag)
    text1 = read_pdf_with_pdfplumber(link)
    struktur = parse_inhaltsverzeichnis(text1)
    return struktur

@app.post("/bild")
def bild_generieren(body: BildRequest):
    print("Titel empfangen:", body.titel)
    img_buffer = process_abstimmung(body.punkt, body.tag, body.titel)
    return StreamingResponse(img_buffer, media_type="image/png")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
