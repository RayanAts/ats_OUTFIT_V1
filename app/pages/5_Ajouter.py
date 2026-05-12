# ============================================
# PAGE 5 - Ajouter un vetement
# ============================================
import streamlit as st
import sys, os, json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from styles import GLOBAL_CSS

st.set_page_config(page_title="Ajouter · SmartWardrobe", page_icon="➕", layout="centered")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────────────────────────
CATEGORIES = {
    "Haut":       ["Chemise", "T-shirt", "Pull", "Sweat", "Blazer", "Veste", "Manteau", "Doudoune", "Cardigan"],
    "Bas":        ["Jean", "Chino", "Pantalon", "Short"],
    "Chaussures": ["Sneaker", "Richelieu", "Boot", "Chelsea Boot", "Mocassin"],
}

CAT_EMOJIS = {"Haut": "👕", "Bas": "👖", "Chaussures": "👟"}

COULEURS = {
    "Noir":     "#1a1a1a",
    "Blanc":    "#F0EEE9",
    "Gris":     "#9E9E9E",
    "Marine":   "#1B2A4A",
    "Bleu":     "#4A90D9",
    "Beige":    "#D4C5A9",
    "Camel":    "#C19A6B",
    "Marron":   "#6B3F2A",
    "Kaki":     "#7D8C5A",
    "Bordeaux": "#722F37",
    "Rouge":    "#C0392B",
    "Vert":     "#2ECC71",
}

COULEURS_LIGHT = ["Blanc", "Beige", "Camel", "Gris"]

MATIERES = {
    "Coton":     {"emoji": "🌿", "desc": "Léger, respirant"},
    "Laine":     {"emoji": "🐑", "desc": "Chaud, hivernal"},
    "Lin":       {"emoji": "🌾", "desc": "Frais, estival"},
    "Denim":     {"emoji": "👖", "desc": "Résistant, casual"},
    "Cuir":      {"emoji": "🐄", "desc": "Premium, durable"},
    "Nylon":     {"emoji": "🧪", "desc": "Technique, léger"},
    "Polyester": {"emoji": "⚙️", "desc": "Résistant, facile"},
    "Cachemire": {"emoji": "✨", "desc": "Luxe, ultra-doux"},
}

SAISONS = {
    "Toutes":    "🗓️",
    "Printemps": "🌸",
    "Ete":       "☀️",
    "Automne":   "🍂",
    "Hiver":     "❄️",
}

NEW_ITEMS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "new_items_local"
)

# ── State ─────────────────────────────────────────────────────────────────────
if "step"  not in st.session_state: st.session_state.step  = 1
if "item"  not in st.session_state: st.session_state.item  = {}
if "added" not in st.session_state: st.session_state.added = False

def go_next():
    st.session_state.step += 1

def reset():
    st.session_state.step  = 1
    st.session_state.item  = {}
    st.session_state.added = False

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="sw-page-header">
    <div class="sw-page-eyebrow">Garde-robe</div>
    <h1 class="sw-page-title">Ajouter un vetement</h1>
    <p class="sw-page-sub">En 30 secondes chrono</p>
