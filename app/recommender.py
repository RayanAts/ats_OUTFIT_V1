# ============================================
# RECOMMENDER - Lecture depuis Supabase
# ============================================
import pandas as pd
from datetime import datetime, timedelta

from connector import get_supabase

supabase = get_supabase()

def get_top_recommendations(offset=0, user_id=1):
    """Récupère le top 1 de chaque catégorie pour l'utilisateur"""
    try:
        result = supabase.table("gold_recommendation") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("score_final", desc=True) \
            .execute()
        
        if not result.data:
            return pd.DataFrame()
        
        df = pd.DataFrame(result.data)
        
        # Top 1 par catégorie (sans .apply qui bugue)
        top_by_category = df.sort_values("score_final", ascending=False) \
            .drop_duplicates(subset=["category"]) \
            .reset_index(drop=True)
        
        return top_by_category
        
    except Exception as e:
        print(f"❌ Erreur get_top_recommendations: {e}")
        return pd.DataFrame()

supabase = get_supabase()

def get_recommendation_date(user_id=1):
    try:
        result = supabase.table("gold_recommendation") \
            .select("recommendation_date") \
            .eq("user_id", user_id) \
            .order("recommendation_date", desc=True) \
            .limit(1) \
            .execute()
        
        if result.data:
            return str(result.data[0]['recommendation_date'])
        return None
    except Exception as e:
        print(f"❌ Erreur get_recommendation_date: {e}")
        return None

def get_weather_context():
    try:
        result = supabase.table("stg_weather") \
            .select("fetch_date, fetch_time, city, temp_current, temp_max, temp_min, temp_avg, weather_label, precipitation_mm, windspeed_max_kmh") \
            .order("fetch_date", desc=True) \
            .limit(1) \
            .execute()
        
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print(f"❌ Erreur get_weather_context: {e}")
        return None

def get_calendar_context(user_id=1):
    try:
        today = datetime.today().strftime("%Y-%m-%d")
        result = supabase.table("stg_calendar") \
            .select("event_date, context_type, context_label, formality_required, outdoor_exposure") \
            .eq("user_id", user_id) \
            .gte("event_date", today) \
            .order("event_date", desc=False) \
            .limit(1) \
            .execute()
        
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print(f"❌ Erreur get_calendar_context: {e}")
        return None

def get_tomorrow_context(user_id=1):
    try:
        tomorrow = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        result = supabase.table("stg_calendar") \
            .select("event_date, context_type, context_label, formality_required") \
            .eq("user_id", user_id) \
            .eq("event_date", tomorrow) \
            .limit(1) \
            .execute()
        
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print(f"❌ Erreur get_tomorrow_context: {e}")
        return None

if __name__ == "__main__":
    print("🌤️ Météo :")
    weather = get_weather_context()
    print(f"   {weather['weather_label']} — {weather['temp_avg']}°C")

    print("\n📅 Contexte :")
    calendar = get_calendar_context()
    print(f"   {calendar['context_label']} (formalité {calendar['formality_required']}/5)")

    print("\n👔 Top recommandations :")
    recs = get_top_recommendations()
    for _, row in recs.iterrows():
        print(f"   #{int(row['rank_today'])} {row['item_name']} — score {row['score_final']}")