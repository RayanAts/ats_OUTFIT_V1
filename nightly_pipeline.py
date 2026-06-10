# ============================================
# NIGHTLY PIPELINE - Supabase
# ============================================
import os
import json
import subprocess
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client
import random

load_dotenv(r"C:\Projects\smartwardrobe\.env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DBT_DIR      = r"C:\Projects\smartwardrobe\ats_outfit"
DBT_ENV      = r"C:\Projects\smartwardrobe\dbt-env\Scripts\dbt.exe"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# ── Météo ─────────────────────────────────────────────────────────────────────
def update_weather():
    log("Mise à jour météo...")

    params = {
        "latitude":  48.8566,
        "longitude": 2.3522,
        "current":   ["temperature_2m", "weathercode", "precipitation"],
        "daily":     ["temperature_2m_max", "temperature_2m_min",
                      "precipitation_sum", "windspeed_10m_max", "weathercode"],
        "timezone":  "Europe/Paris",
        "forecast_days": 1
    }

    r       = requests.get("https://api.open-meteo.com/v1/forecast", params=params)
    raw     = r.json()
    current = raw["current"]
    daily   = raw["daily"]
    today   = datetime.today().strftime("%Y-%m-%d")

    temp_max = daily["temperature_2m_max"][0]
    temp_min = daily["temperature_2m_min"][0]
    temp_avg = round((temp_max + temp_min) / 2, 1)
    wcode    = daily["weathercode"][0]

    weather_labels = {
        0: "Ciel dégagé", 1: "Nuageux", 2: "Nuageux", 3: "Nuageux",
        45: "Brouillard", 48: "Brouillard",
        51: "Pluie", 53: "Pluie", 55: "Pluie",
        61: "Pluie", 63: "Pluie", 65: "Pluie",
        71: "Neige", 73: "Neige", 75: "Neige",
        80: "Averses", 81: "Averses", 82: "Averses",
        95: "Orage", 96: "Orage", 99: "Orage"
    }
    label = weather_labels.get(wcode, "Nuageux")

    if temp_avg >= 20:   warmth = 1
    elif temp_avg >= 12: warmth = 2
    elif temp_avg >= 5:  warmth = 3
    else:                warmth = 4

    record = {
        "fetch_date":          today,
        "fetch_time":          datetime.now().strftime("%H:%M"),
        "ville":               "Paris",
        "temp_actuelle":       current["temperature_2m"],
        "temp_max":            temp_max,
        "temp_min":            temp_min,
        "temp_moyenne":        temp_avg,
        "precipitation_mm":    daily["precipitation_sum"][0],
        "vitesse_vent_max":    daily["windspeed_10m_max"][0],
        "weathercode":         wcode,
        "label_meteo":         label,
        "chaleur_recommandee": warmth
    }

    # Supprimer l'ancienne météo du jour si elle existe
    supabase.table("meteo").delete().eq("fetch_date", today).execute()
    supabase.table("meteo").insert(record).execute()

    log(f"✅ Météo mise à jour : {current['temperature_2m']}°C à Paris")

# ── Calendrier ────────────────────────────────────────────────────────────────
def update_calendar():
    log("Mise à jour calendrier...")

    context_types = [
        {"type_contexte": "bureau",         "label_contexte": "Semi-formel", "formalite_requise": 3, "exposition_exterieure": False},
        {"type_contexte": "réunion_client", "label_contexte": "Formel",      "formalite_requise": 5, "exposition_exterieure": False},
        {"type_contexte": "casual",         "label_contexte": "Casual",      "formalite_requise": 1, "exposition_exterieure": True},
        {"type_contexte": "sport",          "label_contexte": "Sport",       "formalite_requise": 1, "exposition_exterieure": True},
        {"type_contexte": "soirée",         "label_contexte": "Élégant",     "formalite_requise": 4, "exposition_exterieure": False},
    ]

    records = []
    for i in range(30):
        day = (datetime.today() + timedelta(days=i)).strftime("%Y-%m-%d")
        ctx = random.choice(context_types)
        records.append({
            "date_evenement":       day,
            "type_contexte":        ctx["type_contexte"],
            "label_contexte":       ctx["label_contexte"],
            "formalite_requise":    ctx["formalite_requise"],
            "exposition_exterieure": ctx["exposition_exterieure"]
        })

    # Supprimer et réécrire le calendrier
    supabase.table("calendrier").delete().gte("date_evenement", datetime.today().strftime("%Y-%m-%d")).execute()
    supabase.table("calendrier").insert(records).execute()

    log(f"✅ Calendrier mis à jour — 30 jours")

# ── dbt run ───────────────────────────────────────────────────────────────────
def run_dbt():
    log("Lancement dbt run...")
    result = subprocess.run(
        [DBT_ENV, "run"],
        cwd=DBT_DIR,
        capture_output=False,
        text=True
    )
    if result.returncode == 0:
        log("✅ dbt run terminé avec succès")
    else:
        log("❌ dbt run échoué")
    return result.returncode == 0

# ── Historique recommandations ────────────────────────────────────────────────
def save_recommendation_history():
    log("Enregistrement historique recommandations...")
    today = datetime.today().strftime("%Y-%m-%d")

    # Lire gold_recommendation depuis Supabase
    result = supabase.table("gold_recommendation").select("item_name, category").execute()

    if result.data:
        records = [
            {"date_recommandation": today, "nom_vetement": row["item_name"], "categorie": row["category"]}
            for row in result.data
        ]
        supabase.table("historique_recommandations").insert(records).execute()
        log(f"✅ {len(records)} vêtements enregistrés dans l'historique")

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    no_dbt      = "--no-dbt" in sys.argv
    only_history = "--only-history" in sys.argv

    log("=== NIGHTLY PIPELINE DÉMARRÉ ===")

    if only_history:
        save_recommendation_history()
    else:
        update_weather()
        update_calendar()
        if not no_dbt:
            run_dbt()
            save_recommendation_history()

    log("=== PIPELINE TERMINÉ ===")