</div>
""", unsafe_allow_html=True)

# ── Progress bar ──────────────────────────────────────────────────────────────
if not st.session_state.added:
    progress = int(((st.session_state.step - 1) / 5) * 100)
    st.markdown(f"""
    <div style="background:rgba(13,27,42,0.08);border-radius:99px;height:4px;margin-bottom:0.5rem">
        <div style="background:linear-gradient(90deg,#0D1B2A,#B8974A);height:100%;
        border-radius:99px;width:{progress}%"></div>
    </div>
    <div style="font-size:0.78rem;color:#8A8A8A;margin-bottom:2rem">
        Etape {st.session_state.step} sur 5
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SUCCES
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.added:

    st.markdown("""
    <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:16px;
    padding:2.5rem;text-align:center;margin-top:1rem">
        <div style="font-size:3rem">✓</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;
        color:#0D1B2A;margin-top:0.8rem">Vetement ajoute !</div>
        <div style="font-size:0.85rem;color:#8A8A8A;margin-top:0.4rem">
            Il sera synchronise dans ta garde-robe automatiquement.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Ajouter un autre vetement", use_container_width=True, type="primary"):
        reset()
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# ETAPE 1 — Categorie
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 1:

    st.markdown("""
    <p style="font-family:'Syne',sans-serif;font-size:1.2rem;font-weight:700;
    color:#0D1B2A;margin-bottom:1.5rem">C'est quel type de vetement ?</p>
    """, unsafe_allow_html=True)

    for cat, emoji in CAT_EMOJIS.items():
        if st.button(f"{emoji}  {cat}", use_container_width=True,
                     type="secondary", key=f"cat_{cat}"):
            st.session_state.item["category"] = cat
            go_next()
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# ETAPE 2 — Sous-categorie
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 2:

    cat     = st.session_state.item["category"]
    subcats = CATEGORIES[cat]

    st.markdown("""
    <p style="font-family:'Syne',sans-serif;font-size:1.2rem;font-weight:700;
    color:#0D1B2A;margin-bottom:1.5rem">Quelle sous-categorie ?</p>
    """, unsafe_allow_html=True)

    cols = st.columns(2)
    for i, sub in enumerate(subcats):
        if cols[i % 2].button(sub, use_container_width=True,
                              type="secondary", key=f"sub_{sub}"):
            st.session_state.item["subcategory"] = sub
            go_next()
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Retour", type="secondary", key="back_2"):
        st.session_state.step -= 1
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# ETAPE 3 — Couleur, Matiere, Saison, Nom
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 3:

    item = st.session_state.item

    # --- Couleur ---
    st.markdown("""
    <div style="font-size:0.78rem;color:#8A8A8A;text-transform:uppercase;
    letter-spacing:0.1em;margin-bottom:1rem">Couleur principale</div>
    """, unsafe_allow_html=True)

    couleur_sel = item.get("color", list(COULEURS.keys())[0])

    colors_html = '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.7rem;margin-bottom:1rem">'
    for nom, hex_c in COULEURS.items():
        is_sel  = couleur_sel == nom
        border  = "3px solid #B8974A" if is_sel else "2px solid rgba(13,27,42,0.08)"
        txt_clr = "#0D1B2A" if nom in COULEURS_LIGHT else "white"
        check   = "✓" if is_sel else ""
        colors_html += f"""
        <div style="text-align:center">
            <div style="height:42px;border-radius:10px;background:{hex_c};border:{border};
            display:flex;align-items:center;justify-content:center;
            font-size:0.9rem;color:{txt_clr};font-weight:700">{check}</div>
            <div style="font-size:0.7rem;color:#8A8A8A;margin-top:0.3rem">{nom}</div>
        </div>"""
    colors_html += "</div>"
    st.markdown(colors_html, unsafe_allow_html=True)

    couleur_sel = st.selectbox(
        "Couleur", list(COULEURS.keys()),
        index=list(COULEURS.keys()).index(couleur_sel),
        label_visibility="collapsed", key="sel_couleur"
    )
    st.session_state.item["color"] = couleur_sel

    hex_sel = COULEURS[couleur_sel]
    txt_sel = "#0D1B2A" if couleur_sel in COULEURS_LIGHT else "white"
    st.markdown(f"""
    <div style="height:36px;border-radius:10px;background:{hex_sel};
    display:flex;align-items:center;justify-content:center;
    font-size:0.85rem;color:{txt_sel};font-weight:600;margin-bottom:1.5rem">
        {couleur_sel}
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sw-divider"></div>', unsafe_allow_html=True)

    # --- Matiere ---
    st.markdown("""
    <div style="font-size:0.78rem;color:#8A8A8A;text-transform:uppercase;
    letter-spacing:0.1em;margin-bottom:0.8rem">Matiere</div>
    """, unsafe_allow_html=True)

    matiere_sel = item.get("material", None)

    for nom_mat, info in MATIERES.items():
        is_sel = matiere_sel == nom_mat
        check  = "  ✓" if is_sel else ""
        if st.button(
            f"{info['emoji']}  {nom_mat}  —  {info['desc']}{check}",
            key=f"mat_{nom_mat}", use_container_width=True
        ):
            st.session_state.item["material"] = nom_mat
            st.rerun()

    st.markdown('<div class="sw-divider"></div>', unsafe_allow_html=True)

    # --- Saison ---
    st.markdown("""
    <div style="font-size:0.78rem;color:#8A8A8A;text-transform:uppercase;
    letter-spacing:0.1em;margin-bottom:0.8rem">Saison</div>
    """, unsafe_allow_html=True)

    saison_sel  = item.get("season", list(SAISONS.keys())[0])
    saison_html = '<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:0.5rem;margin-bottom:1rem">'
    for nom_s, emoji_s in SAISONS.items():
        is_sel = saison_sel == nom_s
        border = "2px solid #B8974A" if is_sel else "1px solid rgba(13,27,42,0.08)"
        bg     = "rgba(184,151,74,0.08)" if is_sel else "white"
        saison_html += f"""
        <div style="background:{bg};border:{border};border-radius:10px;
        padding:0.6rem 0.2rem;text-align:center">
            <div style="font-size:1.4rem">{emoji_s}</div>
            <div style="font-size:0.65rem;color:#8A8A8A;margin-top:0.2rem">{nom_s}</div>
        </div>"""
    saison_html += "</div>"
    st.markdown(saison_html, unsafe_allow_html=True)

    saison_sel = st.selectbox(
        "Saison", list(SAISONS.keys()),
        index=list(SAISONS.keys()).index(saison_sel),
        label_visibility="collapsed", key="sel_saison"
    )
    st.session_state.item["season"] = saison_sel

    st.markdown('<div class="sw-divider"></div>', unsafe_allow_html=True)

    # --- Nom ---
    nom = st.text_input(
        "Nom du vetement", placeholder="ex: Blazer Marine Zara",
        value=item.get("name", ""), key="input_nom"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    matiere_ok = st.session_state.item.get("material") is not None
    nom_ok     = nom.strip() != ""
    tout_ok    = matiere_ok and nom_ok

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Retour", use_container_width=True, type="secondary", key="back_3"):
            st.session_state.step -= 1
            st.rerun()
    with col2:
        if st.button("Continuer →", use_container_width=True, type="primary",
                     disabled=not tout_ok, key="next_3"):
            st.session_state.item["name"] = nom.strip()
            go_next()
            st.rerun()

    if not tout_ok:
        st.markdown("""
        <div style="font-size:0.78rem;color:#B8974A;margin-top:0.5rem">
            Selectionne une matiere et donne un nom a ton vetement
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ETAPE 4 — Formalite / Chaleur / Etat
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 4:

    st.markdown("""
    <p style="font-family:'Syne',sans-serif;font-size:1.2rem;font-weight:700;
    color:#0D1B2A;margin-bottom:1.5rem">Quelques reglages rapides</p>
    """, unsafe_allow_html=True)

    # Formalite
    st.markdown("""
    <div style="font-size:0.78rem;color:#8A8A8A;text-transform:uppercase;
    letter-spacing:0.1em;margin-bottom:0.3rem">Formalite</div>
    <div style="font-size:0.82rem;color:#0D1B2A;margin-bottom:0.5rem">
    1 = tres casual &nbsp;·&nbsp; 5 = tres formel
    </div>
    """, unsafe_allow_html=True)

    formality = st.slider("Formalite", 1, 5,
                          st.session_state.item.get("formality", 3),
                          label_visibility="collapsed", key="sl_form")

    dots_f = "".join([
        f'<span style="display:inline-block;width:12px;height:12px;border-radius:50%;'
        f'margin-right:5px;background:{"#0D1B2A" if d < formality else "rgba(13,27,42,0.1)"}"></span>'
        for d in range(5)
    ])
    st.markdown(f'<div style="margin-bottom:1.5rem">{dots_f}</div>', unsafe_allow_html=True)

    st.markdown('<div class="sw-divider"></div>', unsafe_allow_html=True)

    # Chaleur
    st.markdown("""
    <div style="font-size:0.78rem;color:#8A8A8A;text-transform:uppercase;
    letter-spacing:0.1em;margin-bottom:0.3rem">Chaleur</div>
    <div style="font-size:0.82rem;color:#0D1B2A;margin-bottom:0.5rem">
    1 = tres leger &nbsp;·&nbsp; 5 = tres chaud
    </div>
    """, unsafe_allow_html=True)

    warmth = st.slider("Chaleur", 1, 5,
                       st.session_state.item.get("warmth", 2),
                       label_visibility="collapsed", key="sl_warm")

    dots_w = "".join([
        f'<span style="display:inline-block;width:12px;height:12px;border-radius:50%;'
        f'margin-right:5px;background:{"#B8974A" if d < warmth else "rgba(13,27,42,0.1)"}"></span>'
        for d in range(5)
    ])
    st.markdown(f'<div style="margin-bottom:1.5rem">{dots_w}</div>', unsafe_allow_html=True)

    st.markdown('<div class="sw-divider"></div>', unsafe_allow_html=True)

    # Etat
    st.markdown("""
    <div style="font-size:0.78rem;color:#8A8A8A;text-transform:uppercase;
    letter-spacing:0.1em;margin-bottom:0.8rem">Etat du vetement</div>
    """, unsafe_allow_html=True)

    condition = st.radio("Etat", ["Bon", "Use", "Abime"],
                         horizontal=True, label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Retour", use_container_width=True, type="secondary", key="back_4"):
            st.session_state.step -= 1
            st.rerun()
    with col2:
        if st.button("Continuer →", use_container_width=True, type="primary", key="next_4"):
            st.session_state.item["formality"] = formality
            st.session_state.item["warmth"]    = warmth
            st.session_state.item["condition"] = condition
            go_next()
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# ETAPE 5 — Confirmation & Enregistrement
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 5:

    item = st.session_state.item

    st.markdown("""
    <p style="font-family:'Syne',sans-serif;font-size:1.2rem;font-weight:700;
    color:#0D1B2A;margin-bottom:1.2rem">Recap avant d'ajouter</p>
    """, unsafe_allow_html=True)

    dots_f = "".join([
        f'<span style="display:inline-block;width:10px;height:10px;border-radius:50%;'
        f'margin-right:4px;background:{"#0D1B2A" if d < item.get("formality",1) else "rgba(13,27,42,0.1)"}"></span>'
        for d in range(5)
    ])
    dots_w = "".join([
        f'<span style="display:inline-block;width:10px;height:10px;border-radius:50%;'
        f'margin-right:4px;background:{"#B8974A" if d < item.get("warmth",1) else "rgba(13,27,42,0.1)"}"></span>'
        for d in range(5)
    ])

    hex_c = COULEURS.get(item.get("color", "Noir"), "#1a1a1a")
    emoji = CAT_EMOJIS.get(item.get("category", "Haut"), "👔")

    st.markdown(f"""
    <div style="background:white;border:1px solid rgba(13,27,42,0.08);
    border-radius:16px;padding:1.5rem;margin-bottom:1.5rem">

        <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.2rem">
            <div style="font-size:2.5rem">{emoji}</div>
            <div>
                <div style="font-family:'Syne',sans-serif;font-size:1.1rem;
                font-weight:800;color:#0D1B2A">{item.get("name","")}</div>
                <div style="font-size:0.82rem;color:#8A8A8A;margin-top:0.2rem">
                    {item.get("category","")} · {item.get("subcategory","")}
                </div>
            </div>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1.2rem">
            <div>
                <div style="font-size:0.7rem;color:#8A8A8A;text-transform:uppercase;
                letter-spacing:0.1em;margin-bottom:0.3rem">Couleur</div>
                <div style="display:flex;align-items:center;gap:0.5rem">
                    <div style="width:16px;height:16px;border-radius:50%;background:{hex_c};
                    border:1px solid rgba(13,27,42,0.1)"></div>
                    <span style="font-size:0.88rem;color:#0D1B2A">{item.get("color","")}</span>
                </div>
            </div>
            <div>
                <div style="font-size:0.7rem;color:#8A8A8A;text-transform:uppercase;
                letter-spacing:0.1em;margin-bottom:0.3rem">Matiere</div>
                <div style="font-size:0.88rem;color:#0D1B2A">{item.get("material","")}</div>
            </div>
            <div>
                <div style="font-size:0.7rem;color:#8A8A8A;text-transform:uppercase;
                letter-spacing:0.1em;margin-bottom:0.3rem">Saison</div>
                <div style="font-size:0.88rem;color:#0D1B2A">{item.get("season","")}</div>
            </div>
            <div>
                <div style="font-size:0.7rem;color:#8A8A8A;text-transform:uppercase;
                letter-spacing:0.1em;margin-bottom:0.3rem">Etat</div>
                <div style="font-size:0.88rem;color:#0D1B2A">{item.get("condition","")}</div>
            </div>
        </div>

        <div style="margin-bottom:0.8rem">
            <div style="font-size:0.7rem;color:#8A8A8A;text-transform:uppercase;
            letter-spacing:0.1em;margin-bottom:0.4rem">Formalite</div>
            {dots_f}
        </div>

        <div>
            <div style="font-size:0.7rem;color:#8A8A8A;text-transform:uppercase;
            letter-spacing:0.1em;margin-bottom:0.4rem">Chaleur</div>
            {dots_w}
        </div>

    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("← Modifier", use_container_width=True, type="secondary", key="back_5"):
            st.session_state.step -= 1
            st.rerun()

    with col2:
        if st.button("✓ Ajouter", use_container_width=True, type="primary", key="btn_add"):
            try:
                from onelake import upload_new_item
                from datetime import datetime

                today = datetime.today().strftime("%Y-%m-%d")
                now   = datetime.today().strftime("%Y%m%d_%H%M%S")

                new_item = {
                    "item_name":       item["name"],
                    "category":        item["category"],
                    "subcategory":     item["subcategory"],
                    "color":           item["color"],
                    "material":        item["material"],
                    "warmth_level":    item["warmth"],
                    "formality_level": item["formality"],
                    "season":          item["season"],
                    "condition":       item["condition"],
                    "is_active":       True,
                    "created_at":      today
                }

                filename = f"new_item_{now}.json"

                with st.spinner("Synchronisation avec ta garde-robe..."):
                    upload_new_item(new_item, filename)

                st.session_state.added = True
                st.rerun()

            except Exception as e:
                st.error(f"Erreur lors de l'ajout : {e}")

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