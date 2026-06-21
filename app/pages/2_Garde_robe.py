# ============================================
# PAGE 2 - Garde-robe
# ============================================
import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd 

from styles import GLOBAL_CSS

from auth import require_wardrobe
USER_ID = require_wardrobe()
from connector import get_supabase
supabase = get_supabase()

st.set_page_config(page_title="Garde-robe · SmartWardrobe", page_icon="👔", layout="centered")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

st.markdown("""
<div class="sw-page-header">
    <div class="sw-page-eyebrow">Inventaire</div>
    <h1 class="sw-page-title">Ta garde-robe</h1>
    <p class="sw-page-sub">Tous tes vêtements, scorés et organisés</p>
</div>
""", unsafe_allow_html=True)

# ── Chargement ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def load_wardrobe(user_id):
    try:
        result = supabase.table("vetements") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("category", desc=False) \
            .execute()
        
        if not result.data:
            return pd.DataFrame()
        
        df = pd.DataFrame(result.data)
        
        # Colonnes par défaut si manquantes
        if 'is_active' not in df.columns:
            df['is_active'] = True
        if 'formality_level' not in df.columns:
            df['formality_level'] = 3
        if 'subcategory' not in df.columns:
            df['subcategory'] = ''
        if 'season' not in df.columns:
            df['season'] = 'Toutes'
        if 'condition' not in df.columns:
            df['condition'] = 'Bon'
            
        return df
    except Exception as e:
        print(f"❌ Erreur load_wardrobe: {e}")
        return pd.DataFrame()

df = load_wardrobe(USER_ID)

# ── Stats ─────────────────────────────────────────────────────────────────────
total      = len(df)
actifs     = int(df['is_active'].sum())
categories = df['category'].nunique()

