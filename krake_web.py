#!/usr/bin/env python3
"""
krake_web.py — Oeffentliche Tuer der Hilfe-Krake (K5)

Versionsstand: v1 (13.07.2026)

Etappe: Krake-Strecke K5. Richtung: Website -> Endpunkt -> beantworte(quelle="website").

Leitplanken (fest):
  * Dienst hoert NUR auf 127.0.0.1:8504 (gunicorn via systemd). Der Cloudflare-
    Tunnel bringt ihn nach aussen. KEIN Cloudflare Access davor -> oeffentliche Tuer.
  * Importiert AUSSCHLIESSLICH `beantworte` aus app_hilfe_krake. Dessen Startwache
    oeffnet nur app_hilfe.lancedb -> Kundenwissen ist physisch unerreichbar.
  * Schnittstellen-Vertrag (mit W1 festgezurrt): POST /frage, Body {"frage": "..."},
    Antwort IMMER HTTP 200 mit {"antwort": "..."} -- auch Deckel-, Fehler- und
    Abwehr-Meldungen. Alles andere -> 404 ohne Inhalt.
  * Drei Schutzschichten (Sonjas Entscheide):
      1. Tagesdeckel 100 beantwortete Fragen gesamt -> danach fester Satz OHNE Haiku.
      2. Blitzschutz pro IP ~6/min (nur RAM) -> Durchatmen-Satz OHNE Haiku.
      3. Bei Deckel-Riss EINE Mail/Tag an Sonja (aggregiert, KEINE Fragetexte).
  * Stille Haertungen: Frage > 500 Zeichen -> Hinweis OHNE Haiku. Fail-soft:
    jede Exception -> 200 + freundlicher Satz, nie Traceback nach aussen.
  * IP + Fragetext werden NIEMALS zusammen persistiert. Der Tageszaehler haelt nur
    aggregierte IP-Anzahlen (fuer die Mail) und wird um Mitternacht komplett neu.
  * Alle Stellschrauben aus der Umgebung (systemd EnvironmentFile), nichts im Code.
  * API-Keys (ANTHROPIC/MISTRAL) kommen ueber scripts/.env, geladen beim Import
    des Krake-Hirns -- nicht in dieser env-Datei.
"""

import os
import sys
import json
import time
import fcntl
import logging
import threading
import smtplib
from pathlib import Path
from datetime import date
from email.mime.text import MIMEText

from flask import Flask, request, jsonify

# --------------------------------------------------------------------------- #
# Workspace-Root in sys.path (identisches Muster wie app_hilfe_krake.py).
# Dadurch traegt `from scripts import ...` unabhaengig von WorkingDirectory.
# --------------------------------------------------------------------------- #
_WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(_WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE_ROOT))

# Import des Krake-Hirns. Die Startwache im Modul laeuft beim Import und wirft,
# falls jemand versucht, etwas anderes als app_hilfe.lancedb zu oeffnen.
# Der Import laedt ausserdem scripts/.env (ANTHROPIC/MISTRAL-Keys).
from scripts.app_hilfe_krake import beantworte  # noqa: E402

# --------------------------------------------------------------------------- #
# Konfiguration / Stellschrauben (alles aus der Umgebung)
# --------------------------------------------------------------------------- #
TAGESDECKEL = int(os.environ.get("KRAKE_TAGESDECKEL", "100"))
IP_PRO_MIN = int(os.environ.get("KRAKE_IP_PRO_MIN", "6"))
MAX_ZEICHEN = int(os.environ.get("KRAKE_MAX_ZEICHEN", "500"))
ALLOW_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "KRAKE_ALLOW_ORIGINS",
        "https://firmenwissen-retten.de,https://www.firmenwissen-retten.de",
    ).split(",")
    if o.strip()
]
ZAEHLER_PFAD = Path(os.environ.get("KRAKE_ZAEHLER_PFAD", "/mnt/moltdata/krake_web/zaehler.json"))
LOG_PATH = Path(os.environ.get("KRAKE_WEB_LOG", "/mnt/moltdata/logs/krake_web.log"))

