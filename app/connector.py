# ============================================
# CONNECTOR - Connexion au Warehouse Fabric
# ============================================
import pyodbc
import struct
from azure.identity import AzureCliCredential

SERVER = "qw4joi7ev7duxhq64sez55cndi-keoyaocqxrbunasslfn52uqmlm.datawarehouse.fabric.microsoft.com"
DATABASE = "smartwardrobe_warehouse"
DRIVER = "ODBC Driver 18 for SQL Server"

def get_token():
    credential = AzureCliCredential()
    token = credential.get_token("https://database.windows.net/.default")
    token_bytes = token.token.encode("UTF-16-LE")
    token_struct = struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)
    return token_struct

def get_connection():
    conn_str = (
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
    )
    token_struct = get_token()
    conn = pyodbc.connect(conn_str, attrs_before={1256: token_struct})
    return conn

def test_connection():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 1 item_name, score_final FROM dbo.gold_recommendation ORDER BY rank_today")
        row = cursor.fetchone()
        print(f"✅ Connexion OK — Meilleure reco : {row[0]} ({row[1]})")
        conn.close()
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    test_connection()