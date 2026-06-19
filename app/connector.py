# ============================================
# CONNECTOR - Connexion Supabase
# ============================================
import os
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv

from pathlib import Path
load_dotenv(Path(__file__).parent.parent / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase():
    return supabase

def run_query(query: str) -> pd.DataFrame:
    """Exécute une requête SQL via RPC Supabase"""
    try:
        # Utilise une fonction Supabase pour exécuter le SQL
        result = supabase.rpc("execute_query", {"sql_query": query}).execute()
        if result.data:
            return pd.DataFrame(result.data)
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"❌ Erreur RPC : {e}")
        # Fallback : essayer de récupérer directement depuis gold_recommendation
        try:
            data = supabase.table("gold_recommendation").select("*").execute()
            return pd.DataFrame(data.data)
        except:
            return pd.DataFrame()

def test_connection():
    try:
        result = supabase.table("gold_recommendation").select("item_name, score_final").execute()
        if result.data:
            print(f"✅ Connexion OK — {len(result.data)} recommandations")
        else:
            print("✅ Connexion OK — table vide")
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    test_connection()