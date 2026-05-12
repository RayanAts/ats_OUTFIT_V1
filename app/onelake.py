# ============================================
# ONELAKE - Upload vers Fabric automatique
# ============================================
from azure.storage.filedatalake import DataLakeServiceClient
from azure.identity import AzureCliCredential
import json
import os

ACCOUNT_NAME  = "onelake"
WORKSPACE     = "liptonws"
LAKEHOUSE     = "smartwardrobe_lakehouse.Lakehouse"
ACCOUNT_URL   = f"https://{ACCOUNT_NAME}.dfs.fabric.microsoft.com"

def get_client():
    credential = AzureCliCredential()
    return DataLakeServiceClient(
        account_url=ACCOUNT_URL,
        credential=credential
    )

def upload_new_item(item_dict: dict, filename: str):
    """
    Upload un vêtement JSON vers Files/bronze/new_items/ dans Fabric
    """
    client     = get_client()
    fs_client  = client.get_file_system_client(WORKSPACE)
    file_path  = f"{LAKEHOUSE}/Files/bronze/new_items/{filename}"
    file_client = fs_client.get_file_client(file_path)

    content = json.dumps(item_dict, indent=2, ensure_ascii=False)
    file_client.upload_data(content, overwrite=True)
    print(f"✅ Uploadé : {file_path}")

def upload_feedback(feedback_dict: dict, filename: str):
    """
    Upload un feedback JSON vers Files/bronze/feedback/ dans Fabric
    """
    client      = get_client()
    fs_client   = client.get_file_system_client(WORKSPACE)
    file_path   = f"{LAKEHOUSE}/Files/bronze/feedback/{filename}"
    file_client = fs_client.get_file_client(file_path)

    content = json.dumps(feedback_dict, indent=2, ensure_ascii=False)
    file_client.upload_data(content, overwrite=True)
    print(f"✅ Feedback uploadé : {file_path}")

if __name__ == "__main__":
    # Test de connexion
    try:
        client    = get_client()
        fs_client = client.get_file_system_client(WORKSPACE)
        print("✅ Connexion OneLake OK")
    except Exception as e:
        print(f"❌ Erreur : {e}")