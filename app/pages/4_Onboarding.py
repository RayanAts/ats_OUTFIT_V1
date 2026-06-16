# ============================================
# PAGE 4 - Onboarding Catalogue
# ============================================
import streamlit as st
import sys, os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(r"C:\Projects\smartwardrobe\.env")

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

st.set_page_config(page_title="Mon style · SmartWardrobe", page_icon="👔", layout="centered")

# ── Vérif connexion ───────────────────────────────────────────────────────────
if 'user_id' not in st.session_state or not st.session_state.user_id:
    st.switch_page("main.py")

USER_ID = st.session_state.user_id
NOM     = st.session_state.get('nom', 'toi')

# ── Catalogue ─────────────────────────────────────────────────────────────────
CATALOGUE = {
    "Haut": [
        {"type": "Chemise",          "emoji": "👔", "subcategory": "Chemise",  "formality": 5, "warmth": 1},
        {"type": "Blazer",           "emoji": "🥼", "subcategory": "Blazer",   "formality": 5, "warmth": 2},
        {"type": "Veste costume",    "emoji": "🧥", "subcategory": "Blazer",   "formality": 5, "warmth": 2},
        {"type": "Pull quarter zip", "emoji": "🧶", "subcategory": "Pull",     "formality": 4, "warmth": 3},
        {"type": "Pull col rond",    "emoji": "🧶", "subcategory": "Pull",     "formality": 3, "warmth": 4},
        {"type": "Pull col V",       "emoji": "🧶", "subcategory": "Pull",     "formality": 3, "warmth": 4},
        {"type": "Sweat col rond",   "emoji": "👕", "subcategory": "Sweat",    "formality": 2, "warmth": 3},
        {"type": "T-shirt basique",  "emoji": "👕", "subcategory": "T-shirt",  "formality": 1, "warmth": 1},
        {"type": "T-shirt oversize", "emoji": "👕", "subcategory": "T-shirt",  "formality": 1, "warmth": 1},
        {"type": "T-shirt col V",    "emoji": "👕", "subcategory": "T-shirt",  "formality": 2, "warmth": 1},
        {"type": "Doudoune",         "emoji": "🦺", "subcategory": "Doudoune", "formality": 1, "warmth": 5},
        {"type": "Veste bomber",     "emoji": "🧥", "subcategory": "Veste",    "formality": 2, "warmth": 3},
        {"type": "Hoodie",           "emoji": "👕", "subcategory": "Sweat",    "formality": 1, "warmth": 3},
        {"type": "Polo",             "emoji": "👕", "subcategory": "Chemise",  "formality": 3, "warmth": 1},
        {"type": "Veste légère",     "emoji": "🧥", "subcategory": "Veste",    "formality": 2, "warmth": 2},
    ],
    "Bas": [
        {"type": "Pantalon costume", "emoji": "👖", "subcategory": "Pantalon", "formality": 4, "warmth": 2},
        {"type": "Jean slim",        "emoji": "👖", "subcategory": "Jean",     "formality": 2, "warmth": 2},
        {"type": "Jean large",       "emoji": "👖", "subcategory": "Jean",     "formality": 2, "warmth": 2},
        {"type": "Jean droit",       "emoji": "👖", "subcategory": "Jean",     "formality": 2, "warmth": 2},
        {"type": "Chino",            "emoji": "👖", "subcategory": "Chino",    "formality": 3, "warmth": 2},
        {"type": "Cargo",            "emoji": "👖", "subcategory": "Pantalon", "formality": 2, "warmth": 2},
        {"type": "Jogging",          "emoji": "👖", "subcategory": "Jogging",  "formality": 1, "warmth": 2},
        {"type": "Short",            "emoji": "🩳", "subcategory": "Short",    "formality": 1, "warmth": 1},
        {"type": "Short sport",      "emoji": "🩳", "subcategory": "Short",    "formality": 1, "warmth": 1},
    ],
    "Chaussures": [
        {"type": "Sneaker basique",   "emoji": "👟", "subcategory": "Sneaker",      "formality": 2, "warmth": 1},
        {"type": "Sneaker chunky",    "emoji": "👟", "subcategory": "Sneaker",      "formality": 1, "warmth": 1},
        {"type": "Sneaker colorée",   "emoji": "👟", "subcategory": "Sneaker",      "formality": 1, "warmth": 1},
        {"type": "Trail / Outdoor",   "emoji": "🥾", "subcategory": "Trail",        "formality": 1, "warmth": 2},
        {"type": "Loafer / Mocassin", "emoji": "👞", "subcategory": "Mocassin",     "formality": 4, "warmth": 1},
        {"type": "Derby / Richelieu", "emoji": "👞", "subcategory": "Richelieu",    "formality": 5, "warmth": 1},
        {"type": "Chelsea boot",      "emoji": "👢", "subcategory": "Chelsea Boot", "formality": 3, "warmth": 2},
        {"type": "Sandale",           "emoji": "🩴", "subcategory": "Sandale",      "formality": 1, "warmth": 1},
    ]
}