st.markdown(f"""
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:1.5rem">
    <div class="stat-block">
        <div class="stat-num">{total}</div>
        <div class="stat-lbl">Pièces</div>
    </div>
    <div class="stat-block">
        <div class="stat-num stat-gold">{actifs}</div>
        <div class="stat-lbl">Actives</div>
    </div>
    <div class="stat-block">
        <div class="stat-num">{categories}</div>
        <div class="stat-lbl">Catégories</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="sw-divider"></div>', unsafe_allow_html=True)


# ── Config ────────────────────────────────────────────────────────────────────
cat_emojis = {
    "Haut":       "👕",
    "Bas":        "👖",
    "Chaussures": "👟",
    "Accessoire": "🧣"
}

condition_colors = {
    "Bon":   "#22c55e",
    "Usé":   "#f59e0b",
    "Abîmé": "#ef4444"
}
# ── Filtre catégorie (Tabs) ───────────────────────────────────────────────────
cat_emojis_tab = {"Haut": "👕", "Bas": "👖", "Chaussures": "👟", "Accessoire": "🧣"}
cats = sorted(df['category'].dropna().astype(str).unique().tolist())

tab_labels = [f"Tous ({len(df)})"]
for cat in cats:
    emoji = cat_emojis_tab.get(cat, "👔")
    count = len(df[df['category'] == cat])
    tab_labels.append(f"{emoji} {cat} ({count})")

tabs = st.tabs(tab_labels)

def render_card(row):
    """Affiche une card vêtement"""
    emoji      = cat_emojis.get(str(row['category']), "👔")
    cond_color = condition_colors.get(str(row['condition']), "#22c55e")

    try:
        formality_val = int(float(row["formality_level"])) if str(row["formality_level"]) not in ["nan", "None", ""] else 3
    except:
        formality_val = 3
    try:
        warmth_val = int(float(row["warmth_level"])) if str(row["warmth_level"]) not in ["nan", "None", ""] else 2
    except:
        warmth_val = 2

    form_html = "".join([
        f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;'
        f'margin-right:3px;background:{"#0D1B2A" if d < formality_val else "rgba(13,27,42,0.1)"}"></span>'
        for d in range(5)
    ])
    warm_html = "".join([
        f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;'
        f'margin-right:3px;background:{"#B8974A" if d < warmth_val else "rgba(13,27,42,0.1)"}"></span>'
        for d in range(5)
    ])

    item_name   = str(row['item_name'])   if str(row['item_name'])   not in ["nan", "None"] else "—"
    subcategory = str(row['subcategory'])  if str(row['subcategory']) not in ["nan", "None"] else "—"
    color       = str(row['color'])        if str(row['color'])       not in ["nan", "None"] else "—"
    season      = str(row['season'])       if str(row['season'])      not in ["nan", "None"] else "—"
    condition   = str(row['condition'])    if str(row['condition'])   not in ["nan", "None"] else "—"

    return f"""
<div style="background:white;border:1px solid rgba(13,27,42,0.08);
border-radius:14px;padding:1.2rem;margin-bottom:1rem">
    <div style="font-size:2rem;margin-bottom:0.5rem">{emoji}</div>
    <div style="font-family:'Syne',sans-serif;font-size:0.92rem;
    font-weight:700;color:#0D1B2A">{item_name}</div>
    <div style="font-size:0.76rem;color:#8A8A8A;margin-top:0.3rem">
        {subcategory} · {color} · {season}
    </div>
    <div style="margin-top:0.8rem">
        <div style="font-size:0.68rem;color:#8A8A8A;text-transform:uppercase;
        letter-spacing:0.1em;margin-bottom:0.4rem">Formalité</div>
        {form_html}
    </div>
    <div style="margin-top:0.6rem">
        <div style="font-size:0.68rem;color:#8A8A8A;text-transform:uppercase;
        letter-spacing:0.1em;margin-bottom:0.4rem">Chaleur</div>
        {warm_html}
    </div>
    <div style="margin-top:0.8rem;display:flex;align-items:center;gap:0.5rem">
        <div style="width:7px;height:7px;border-radius:50%;
        background:{cond_color}"></div>
        <span style="font-size:0.75rem;color:#8A8A8A">{condition}</span>
    </div>
</div>
    """

def render_items_grouped(items_df):
    """Affiche les vêtements groupés par sous-catégorie"""
    if items_df.empty:
        st.info("Aucun vêtement dans cette catégorie")
        return

    subcats = sorted(items_df['subcategory'].dropna().astype(str).unique().tolist())

    for subcat in subcats:
        sub_df = items_df[items_df['subcategory'].astype(str) == subcat]
        subcat_label = subcat if subcat not in ["nan", "None", ""] else "Autre"

        st.markdown(
            f'<div style="margin:16px 0 8px;padding:6px 12px;background:#F2F2F7;'
            f'border-radius:10px;display:inline-block">'
            f'<span style="font-size:13px;font-weight:600;color:#1C1C1E">'
            f'{subcat_label}</span>'
            f'<span style="font-size:12px;color:#8E8E93;margin-left:6px">({len(sub_df)})</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        rows_list = list(sub_df.iterrows())
        for i in range(0, len(rows_list), 2):
            pair = rows_list[i:i+2]
            cols = st.columns(2)
            for j, (_, row) in enumerate(pair):
                cols[j].markdown(render_card(row), unsafe_allow_html=True)

def render_items_flat(items_df):
    """Affiche les vêtements sans groupement (pour Chaussures, Accessoires)"""
    if items_df.empty:
        st.info("Aucun vêtement dans cette catégorie")
        return

    rows_list = list(items_df.iterrows())
    for i in range(0, len(rows_list), 2):
        pair = rows_list[i:i+2]
        cols = st.columns(2)
        for j, (_, row) in enumerate(pair):
            cols[j].markdown(render_card(row), unsafe_allow_html=True)

# Tab "Tous" → groupé par catégorie puis sous-catégorie
with tabs[0]:
    for cat in cats:
        cat_df = df[df['category'] == cat]
        emoji = cat_emojis_tab.get(cat, "👔")
        st.markdown(f"### {emoji} {cat} ({len(cat_df)})")
        render_items_grouped(cat_df)

# Tabs par catégorie
for i, cat in enumerate(cats):
    with tabs[i + 1]:
        cat_df = df[df['category'] == cat]
        if cat in ["Haut", "Bas"]:
            render_items_grouped(cat_df)
        else:
            render_items_flat(cat_df)

# ── Navigation ────────────────────────────────────────────────────────────────
st.markdown('<div class="sw-divider"></div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏠\nAccueil", use_container_width=True, type="secondary"):
        st.switch_page("pages/1_Recommandation.py")
with col2:
    if st.button("👔\nGarde-robe", use_container_width=True, type="secondary"):
        st.switch_page("pages/2_Garde_robe.py")
with col3:
    if st.button("📊\nStats", use_container_width=True, type="secondary"):
        st.switch_page("pages/3_Historique.py")
with col4:
    if st.button("➕\nAjouter", use_container_width=True, type="secondary"):
        st.switch_page("pages/5_Ajouter.py")