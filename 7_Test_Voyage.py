import streamlit as st
from datetime import datetime

# Configuration page
st.set_page_config(page_title="Test Mode Voyage - Options A & B", layout="wide")

# Titre
st.title("🧳 Test Mode Voyage - Options A vs B")
st.markdown("Comparer les deux approches UX pour la sélection vêtements")
st.divider()

# ═══════════════════════════════════════════════════════════
# DONNÉES DE TEST
# ═══════════════════════════════════════════════════════════

# Vêtements disponibles
wardrobe = {
    "Hauts": ["Chemise blanche", "T-shirt noir", "Pull gris", "Polo bleu", "Hoodie", "Blazer"],
    "Bas": ["Jeans bleu", "Chino beige", "Pantalon noir", "Short noir", "Jogging gris"],
    "Chaussures": ["Air Force", "Chelsea boots", "Loafers", "Sneakers colorées"]
}

# Sélection IA (ce qu'on propose)
ai_selection = {
    "Hauts": ["Chemise blanche", "Pull gris"],
    "Bas": ["Jeans bleu"],
    "Chaussures": ["Air Force"]
}

# ═══════════════════════════════════════════════════════════
# SESSION STATE (pour tracker les choix utilisateur)
# ═══════════════════════════════════════════════════════════

if "option_a_selections" not in st.session_state:
    st.session_state.option_a_selections = {
        "Hauts": ai_selection["Hauts"].copy(),
        "Bas": ai_selection["Bas"].copy(),
        "Chaussures": ai_selection["Chaussures"].copy()
    }

if "option_b_selections" not in st.session_state:
    st.session_state.option_b_selections = {
        "Hauts": ai_selection["Hauts"].copy(),
        "Bas": ai_selection["Bas"].copy(),
        "Chaussures": ai_selection["Chaussures"].copy()
    }

# ═══════════════════════════════════════════════════════════
# FONCTION : Afficher une catégorie avec 2 colonnes
# ═══════════════════════════════════════════════════════════

def render_category(category, selections, option_key):
    """
    Affiche une catégorie avec deux colonnes (IA vs User)
    category: str (ex: "Hauts")
    selections: dict des sélections actuelles
    option_key: str ("A" ou "B") pour identifier les clés session_state
    """
    col1, col2 = st.columns(2, gap="medium")
    
    # ===== COLONNE 1 : SÉLECTION IA =====
    with col1:
        st.markdown("### 🤖 Sélection IA")
        ai_items = ai_selection[category]
        ai_count = len([item for item in selections[category] if item in ai_items])
        st.markdown(f"**{ai_count}/{len(ai_items)} sélectionnés**")
        
        # Affichage chips IA
        chips_ia = []
        for item in ai_items:
            if item in selections[category]:
                # Item sélectionné = chip visible avec ×
                chips_ia.append(f"🏷️ {item}")
            else:
                # Item non-sélectionné = grisé ou caché
                chips_ia.append(f"⚪ ~~{item}~~")
        
        st.markdown(" | ".join(chips_ia) if chips_ia else "Aucune sélection")
    
    # ===== COLONNE 2 : SÉLECTION USER =====
    with col2:
        st.markdown("### 👤 Ma sélection")
        user_items = selections[category]
        user_count = len(user_items)
        total_available = len(wardrobe[category])
        st.markdown(f"**{user_count}/{total_available} sélectionnés**")
        
        # Multiselect pour user
        selected = st.multiselect(
            label=f"Choisir {category.lower()}",
            options=wardrobe[category],
            default=user_items,
            key=f"{option_key}_{category}_select",
            label_visibility="collapsed"
        )
        
        # Update session state
        selections[category] = selected
        
        # Affichage chips User
        chips_user = [f"✓ {item}" for item in selected]
        st.markdown(" | ".join(chips_user) if chips_user else "Aucune sélection")

# ═══════════════════════════════════════════════════════════
# OPTION A : TABS
# ═══════════════════════════════════════════════════════════

st.markdown("---")
st.header("📑 OPTION A : TABS par catégorie")
st.markdown("Une catégorie visible à la fois. Clic facile sur mobile.")

tab_hauts, tab_bas, tab_chaussures = st.tabs(["👕 HAUTS", "👖 BAS", "👞 CHAUSSURES"])

with tab_hauts:
    st.markdown("### Hauts")
    render_category("Hauts", st.session_state.option_a_selections, "A")

with tab_bas:
    st.markdown("### Bas")
    render_category("Bas", st.session_state.option_a_selections, "A")

with tab_chaussures:
    st.markdown("### Chaussures")
    render_category("Chaussures", st.session_state.option_a_selections, "A")

# Résumé Option A
st.markdown("#### 📊 Résumé Option A")
total_a = sum(len(items) for items in st.session_state.option_a_selections.values())
st.info(f"✅ Total sélectionné : **{total_a} pièces**")

# ═══════════════════════════════════════════════════════════
# OPTION B : ACCORDION
# ═══════════════════════════════════════════════════════════

st.markdown("---")
st.header("📂 OPTION B : ACCORDION (Expand/Collapse)")
st.markdown("Toutes les catégories visibles. Expand au besoin.")

with st.expander("👕 HAUTS", expanded=True):
    render_category("Hauts", st.session_state.option_b_selections, "B")

with st.expander("👖 BAS", expanded=True):
    render_category("Bas", st.session_state.option_b_selections, "B")

with st.expander("👞 CHAUSSURES", expanded=True):
    render_category("Chaussures", st.session_state.option_b_selections, "B")

# Résumé Option B
st.markdown("#### 📊 Résumé Option B")
total_b = sum(len(items) for items in st.session_state.option_b_selections.values())
st.info(f"✅ Total sélectionné : **{total_b} pièces**")

# ═══════════════════════════════════════════════════════════
# COMPARAISON
# ═══════════════════════════════════════════════════════════

st.markdown("---")
st.header("🔍 Comparaison")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### ✅ Option A : TABS")
    st.markdown("""
    **Avantages :**
    - Une catégorie visible → moins de scroll
    - Tabs faciles sur mobile (big tap target)
    - Pas de scroll interne piégeux
    - Clean et minimaliste
    
    **Inconvénients :**
    - Doit changer de tab pour voir autres catégories
    - Moins "une vue d'ensemble"
    """)

with col2:
    st.markdown("### ✅ Option B : ACCORDION")
    st.markdown("""
    **Avantages :**
    - Toutes catégories visibles au repos
    - Expand au besoin (contrôle utilisateur)
    - Vue d'ensemble rapide
    - Scroll page normal (pas interne)
    
    **Inconvénients :**
    - Peut être long sur mobile (beaucoup de scrolling page)
    - Plus d'éléments visibles = potentiellement overload
    """)

st.markdown("---")
st.markdown("**🎯 À tester :** Cliquez dans chaque onglet/accordion. Décochez/Cochez des items. Voyez comment les compteurs et chips évoluent.")