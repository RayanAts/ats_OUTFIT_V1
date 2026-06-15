# ============================================
# SUPABASE UPLOAD - Remplace OneLake/Fabric
# ============================================
import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(r"C:\Projects\smartwardrobe\.env")

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def upload_new_item(item_dict: dict, filename: str = None):
    """
    Insère un vêtement directement dans Supabase + relance dbt
    """
    import subprocess

    record = {
        "item_name":       item_dict.get("item_name"),
        "category":        item_dict.get("category"),
        "subcategory":     item_dict.get("subcategory"),
        "color":           item_dict.get("color"),
        "material":        item_dict.get("material"),
        "warmth_level":    int(item_dict.get("warmth_level", 2)),
        "formality_level": int(item_dict.get("formality_level", 2)),
        "season":          item_dict.get("season", "Toutes"),
        "condition":       item_dict.get("condition", "Bon"),
        "is_active":       True,
        "created_at":      datetime.today().strftime("%Y-%m-%d"),
        "user_id":         item_dict.get("user_id", 1)
    }

    result = supabase.table("vetements").insert(record).execute()
    print(f"✅ Vêtement ajouté : {record['item_name']} (user_id={record['user_id']})")

    # Relancer dbt automatiquement
    print("🔄 Recalcul des recommandations...")
    subprocess.run(
        [r"C:\Projects\smartwardrobe\dbt-env\Scripts\dbt.exe", "run"],
        cwd=r"C:\Projects\smartwardrobe\ats_outfit",
        capture_output=True
    )
    print("✅ Recommandations mises à jour !")

    return result

def upload_feedback(feedback_dict: dict, filename: str = None):
    """
    Insère un feedback directement dans Supabase
    """
    record = {
        "nom_vetement":  feedback_dict.get("item_name"),
        "signal":        int(feedback_dict.get("signal", 0)),
        "type_contexte": feedback_dict.get("context_type"),
        "temp_moyenne":  float(feedback_dict.get("temp_avg", 0)),
        "weathercode":   int(feedback_dict.get("weathercode", 0)),
        "cree_le":       datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    result = supabase.table("retours").insert(record).execute()
    print(f"✅ Feedback uploadé dans Supabase : {record['nom_vetement']}")
    return result

if __name__ == "__main__":
    try:
        result = supabase.table("vetements").select("id").limit(1).execute()
        print("✅ Connexion Supabase OK")
    except Exception as e:
        print(f"❌ Erreur : {e}")