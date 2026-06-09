# ============================================
# FEEDBACK - Enregistrement des swipes
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

def save_feedback(item_id, item_name, signal, context_type, temp_avg, weathercode):
    """
    signal : +1 (accepté) ou -1 (refusé)
    """
    now   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today = datetime.today().strftime("%Y-%m-%d")

    record = {
        "nom_vetement":  item_name,
        "signal":        int(signal),
        "type_contexte": context_type,
        "temp_moyenne":  float(temp_avg),
        "weathercode":   int(weathercode),
        "cree_le":       now
    }

    result = supabase.table("retours").insert(record).execute()
    print(f"✅ Feedback sauvegardé dans Supabase : {item_name} ({'+1' if signal == 1 else '-1'})")
    return result

if __name__ == "__main__":
    save_feedback(
        item_id=7,
        item_name="Test Veste Marine",
        signal=1,
        context_type="bureau",
        temp_avg=14.0,
        weathercode=3
    )