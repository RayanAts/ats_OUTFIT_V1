# ============================================
# FEEDBACK - Enregistrement des swipes
# ============================================
import json
import os
from datetime import datetime

FEEDBACK_DIR = r"C:\Projects\smartwardrobe\app\feedback_local"

def save_feedback(item_id, item_name, signal, context_type, temp_avg, weathercode):
    """
    signal : +1 (accepté) ou -1 (refusé)
    """
    os.makedirs(FEEDBACK_DIR, exist_ok=True)

    today = datetime.today().strftime("%Y-%m-%d")
    now = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

    feedback = {
        "feedback_date": today,
        "feedback_timestamp": now,
        "item_id": int(item_id),
        "item_name": item_name,
        "signal": signal,
        "context_type": context_type,
        "temp_avg": float(temp_avg),
        "weathercode": int(weathercode)
    }

    filename = f"feedback_{today}_{item_id}.json"
    filepath = os.path.join(FEEDBACK_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(feedback, f, indent=2, ensure_ascii=False)

    print(f"✅ Feedback sauvegardé : {filepath}")
    return feedback

if __name__ == "__main__":
    # Test
    save_feedback(
        item_id=7,
        item_name="Veste Blazer Marine",
        signal=1,
        context_type="bureau",
        temp_avg=14.0,
        weathercode=3
    )