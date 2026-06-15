# ============================================
# AUTH - Vérifications de sécurité
# ============================================
import streamlit as st
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv(r"C:\Projects\smartwardrobe\.env")
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def require_auth():
    """Vérifie que l'utilisateur est connecté"""
    user_id = st.session_state.get('user_id')
    if not user_id:
        st.warning("Session expirée — reconnecte-toi.")
        st.switch_page("main.py")
    return user_id

def require_wardrobe():
    """Vérifie connexion + garde-robe non vide"""
    user_id = require_auth()
    wardrobe = supabase.table("vetements")\
        .select("id")\
        .eq("user_id", user_id)\
        .execute()
    if len(wardrobe.data) == 0:
        st.info("Commence par construire ta garde-robe !")
        st.switch_page("pages/4_Onboarding.py")
    return user_id