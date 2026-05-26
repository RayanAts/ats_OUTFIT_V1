# ============================================
# IMPORT WARDROBE - Excel vers Fabric OneLake
# ============================================
import pandas as pd
import json
import os
from datetime import datetime
from azure.identity import AzureCliCredential
from azure.storage.filedatalake import DataLakeServiceClient

# ── Config ────────────────────────────────────────────────────────────────────
EXCEL_PATH   = r"C:\Projects\smartwardrobe\wardrobe_rayan.xlsx"
ACCOUNT_URL  = "https://onelake.dfs.fabric.microsoft.com"
WORKSPACE    = "liptonws"
LAKEHOUSE    = "smartwardrobe_lakehouse.Lakehouse"
TODAY        = datetime.today().strftime("%Y-%m-%d")

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
def read_excel():
    log("Lecture du fichier Excel...")
    df = pd.read_excel(EXCEL_PATH, sheet_name="Garde-robe Rayan", header=None)
    
    # Trouver la ligne qui contient "item_name"
    header_row = None
    for i, row in df.iterrows():
        if "item_name" in row.values:
            header_row = i
            break
    
    if header_row is None:
        raise Exception("Colonne item_name introuvable dans le fichier Excel")
    
    # Relire avec le bon header
    df = pd.read_excel(EXCEL_PATH, sheet_name="Garde-robe Rayan", header=header_row)
    df = df.dropna(subset=["item_name"])
    df = df[df["item_name"] != "item_name"]  # Supprimer les doublons de header
    
    log(f"✅ {len(df)} vêtements lus depuis le fichier Excel")
    return df
# ── Upload vers OneLake ───────────────────────────────────────────────────────
def upload_to_onelake(df):
    log("Connexion à OneLake...")
    credential = AzureCliCredential()
    client     = DataLakeServiceClient(account_url=ACCOUNT_URL, credential=credential)
    fs_client  = client.get_file_system_client(WORKSPACE)

    # Vider le dossier new_items d'abord
    log("Upload des vêtements vers Fabric...")
    
    uploaded = 0
    for _, row in df.iterrows():
        item = {
            "item_name":       str(row["item_name"]),
            "category":        str(row["category"]),
            "subcategory":     str(row["subcategory"]),
            "color":           str(row["color"]),
            "material":        str(row["material"]),
            "warmth_level":    int(row["warmth_level"]),
            "formality_level": int(row["formality_level"]),
            "season":          str(row["season"]),
            "condition":       str(row["condition"]),
            "is_active":       True,
            "created_at":      TODAY
        }

        filename    = f"wardrobe_{uploaded+1:03d}_{item['item_name'][:20].replace(' ','_')}.json"
        remote_path = f"{LAKEHOUSE}/Files/bronze/new_items/{filename}"
        file_client = fs_client.get_file_client(remote_path)
        file_client.upload_data(
            json.dumps(item, indent=2, ensure_ascii=False),
            overwrite=True
        )
        uploaded += 1

    log(f"✅ {uploaded} vêtements uploadés vers Fabric !")
    log("➡️  Lance maintenant le Notebook Fabric de sync puis dbt run")

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log("=== IMPORT WARDROBE DÉMARRÉ ===")
    df = read_excel()
    upload_to_onelake(df)
    log("=== IMPORT TERMINÉ ===")