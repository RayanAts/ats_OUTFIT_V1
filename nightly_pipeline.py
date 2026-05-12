# ============================================
# NIGHTLY PIPELINE - Boucle RL automatique
# ============================================
import os
import json
import subprocess
import requests
from datetime import datetime
from azure.identity import AzureCliCredential
from azure.storage.filedatalake import DataLakeServiceClient

# ── Config ────────────────────────────────────────────────────────────────────
ACCOUNT_URL   = "https://onelake.dfs.fabric.microsoft.com"
WORKSPACE     = "liptonws"
LAKEHOUSE     = "smartwardrobe_lakehouse.Lakehouse"
FEEDBACK_DIR  = r"C:\Projects\smartwardrobe\app\feedback_local"
DBT_DIR       = r"C:\Projects\smartwardrobe\ats_outfit"
DBT_ENV       = r"C:\Projects\smartwardrobe\dbt-env\Scripts\dbt.exe"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# ── Étape 1 : Upload feedbacks vers Fabric ────────────────────────────────────
def upload_feedbacks():
    log("Upload feedbacks vers Fabric...")
    
    credential = AzureCliCredential()
    client     = DataLakeServiceClient(account_url=ACCOUNT_URL, credential=credential)
    fs_client  = client.get_file_system_client(WORKSPACE)

    uploaded = 0
    for fname in os.listdir(FEEDBACK_DIR):
        if not fname.endswith(".json"):
            continue

        filepath = os.path.join(FEEDBACK_DIR, fname)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        remote_path = f"{LAKEHOUSE}/Files/bronze/feedback/{fname}"
        file_client = fs_client.get_file_client(remote_path)
        file_client.upload_data(content, overwrite=True)
        uploaded += 1

    log(f"✅ {uploaded} feedback(s) uploadé(s)")
    return uploaded

# ── Étape 2 : Déclencher le Notebook Fabric via API REST ─────────────────────
def trigger_fabric_notebook():
    log("Déclenchement du Notebook Fabric...")

    credential   = AzureCliCredential()
    token        = credential.get_token("https://api.fabric.microsoft.com/.default")
    access_token = token.token

    # Récupérer l'ID du workspace
    headers = {"Authorization": f"Bearer {access_token}"}
    
    ws_response = requests.get(
        "https://api.fabric.microsoft.com/v1/workspaces",
        headers=headers
    )
    
    workspace_id = None
    for ws in ws_response.json().get("value", []):
        if ws["displayName"] == WORKSPACE:
            workspace_id = ws["id"]
            break

    if not workspace_id:
        log("❌ Workspace non trouvé")
        return False

    # Récupérer l'ID du Notebook
    nb_response = requests.get(
        f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/notebooks",
        headers=headers
    )

    notebook_id = None
    for nb in nb_response.json().get("value", []):
        if "Notebook 2" in nb["displayName"] or "sync" in nb["displayName"].lower():
            notebook_id = nb["id"]
            break

    if not notebook_id:
        log("❌ Notebook non trouvé")
        return False

    log(f"✅ Notebook trouvé : {notebook_id}")
    return True

# ── Étape 3 : Lancer dbt run ──────────────────────────────────────────────────
def run_dbt():
    log("Lancement dbt run...")

    result = subprocess.run(
        [DBT_ENV, "run", "--select",
         "stg_wardrobe stg_weather stg_calendar dim_wardrobe_scd2 gold_recommendation"],
        cwd=DBT_DIR,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        log("✅ dbt run terminé avec succès")
    else:
        log(f"❌ dbt run échoué : {result.stderr}")

    return result.returncode == 0

# ── Étape 4 : Mettre à jour la météo ─────────────────────────────────────────
def update_weather():
    log("Mise à jour météo...")

    import requests as req
    from datetime import datetime

    today  = datetime.today().strftime("%Y-%m-%d")
    params = {
        "latitude": 48.8566,
        "longitude": 2.3522,
        "daily": ["temperature_2m_max", "temperature_2m_min",
                  "precipitation_sum", "windspeed_10m_max", "weathercode"],
        "timezone": "Europe/Paris",
        "forecast_days": 1
    }

    response = req.get("https://api.open-meteo.com/v1/forecast", params=params)
    raw      = response.json()

    weather_record = {
        "fetch_date":        today,
        "latitude":          48.8566,
        "longitude":         2.3522,
        "temp_max":          raw["daily"]["temperature_2m_max"][0],
        "temp_min":          raw["daily"]["temperature_2m_min"][0],
        "precipitation_mm":  raw["daily"]["precipitation_sum"][0],
        "windspeed_max_kmh": raw["daily"]["windspeed_10m_max"][0],
        "weathercode":       raw["daily"]["weathercode"][0]
    }

    content     = json.dumps(weather_record, indent=2)
    credential  = AzureCliCredential()
    client      = DataLakeServiceClient(account_url=ACCOUNT_URL, credential=credential)
    fs_client   = client.get_file_system_client(WORKSPACE)
    remote_path = f"{LAKEHOUSE}/Files/bronze/weather/weather_raw_{today}.json"
    file_client = fs_client.get_file_client(remote_path)
    file_client.upload_data(content, overwrite=True)

    log(f"✅ Météo mise à jour : {weather_record['temp_max']}°C / {weather_record['temp_min']}°C")

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log("=== NIGHTLY PIPELINE DÉMARRÉ ===")

    upload_feedbacks()
    update_weather()
    trigger_fabric_notebook()
    run_dbt()

    log("=== PIPELINE TERMINÉ ===")