# Mail bei Deckel-Riss (leere Creds = Mailversand AUS, nur Log)
SMTP_HOST = os.environ.get("KRAKE_SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("KRAKE_SMTP_PORT", "587"))
SMTP_USER = os.environ.get("KRAKE_SMTP_USER", "")
SMTP_PASS = os.environ.get("KRAKE_SMTP_PASS", "")
MAIL_EMPFAENGER = os.environ.get("KRAKE_MAIL_EMPFAENGER", "")
MAIL_ABSENDER = os.environ.get("KRAKE_MAIL_ABSENDER", SMTP_USER)

# Feste, KOSTENLOSE Antworttexte (kein Haiku, kein Embedding)
TXT_LEER = "Stell mir gern eine Frage rund um die App und das Retten von Firmenwissen."
TXT_ZU_LANG = "Das ist eine ganze Menge auf einmal — magst du die Frage etwas kuerzer fassen?"
TXT_BLITZ = "Einen Moment bitte kurz durchatmen — gleich beantworte ich deine naechste Frage."
TXT_DECKEL = "Ich habe heute schon viele Fragen beantwortet — morgen bin ich wieder fuer dich da."
TXT_FEHLER = "Da ist mir gerade etwas dazwischengekommen — magst du es gleich noch einmal versuchen?"

# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #
try:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=str(LOG_PATH),
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
except Exception:
    logging.basicConfig(level=logging.INFO)
log = logging.getLogger("krake_web")

# --------------------------------------------------------------------------- #
# App + Zustand
# --------------------------------------------------------------------------- #
app = Flask(__name__)

_ram_lock = threading.Lock()
_ip_fenster: dict = {}  # ip -> [zeitstempel]  (nur RAM, Blitzschutz)


def _client_ip() -> str:
    """Echte Besucher-IP. Hinter cloudflared ist remote_addr = localhost!"""
    ip = request.headers.get("CF-Connecting-IP")
    if ip:
        return ip.strip()
    xff = request.headers.get("X-Forwarded-For", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.remote_addr or "unbekannt"


def _blitz_ok(ip: str) -> bool:
    """Schutzschicht 2: max. IP_PRO_MIN Fragen pro 60s je IP. Nur RAM."""
    now = time.time()
    with _ram_lock:
        fenster = [t for t in _ip_fenster.get(ip, []) if now - t < 60]
        if len(fenster) >= IP_PRO_MIN:
            _ip_fenster[ip] = fenster
            return False
        fenster.append(now)
        _ip_fenster[ip] = fenster
        # gelegentlich abgelaufene IPs ausraeumen, damit der Speicher nicht waechst
        if len(_ip_fenster) > 5000:
            for k in list(_ip_fenster):
                if all(now - t >= 60 for t in _ip_fenster[k]):
                    del _ip_fenster[k]
        return True


def _frischer_zaehler() -> dict:
    return {"datum": date.today().isoformat(), "beantwortet": 0, "ip_zaehler": {}, "mail_gesendet": False}


def _lade_zaehler(fh) -> dict:
    fh.seek(0)
    roh = fh.read()
    if not roh.strip():
        return _frischer_zaehler()
    try:
        d = json.loads(roh)
    except Exception:
        d = {}
    if d.get("datum") != date.today().isoformat():
        return _frischer_zaehler()  # Reset um Mitternacht -> IPs verschwinden mit
    d.setdefault("beantwortet", 0)
    d.setdefault("ip_zaehler", {})
    d.setdefault("mail_gesendet", False)
    return d


def _schreibe_zaehler(fh, d: dict) -> None:
    fh.seek(0)
    fh.truncate()
    fh.write(json.dumps(d, ensure_ascii=False))
    fh.flush()
    os.fsync(fh.fileno())


def _deckel_pruefen_und_zaehlen(ip: str):
    """Schutzschicht 1 + 3.

    Returns (erlaubt, deckel_text, mail_snapshot).
      erlaubt=True  -> Frage darf beantwortet werden (kostet Haiku).
      erlaubt=False -> Deckel gerissen, deckel_text zurueckgeben (kostenlos).
      mail_snapshot -> dict fuer die EINE Mail bei erstem Riss, sonst None.
    """
    ZAEHLER_PFAD.parent.mkdir(parents=True, exist_ok=True)
    with open(ZAEHLER_PFAD, "a+", encoding="utf-8") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            d = _lade_zaehler(fh)
            # jede ankommende (bereits laengen- und blitzgepruefte) Frage zaehlt je IP
            d["ip_zaehler"][ip] = d["ip_zaehler"].get(ip, 0) + 1

            if d["beantwortet"] >= TAGESDECKEL:
                riss_jetzt = not d["mail_gesendet"]
                if riss_jetzt:
                    d["mail_gesendet"] = True
                snapshot = dict(d) if riss_jetzt else None
                _schreibe_zaehler(fh, d)
                return False, TXT_DECKEL, snapshot

            d["beantwortet"] += 1
            _schreibe_zaehler(fh, d)
            return True, None, None
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def _mail_deckel(snapshot: dict) -> None:
    """EINE Mail bei Deckel-Riss. Aggregiert, ohne Fragetexte (Muster Quellenradar)."""
    if not (SMTP_USER and SMTP_PASS and MAIL_EMPFAENGER):
        log.info("Deckel gerissen, Mailversand AUS (keine SMTP-Creds) — nur Log.")
        return
    top = sorted(snapshot.get("ip_zaehler", {}).items(), key=lambda kv: kv[1], reverse=True)[:10]
    zeilen = "\n".join(f"  {ip}: {n}" for ip, n in top) or "  (keine)"
    text = (
        f"Die Krake-Website hat heute ({snapshot.get('datum')}) den Tagesdeckel von "
        f"{TAGESDECKEL} beantworteten Fragen erreicht.\n\n"
        f"Aktivste IPs heute (aggregiert, ohne Fragetexte):\n{zeilen}\n\n"
        f"Kein Handlungsbedarf, wenn das echtes Interesse ist. Eine einzelne IP mit "
        f"sehr vielen Anfragen deutet eher auf einen Bot hin."
    )
    msg = MIMEText(text, _charset="utf-8")
    msg["Subject"] = "Krake-Website: Tagesdeckel erreicht"
    msg["From"] = MAIL_ABSENDER
    msg["To"] = MAIL_EMPFAENGER
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
        log.info("Deckel-Mail an %s gesendet.", MAIL_EMPFAENGER)
    except Exception:
        log.exception("Deckel-Mail konnte nicht gesendet werden.")


# --------------------------------------------------------------------------- #
# CORS: Access-Control-Allow-Origin gibt die WEBSITE-Herkunft zurueck
# (nicht die krake-Subdomain!). Ohne diese Kopfzeilen schweigt die Krake im
# Browser, obwohl curl funktioniert -> Pflicht-Pruefpunkt.
# --------------------------------------------------------------------------- #
@app.after_request
def _cors(resp):
    origin = request.headers.get("Origin", "")
    if origin in ALLOW_ORIGINS:
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Vary"] = "Origin"
        resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


@app.route("/frage", methods=["POST", "OPTIONS"])
def frage():
    if request.method == "OPTIONS":
        return ("", 204)  # Preflight; CORS-Header setzt _cors()
    try:
        daten = request.get_json(silent=True) or {}
        text = (daten.get("frage") or "").strip()

        if not text:
            return jsonify(antwort=TXT_LEER)
        if len(text) > MAX_ZEICHEN:
            return jsonify(antwort=TXT_ZU_LANG)

        ip = _client_ip()
        if not _blitz_ok(ip):
            return jsonify(antwort=TXT_BLITZ)

        erlaubt, deckel_text, snapshot = _deckel_pruefen_und_zaehlen(ip)
        if not erlaubt:
            if snapshot is not None:
                _mail_deckel(snapshot)
            return jsonify(antwort=deckel_text)

        # einziger kostenpflichtiger Pfad: Haiku + Embedding, gebucht unter
        # mandant="system" im Krake-Hirn. Unbeantwortete Fragen loggt das Modul
        # selbst mit quelle="website" (K2-Kreislauf) -- gratis, nichts extra.
        antwort = beantworte(text, quelle="website")
        return jsonify(antwort=antwort)

    except Exception:
        log.exception("Fehler in /frage")
        return jsonify(antwort=TXT_FEHLER)


# Alles ausser POST/OPTIONS /frage -> 404 ohne Inhalt.
@app.errorhandler(404)
def _404(_e):
    return ("", 404)


@app.errorhandler(405)
def _405(_e):
    return ("", 404)


if __name__ == "__main__":
    # Nur lokaler Handbetrieb. Produktiv laeuft der Dienst unter gunicorn/systemd.
    port = int(os.environ.get("KRAKE_WEB_PORT", "8504"))
    app.run(host="127.0.0.1", port=port)