# ── Couleurs simples (18) ─────────────────────────────────────────────────────
COULEURS_SIMPLES = [
    {"nom": "Noir",      "hex": "#1a1a1a"},
    {"nom": "Blanc",     "hex": "#F5F3EE"},
    {"nom": "Gris",      "hex": "#9E9E9E"},
    {"nom": "Marine",    "hex": "#1B2A4A"},
    {"nom": "Bleu",      "hex": "#4A90D9"},
    {"nom": "Bleu ciel", "hex": "#87CEEB"},
    {"nom": "Marron",    "hex": "#6B3F2A"},
    {"nom": "Beige",     "hex": "#D4C5A9"},
    {"nom": "Kaki",      "hex": "#7D8C5A"},
    {"nom": "Camel",     "hex": "#C19A6B"},
    {"nom": "Bordeaux",  "hex": "#722F37"},
    {"nom": "Orange",    "hex": "#E8732A"},
    {"nom": "Violet",    "hex": "#6B4E9B"},
    {"nom": "Rose",      "hex": "#E8A0B4"},
    {"nom": "Jaune",     "hex": "#F5C842"},
    {"nom": "Vert",      "hex": "#2ECC71"},
    {"nom": "Crème",     "hex": "#F5F0E8"},
    {"nom": "Taupe",     "hex": "#8B7D6B"},
]

# ── Duos de couleurs (25) ─────────────────────────────────────────────────────
COULEURS_DUOS = [
    {"nom": "Noir / Blanc",      "hex1": "#1a1a1a", "hex2": "#F5F3EE"},
    {"nom": "Noir / Gris",       "hex1": "#1a1a1a", "hex2": "#9E9E9E"},
    {"nom": "Marine / Blanc",    "hex1": "#1B2A4A", "hex2": "#F5F3EE"},
    {"nom": "Gris / Blanc",      "hex1": "#9E9E9E", "hex2": "#F5F3EE"},
    {"nom": "Blanc / Beige",     "hex1": "#F5F3EE", "hex2": "#D4C5A9"},
    {"nom": "Marine / Beige",    "hex1": "#1B2A4A", "hex2": "#D4C5A9"},
    {"nom": "Kaki / Beige",      "hex1": "#7D8C5A", "hex2": "#D4C5A9"},
    {"nom": "Marron / Beige",    "hex1": "#6B3F2A", "hex2": "#D4C5A9"},
    {"nom": "Camel / Blanc",     "hex1": "#C19A6B", "hex2": "#F5F3EE"},
    {"nom": "Gris / Marine",     "hex1": "#9E9E9E", "hex2": "#1B2A4A"},
    {"nom": "Noir / Orange",     "hex1": "#1a1a1a", "hex2": "#E8732A"},
    {"nom": "Noir / Jaune",      "hex1": "#1a1a1a", "hex2": "#F5C842"},
    {"nom": "Noir / Bordeaux",   "hex1": "#1a1a1a", "hex2": "#722F37"},
    {"nom": "Gris / Orange",     "hex1": "#9E9E9E", "hex2": "#E8732A"},
    {"nom": "Blanc / Vert",      "hex1": "#F5F3EE", "hex2": "#2ECC71"},
    {"nom": "Blanc / Bleu ciel", "hex1": "#F5F3EE", "hex2": "#87CEEB"},
    {"nom": "Beige / Kaki",      "hex1": "#D4C5A9", "hex2": "#7D8C5A"},
    {"nom": "Blanc / Rose",      "hex1": "#F5F3EE", "hex2": "#E8A0B4"},
    {"nom": "Crème / Camel",     "hex1": "#F5F0E8", "hex2": "#C19A6B"},
    {"nom": "Bleu / Blanc",      "hex1": "#4A90D9", "hex2": "#F5F3EE"},
    {"nom": "Marine / Orange",   "hex1": "#1B2A4A", "hex2": "#E8732A"},
    {"nom": "Bordeaux / Beige",  "hex1": "#722F37", "hex2": "#D4C5A9"},
    {"nom": "Kaki / Orange",     "hex1": "#7D8C5A", "hex2": "#E8732A"},
    {"nom": "Marron / Kaki",     "hex1": "#6B3F2A", "hex2": "#7D8C5A"},
    {"nom": "Violet / Gris",     "hex1": "#6B4E9B", "hex2": "#9E9E9E"},
]

