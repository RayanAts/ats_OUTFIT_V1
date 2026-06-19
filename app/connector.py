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
    from sqlalchemy import create_engine
    password = os.getenv("SUPABASE_DB_PASSWORD")
    engine = create_engine(
        f"postgresql://postgres.wvqntpaovovtpwxunkxd:{password}@aws-1-eu-central-1.pooler.supabase.com:6543/postgres",
        connect_args={"sslmode": "require"}
    )
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df

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