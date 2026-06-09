# ============================================
# MIGRATION - 72 vêtements Fabric → Supabase
# ============================================
import pandas as pd
import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime

load_dotenv(r"C:\Projects\smartwardrobe\.env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# ── Lecture Excel ──────────────────────────────────────────────────────────────
def migrate_wardrobe():
    log("Lecture du fichier Excel...")

    df = pd.read_excel(
        r"C:\Projects\smartwardrobe\wardrobe_rayan.xlsx",
        sheet_name="Garde-robe Rayan",
        header=None
    )

    # Trouver la ligne header
    header_row = None
    for i, row in df.iterrows():
        if "item_name" in row.values:
            header_row = i
            break

    df = pd.read_excel(
        r"C:\Projects\smartwardrobe\wardrobe_rayan.xlsx",
        sheet_name="Garde-robe Rayan",
        header=header_row
    )
    df = df.dropna(subset=["item_name"])
    df = df[df["item_name"] != "item_name"]

    log(f"✅ {len(df)} vêtements lus depuis Excel")

    # ── Upload vers Supabase ───────────────────────────────────────────────────
    log("Upload vers Supabase...")

    success = 0
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
            "created_at":      str(datetime.today().strftime("%Y-%m-%d"))
        }

        result = supabase.table("vetements").insert(item).execute()
        success += 1

    log(f"✅ {success} vêtements migrés vers Supabase !")

if __name__ == "__main__":
    log("=== MIGRATION DÉMARRÉE ===")
    migrate_wardrobe()
    log("=== MIGRATION TERMINÉE ===")