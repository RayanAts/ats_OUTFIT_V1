# ============================================
# RECOMMENDER - Lecture depuis Supabase
# ============================================
import pandas as pd
from connector import run_query
from datetime import datetime, timedelta

def get_top_recommendations(offset=0):
    query = f"""
        WITH ranked AS (
            SELECT
                item_id, item_name, category, subcategory,
                color, material, warmth_level, formality_level,
                score_final, rank_today, weather_label,
                temp_avg, context_label, formality_required,
                warmth_match_score, formality_match_score,
                preference_score,
                ROW_NUMBER() OVER (
                    PARTITION BY category
                    ORDER BY score_final DESC
                ) AS rn
            FROM public.gold_recommendation
        )
        SELECT * FROM ranked
        WHERE rn = {offset + 1}
        ORDER BY rank_today
    """
    result = run_query(query)
    return result

def get_recommendation_date():
    query = """
        SELECT recommendation_date
        FROM public.gold_recommendation
        ORDER BY recommendation_date DESC
        LIMIT 1
    """
    result = run_query(query)
    if len(result) > 0:
        return str(result.iloc[0]['recommendation_date'])
    return None

def get_weather_context():
    query = """
        SELECT
            fetch_date,
            fetch_time,
            city,
            temp_current,
            temp_max,
            temp_min,
            temp_avg,
            weather_label,
            precipitation_mm,
            windspeed_max_kmh
        FROM public.stg_weather
        ORDER BY fetch_date DESC
        LIMIT 1
    """
    return run_query(query).iloc[0]

def get_calendar_context():
    query = """
        SELECT
            event_date,
            context_type,
            context_label,
            formality_required,
            outdoor_exposure
        FROM public.stg_calendar
        WHERE event_date >= CURRENT_DATE
        ORDER BY event_date ASC
        LIMIT 1
    """
    return run_query(query).iloc[0]

def get_tomorrow_context():
    try:
        tomorrow = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        query = f"""
            SELECT
                event_date,
                context_type,
                context_label,
                formality_required
            FROM public.stg_calendar
            WHERE event_date = '{tomorrow}'
            LIMIT 1
        """
        result = run_query(query)
        if len(result) > 0:
            return result.iloc[0]
        return None
    except:
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