COULEURS_LIGHT = ["Blanc", "Beige", "Camel", "Gris", "Crème", "Rose", "Jaune", "Bleu ciel"]

# ── State ─────────────────────────────────────────────────────────────────────
if 'onb_step'         not in st.session_state: st.session_state.onb_step         = 1
if 'onb_selections'   not in st.session_state: st.session_state.onb_selections   = []
if 'onb_current_item' not in st.session_state: st.session_state.onb_current_item = None
if 'onb_category'     not in st.session_state: st.session_state.onb_category     = "Haut"
if 'onb_colors_sel'   not in st.session_state: st.session_state.onb_colors_sel   = []
if 'onb_color_mode'   not in st.session_state: st.session_state.onb_color_mode   = "simple"

# ── Progress bar ──────────────────────────────────────────────────────────────
steps   = ["Hauts", "Bas", "Chaussures", "Confirmation"]
current = ["Haut", "Bas", "Chaussures"].index(st.session_state.onb_category) if st.session_state.onb_step < 4 else 3
progress = current / 3

st.markdown(f"""
<div style="margin-bottom:1.5rem">
    <div style="font-family:'Syne',sans-serif;font-size:1.5rem;
    font-weight:800;color:#0D1B2A;margin-bottom:0.3rem">
        Construis ta garde-robe 👔
    </div>
    <div style="font-size:0.85rem;color:#8A8A8A;margin-bottom:1rem">
        Sélectionne les vêtements que tu possèdes
    </div>
    <div style="background:#E0D8CE;border-radius:99px;height:6px">
        <div style="background:#B8974A;border-radius:99px;height:6px;
        width:{int(progress*100)}%;transition:width 0.3s"></div>
    </div>
    <div style="display:flex;justify-content:space-between;margin-top:0.4rem">
        {''.join([f'<span style="font-size:0.7rem;color:{"#B8974A" if i <= current else "#8A8A8A"};font-weight:{"700" if i == current else "400"}">{s}</span>' for i, s in enumerate(steps)])}
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ÉTAPES 1-3 — Sélection par catégorie
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.onb_step in [1, 2, 3]:
    cat   = st.session_state.onb_category
    items = CATALOGUE[cat]

    st.markdown(f"""
    <div style="font-family:'Syne',sans-serif;font-size:1.1rem;
    font-weight:700;color:#0D1B2A;margin-bottom:1rem">
        Quels {cat.lower()}s as-tu ?
    </div>
    """, unsafe_allow_html=True)

    # ── Mode sélection couleurs ───────────────────────────────────────────────
    if st.session_state.onb_current_item:
        item = st.session_state.onb_current_item

        st.markdown(f"""
        <div style="background:white;border:2px solid #B8974A;border-radius:14px;
        padding:1.2rem;margin-bottom:1rem;text-align:center">
            <div style="font-size:2rem">{item['emoji']}</div>
            <div style="font-family:'Syne',sans-serif;font-size:1rem;
            font-weight:700;color:#0D1B2A">{item['type']}</div>
            <div style="font-size:0.8rem;color:#8A8A8A;margin-top:0.3rem">
                Sélectionne toutes tes couleurs
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Nom optionnel
        nom_custom = st.text_input(
            "Nom personnalisé (optionnel)",
            placeholder=f"ex: Ma paire de Salomon, Mon {item['type']} Zara...",
            key=f"nom_{item['type']}_{cat}"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Toggle simple / duo
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            if st.button(
                "✅ Couleur simple" if st.session_state.onb_color_mode == "simple" else "🎨 Couleur simple",
                use_container_width=True,
                type="primary" if st.session_state.onb_color_mode == "simple" else "secondary"
            ):
                st.session_state.onb_color_mode = "simple"
                st.session_state.onb_colors_sel = []
                st.rerun()
        with col_t2:
            if st.button(
                "✅ Duo de couleurs" if st.session_state.onb_color_mode == "duo" else "🎨 Duo de couleurs",
                use_container_width=True,
                type="primary" if st.session_state.onb_color_mode == "duo" else "secondary"
            ):
                st.session_state.onb_color_mode = "duo"
                st.session_state.onb_colors_sel = []
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Mode couleur simple ───────────────────────────────────────────────
        if st.session_state.onb_color_mode == "simple":
            cols = st.columns(3)
            for idx, couleur in enumerate(COULEURS_SIMPLES):
                with cols[idx % 3]:
                    is_sel  = couleur['nom'] in st.session_state.onb_colors_sel
                    txt_clr = "#0D1B2A" if couleur['nom'] in COULEURS_LIGHT else "white"
                    check   = "✓ " if is_sel else ""
                    border  = "3px solid #B8974A" if is_sel else "1px solid #E0D8CE"

                    st.markdown(f"""
                    <div style="margin-bottom:0.3rem">
                        <div style="height:38px;border-radius:8px;background:{couleur['hex']};
                        border:{border};display:flex;align-items:center;justify-content:center;
                        font-size:0.75rem;color:{txt_clr};font-weight:700;margin-bottom:0.2rem">
                            {check}{couleur['nom']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button(couleur['nom'], key=f"sc_{couleur['nom']}_{cat}", use_container_width=True):
                        if couleur['nom'] in st.session_state.onb_colors_sel:
                            st.session_state.onb_colors_sel.remove(couleur['nom'])
                        else:
                            st.session_state.onb_colors_sel.append(couleur['nom'])
                        st.rerun()

        # ── Mode duo de couleurs ──────────────────────────────────────────────
        else:
            for duo in COULEURS_DUOS:
                is_sel = duo['nom'] in st.session_state.onb_colors_sel
                border = "3px solid #B8974A" if is_sel else "1px solid #E0D8CE"
                check  = "✓ " if is_sel else ""
                bg     = "rgba(184,151,74,0.08)" if is_sel else "white"

                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:0.8rem;
                background:{bg};border:{border};border-radius:10px;
                padding:0.6rem 1rem;margin-bottom:0.4rem">
                    <div style="display:flex;gap:3px;flex-shrink:0">
                        <div style="width:20px;height:20px;border-radius:4px;
                        background:{duo['hex1']};border:1px solid rgba(0,0,0,0.1)"></div>
                        <div style="width:20px;height:20px;border-radius:4px;
                        background:{duo['hex2']};border:1px solid rgba(0,0,0,0.1)"></div>
                    </div>
                    <div style="font-size:0.85rem;color:#0D1B2A;
                    font-weight:{'700' if is_sel else '400'}">
                        {check}{duo['nom']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(duo['nom'], key=f"duo_{duo['nom']}_{cat}", use_container_width=True):
                    if duo['nom'] in st.session_state.onb_colors_sel:
                        st.session_state.onb_colors_sel.remove(duo['nom'])
                    else:
                        st.session_state.onb_colors_sel.append(duo['nom'])
                    st.rerun()

        # Résumé couleurs sélectionnées
        if st.session_state.onb_colors_sel:
            st.markdown(f"""
            <div style="padding:0.8rem 1rem;background:#F7F5F0;border-radius:10px;
            font-size:0.82rem;color:#0D1B2A;margin-top:0.8rem">
                <b>Sélectionnées ({len(st.session_state.onb_colors_sel)}) :</b>
                {' · '.join(st.session_state.onb_colors_sel)}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Retour", use_container_width=True, type="secondary", key=f"back_col_{cat}"):
                st.session_state.onb_current_item = None
                st.session_state.onb_colors_sel   = []
                st.rerun()
        with col2:
            nb = len(st.session_state.onb_colors_sel)
            if st.button(
                f"✓ Ajouter {nb} {item['type']}{'s' if nb > 1 else ''}",
                use_container_width=True,
                type="primary",
                disabled=nb == 0,
                key=f"add_{cat}"
            ):
                for couleur in st.session_state.onb_colors_sel:
                    # Nom final : custom si rempli, sinon "Type Couleur"
                    nom_final = nom_custom.strip() if nom_custom.strip() else f"{item['type']} {couleur}"
                    st.session_state.onb_selections.append({
                        "type":        item['type'],
                        "emoji":       item['emoji'],
                        "category":    cat,
                        "subcategory": item['subcategory'],
                        "color":       couleur,
                        "formality":   item['formality'],
                        "warmth":      item['warmth'],
                        "nom_final":   nom_final,
                    })
                st.success(f"✅ {nb} {item['type']}(s) ajouté(s) !")
                st.session_state.onb_current_item = None
                st.session_state.onb_colors_sel   = []
                st.rerun()

    else:
        # ── Grille types de vêtements ─────────────────────────────────────────
        cols = st.columns(3)
        for idx, item in enumerate(items):
            with cols[idx % 3]:
                count = sum(1 for s in st.session_state.onb_selections
                           if s['type'] == item['type'] and s['category'] == cat)
                badge = f" +{count}" if count > 0 else ""
                if st.button(
                    f"{item['emoji']} {item['type']}{badge}",
                    key=f"item_{cat}_{idx}",
                    use_container_width=True
                ):
                    st.session_state.onb_current_item = item
                    st.session_state.onb_colors_sel   = []
                    st.session_state.onb_color_mode   = "simple"
                    st.rerun()

        # Résumé sélections
        cat_selections = [s for s in st.session_state.onb_selections if s['category'] == cat]
        if cat_selections:
            st.markdown(f"""
            <div style="margin-top:1rem;padding:0.8rem 1rem;background:#F7F5F0;
            border-radius:10px;font-size:0.82rem;color:#0D1B2A">
                <b>Sélectionnés ({len(cat_selections)}) :</b><br>
                {' · '.join([f"{s['emoji']} {s['nom_final']}" for s in cat_selections])}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.onb_step > 1:
                if st.button("← Retour", use_container_width=True, type="secondary", key=f"back_{cat}"):
                    cats = ["Haut", "Bas", "Chaussures"]
                    st.session_state.onb_step    -= 1
                    st.session_state.onb_category = cats[st.session_state.onb_step - 1]
                    st.rerun()
        with col2:
            next_label = "Continuer →" if st.session_state.onb_step < 3 else "Terminer ✓"
            if st.button(next_label, use_container_width=True, type="primary", key=f"next_{cat}"):
                cats = ["Haut", "Bas", "Chaussures"]
                if st.session_state.onb_step < 3:
                    st.session_state.onb_step    += 1
                    st.session_state.onb_category = cats[st.session_state.onb_step - 1]
                else:
                    st.session_state.onb_step = 4
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# ÉTAPE 4 — Confirmation et enregistrement
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.onb_step == 4:

    total = len(st.session_state.onb_selections)

    st.markdown(f"""
    <div style="text-align:center;padding:1rem 0">
        <div style="font-size:3rem">🎉</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.4rem;
        font-weight:800;color:#0D1B2A;margin-top:0.5rem">
            {total} vêtements sélectionnés !
        </div>
        <div style="font-size:0.85rem;color:#8A8A8A;margin-top:0.3rem">
            Vérifie ta sélection avant de confirmer
        </div>
    </div>
    """, unsafe_allow_html=True)

    for cat in ["Haut", "Bas", "Chaussures"]:
        cat_items = [s for s in st.session_state.onb_selections if s['category'] == cat]
        if cat_items:
            st.markdown(f"**{cat}s ({len(cat_items)})**")
            for item in cat_items:
                st.markdown(f"• {item['emoji']} {item['nom_final']} — {item['color']}")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Modifier", use_container_width=True, type="secondary"):
            st.session_state.onb_step     = 1
            st.session_state.onb_category = "Haut"
            st.rerun()
    with col2:
        if st.button("✓ Confirmer ma garde-robe", use_container_width=True, type="primary"):
            today   = datetime.today().strftime("%Y-%m-%d")
            records = []
            for item in st.session_state.onb_selections:
                records.append({
                    "item_name":       item['nom_final'],
                    "category":        item['category'],
                    "subcategory":     item['subcategory'],
                    "color":           item['color'],
                    "material":        "Coton",
                    "warmth_level":    item['warmth'],
                    "formality_level": item['formality'],
                    "season":          "Toutes",
                    "condition":       "Bon",
                    "is_active":       True,
                    "created_at":      today,
                    "user_id":         USER_ID
                })

            with st.spinner(f"Enregistrement de {len(records)} vêtements..."):
                supabase.table("vetements").insert(records).execute()

            with st.spinner("Calcul de tes premières recommandations..."):
                subprocess.run(
                    [r"C:\Projects\smartwardrobe\dbt-env\Scripts\dbt.exe", "run"],
                    cwd=r"C:\Projects\smartwardrobe\ats_outfit",
                    capture_output=True
                )

            st.success(f"✅ {len(records)} vêtements ajoutés — recommandations prêtes !")
            st.session_state.onb_step         = 1
            st.session_state.onb_selections   = []
            st.session_state.onb_current_item = None

            st.balloons()
            import time
            time.sleep(2)
            st.switch_page("pages/1_Recommandation.py")