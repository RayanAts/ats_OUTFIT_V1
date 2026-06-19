# ============================================
# PAGE 6 - Mode Voyage
# ============================================
import streamlit as st
from connector import get_supabase
supabase = get_supabase()
import sys
import os
import requests
import time
import math
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / ".env")

from styles import GLOBAL_CSS
from auth import require_auth


supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

st.set_page_config(page_title="Mode Voyage · SmartWardrobe", page_icon="🧳", layout="centered")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

USER_ID = require_auth()
NOM = st.session_state.get('nom', '')

# ── Dictionnaires ─────────────────────────────────────────────────────────────
WEATHER_EMOJIS = {
    "Ciel dégagé": "☀️", "Nuageux": "⛅", "Couvert": "☁️",
    "Brouillard": "🌫️", "Pluie légère": "🌦️", "Pluie": "🌧️",
    "Averses": "🌧️", "Orage": "⛈️", "Variable": "🌤️"
}
WEATHER_LABELS = {
    0: "Ciel dégagé", 1: "Nuageux", 2: "Nuageux", 3: "Couvert",
    45: "Brouillard", 48: "Brouillard", 51: "Pluie légère",
    53: "Pluie légère", 61: "Pluie", 63: "Pluie", 65: "Pluie",
    80: "Averses", 81: "Averses", 82: "Averses", 95: "Orage", 96: "Orage"
}

# ── State ─────────────────────────────────────────────────────────────────────
if 'voyage_step' not in st.session_state: st.session_state.voyage_step = 1
if 'voyage_data' not in st.session_state: st.session_state.voyage_data = {}
if 'voyage_meteo' not in st.session_state: st.session_state.voyage_meteo = None
if 'voyage_vetements' not in st.session_state: st.session_state.voyage_vetements = []
if 'voyage_suggested' not in st.session_state: st.session_state.voyage_suggested = False
if 'voyage_city_choice' not in st.session_state: st.session_state.voyage_city_choice = None

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="sw-page-header">'
    f'<div class="sw-page-eyebrow">SmartWardrobe · 👤 {NOM}</div>'
    '<h1 class="sw-page-title">Mode Voyage 🧳</h1>'
    '<p class="sw-page-sub">Prépare ta valise intelligemment</p>'
    '</div>',
    unsafe_allow_html=True
)

# ── Progress bar ──────────────────────────────────────────────────────────────
steps = ["Destination", "Vêtements", "Confirmation"]
current = min(st.session_state.voyage_step - 1, 2)
progress = current / 2
steps_html = ''.join([
    f'<span style="font-size:0.7rem;color:{"#B8974A" if i <= current else "#8A8A8A"};font-weight:{"700" if i == current else "400"}">{s}</span>'
    for i, s in enumerate(steps)
])
st.markdown(
    '<div style="margin-bottom:1.5rem">'
    '<div style="background:#E0D8CE;border-radius:99px;height:6px">'
    f'<div style="background:#B8974A;border-radius:99px;height:6px;width:{int(progress*100)}%;transition:width 0.3s"></div>'
    '</div>'
    f'<div style="display:flex;justify-content:space-between;margin-top:0.4rem">{steps_html}</div>'
    '</div>',
    unsafe_allow_html=True
)

# ── Fonctions ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def search_cities(query_str):
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": query_str, "format": "json", "limit": 6,
                    "featuretype": "city", "addressdetails": 1},
            headers={"User-Agent": "SmartWardrobe/1.0"},
            timeout=5
        )
        results = []
        for item in r.json():
            addr = item.get("address", {})
            ville = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("municipality") or item.get("display_name", "").split(",")[0]
            pays = addr.get("country", "")
            region = addr.get("state", "")
            label = ", ".join([p for p in [ville, region, pays] if p])
            results.append({"label": label, "ville": ville,
                            "lat": float(item["lat"]), "lon": float(item["lon"])})
        seen, unique = set(), []
        for r_ in results:
            if r_["label"] not in seen:
                seen.add(r_["label"])
                unique.append(r_)
        return unique
    except Exception:
        return []

def get_meteo_voyage(lat, lon, d_depart, d_retour):
    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat, "longitude": lon,
                "daily": ["temperature_2m_max", "temperature_2m_min", "weathercode"],
                "timezone": "auto",
                "start_date": d_depart.strftime("%Y-%m-%d"),
                "end_date": min(d_retour, d_depart + timedelta(days=15)).strftime("%Y-%m-%d")
            },
            timeout=5
        )
        daily = r.json().get("daily", {})
        if not daily:
            return None
        temps_max = daily.get("temperature_2m_max", [])
        temps_min = daily.get("temperature_2m_min", [])
        dates = daily.get("time", [])
        wcodes = daily.get("weathercode", [])
        if not (temps_max and temps_min):
            return None
        jours = []
        for i in range(len(temps_max)):
            wc = wcodes[i] if i < len(wcodes) else 0
            jours.append({
                "date": dates[i] if i < len(dates) else "",
                "max": round(temps_max[i], 1),
                "min": round(temps_min[i], 1),
                "label": WEATHER_LABELS.get(wc, "Variable")
            })
        avg_max = round(sum(temps_max) / len(temps_max), 1)
        avg_min = round(sum(temps_min) / len(temps_min), 1)
        avg_temp = round((avg_max + avg_min) / 2, 1)
        labels_list = [j["label"] for j in jours]
        label_dominant = max(set(labels_list), key=labels_list.count)
        return {
            "temp_avg": avg_temp, "temp_max": avg_max, "temp_min": avg_min,
            "label": label_dominant, "nb_jours": len(temps_max), "jours": jours
        }
    except Exception:
        return None

def suggerer_essentiel(user_id, temp_avg, nb_jours):
    """Sélection proportionnelle à la durée du voyage"""
    try:
        if temp_avg >= 22:
            warmth_target = [1, 2]
        elif temp_avg >= 14:
            warmth_target = [1, 2, 3]
        else:
            warmth_target = [3, 4, 5]

        # Quotas dynamiques selon la durée
        nb_hauts = max(2, math.ceil(nb_jours / 1.5))
        nb_bas   = max(1, math.ceil(nb_jours / 3))
        nb_shoes = 1 if nb_jours <= 4 else (2 if nb_jours <= 10 else 3)
        quotas = {"Haut": nb_hauts, "Bas": nb_bas, "Chaussures": nb_shoes}

        # Récupère les items likés
        liked_result = supabase.table("retours") \
            .select("nom_vetement") \
            .eq("user_id", user_id) \
            .eq("signal", 1) \
            .execute()
        liked_names = set(r["nom_vetement"] for r in liked_result.data) if liked_result.data else set()

        selection = []
        for cat, quota in quotas.items():
            # Essaie d'abord avec le warmth_target
            items_result = supabase.table("stg_wardrobe") \
                .select("item_id, item_name, category, warmth_level") \
                .eq("user_id", user_id) \
                .eq("category", cat) \
                .execute()
            
            items = [r for r in items_result.data if r["warmth_level"] in warmth_target] if items_result.data else []
            
            # Si pas d'items avec warmth_target, prend tout
            if not items and items_result.data:
                items = items_result.data
            
            if not items:
                continue
            
            # Sort par liked items en priorité
            items_sorted = sorted(items, key=lambda x: x["item_name"] in liked_names, reverse=True)
            
            for item in items_sorted[:quota]:
                selection.append(int(item["item_id"]))
        
        return selection
    except Exception as e:
        print(f"❌ Erreur suggerer_essentiel: {e}")
        return []
    
def fmt_jour(date_str):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return f"{jours_fr[d.weekday()]} {d.day}"
    except Exception:
        return date_str

# ══════════════════════════════════════════════════════════════════════════════
# ÉTAPE 1 — Destination + Dates + Météo
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.voyage_step == 1:
    st.markdown(
        '<p style="font-family:\'Syne\',sans-serif;font-size:1.1rem;font-weight:700;color:#0D1B2A;margin-bottom:1.2rem">Où vas-tu ? 🌍</p>',
        unsafe_allow_html=True
    )

    query = st.text_input(
        "Ville de destination",
        placeholder="Commence à taper : Lausanne, Douala, Tokyo...",
        value=st.session_state.voyage_data.get('query', '')
    )

    chosen_city = None
    if query and len(query) >= 3:
        villes = search_cities(query)
        if villes:
            labels = [v["label"] for v in villes]
            choix = st.selectbox("Choisis ta ville", options=labels, key="city_select")
            chosen_city = next((v for v in villes if v["label"] == choix), None)
            st.session_state.voyage_city_choice = chosen_city
        else:
            st.warning("Aucune ville trouvée — vérifie l'orthographe")
    elif query and len(query) < 3:
        st.caption("Tape au moins 3 lettres...")

    col1, col2 = st.columns(2)
    with col1:
        date_depart = st.date_input(
            "Date de départ",
            value=st.session_state.voyage_data.get('date_depart', datetime.today().date() + timedelta(days=1)),
            min_value=datetime.today().date()
        )
    with col2:
        date_retour = st.date_input(
            "Date de retour",
            value=st.session_state.voyage_data.get('date_retour', datetime.today().date() + timedelta(days=7)),
            min_value=datetime.today().date() + timedelta(days=1)
        )

    nb_jours = (date_retour - date_depart).days
    if nb_jours > 0:
        st.markdown(
            f'<div style="font-size:0.82rem;color:#8A8A8A;margin-bottom:1rem">📅 {nb_jours} jour{"s" if nb_jours > 1 else ""} de voyage</div>',
            unsafe_allow_html=True
        )

    city = st.session_state.voyage_city_choice
    if city:
        if st.button(f"🌤️ Voir la météo · {city['ville']}", use_container_width=True, type="secondary"):
            with st.spinner(f"Météo pour {city['ville']}..."):
                meteo = get_meteo_voyage(city['lat'], city['lon'], date_depart, date_retour)
                if meteo:
                    st.session_state.voyage_meteo = meteo
                    st.session_state.voyage_data['lat'] = city['lat']
                    st.session_state.voyage_data['lon'] = city['lon']
                else:
                    st.error("Météo non disponible pour ces dates")

    if st.session_state.voyage_meteo:
        meteo = st.session_state.voyage_meteo
        emoji = WEATHER_EMOJIS.get(meteo['label'], '🌤️')
        ville_aff = city['ville'] if city else st.session_state.voyage_data.get('destination', '')
        jours = meteo.get('jours', [])

        # En-tête résumé (HTML compact)
        st.markdown(
            '<div style="background:white;border:1px solid rgba(13,27,42,0.08);border-radius:14px;padding:1.2rem;margin:1rem 0 0.8rem 0;text-align:center">'
            f'<div style="font-size:2rem">{emoji}</div>'
            f'<div style="font-size:0.75rem;color:#B8974A;text-transform:uppercase;letter-spacing:0.1em;margin-top:0.5rem">Météo prévue · {ville_aff}</div>'
            f'<div style="font-family:\'Syne\',sans-serif;font-size:2rem;font-weight:800;color:#0D1B2A;margin-top:0.3rem">{meteo["temp_avg"]}°C</div>'
            f'<div style="font-size:0.82rem;color:#8A8A8A">{meteo["label"]} en moyenne</div>'
            f'<div style="font-size:0.78rem;color:#B8974A;margin-top:0.3rem">↑ {meteo["temp_max"]}°C · ↓ {meteo["temp_min"]}°C · {meteo["nb_jours"]} jours</div>'
            '</div>',
            unsafe_allow_html=True
        )

        # Cartes par jour (≤7j) ou tranches (>7j) — HTML COMPACT sans indentation
        if len(jours) <= 7:
            cards = ""
            for j in jours:
                e = WEATHER_EMOJIS.get(j['label'], '🌤️')
                cards += (
                    '<div style="flex:1;min-width:64px;background:white;border:1px solid rgba(13,27,42,0.08);border-radius:12px;padding:0.7rem 0.4rem;text-align:center">'
                    f'<div style="font-size:0.7rem;color:#8A8A8A;font-weight:600">{fmt_jour(j["date"])}</div>'
                    f'<div style="font-size:1.4rem;margin:0.3rem 0">{e}</div>'
                    f'<div style="font-family:\'Syne\',sans-serif;font-size:0.95rem;font-weight:800;color:#0D1B2A">{int(j["max"])}°</div>'
                    f'<div style="font-size:0.7rem;color:#B8974A">{int(j["min"])}°</div>'
                    '</div>'
                )
            st.markdown(
                f'<div style="display:flex;gap:0.5rem;overflow-x:auto;margin-bottom:1rem">{cards}</div>',
                unsafe_allow_html=True
            )
        else:
            n = len(jours)
            tiers = [("Début", jours[:n//3]), ("Milieu", jours[n//3:2*n//3]), ("Fin", jours[2*n//3:])]
            cards = ""
            for nom_tranche, sous in tiers:
                if not sous:
                    continue
                t_max = round(sum(j['max'] for j in sous) / len(sous))
                t_min = round(sum(j['min'] for j in sous) / len(sous))
                sub_labels = [j['label'] for j in sous]
                lab = max(set(sub_labels), key=sub_labels.count)
                e = WEATHER_EMOJIS.get(lab, '🌤️')
                d1, d2 = fmt_jour(sous[0]['date']), fmt_jour(sous[-1]['date'])
                cards += (
                    '<div style="flex:1;background:white;border:1px solid rgba(13,27,42,0.08);border-radius:12px;padding:0.9rem 0.6rem;text-align:center">'
                    f'<div style="font-size:0.7rem;color:#8A8A8A;font-weight:600;text-transform:uppercase">{nom_tranche}</div>'
                    f'<div style="font-size:0.65rem;color:#8A8A8A">{d1} → {d2}</div>'
                    f'<div style="font-size:1.4rem;margin:0.3rem 0">{e}</div>'
                    f'<div style="font-family:\'Syne\',sans-serif;font-size:0.95rem;font-weight:800;color:#0D1B2A">{t_max}° / {t_min}°</div>'
                    f'<div style="font-size:0.68rem;color:#B8974A">{lab}</div>'
                    '</div>'
                )
            st.markdown(
                f'<div style="display:flex;gap:0.5rem;margin-bottom:1rem">{cards}</div>',
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Continuer →", use_container_width=True, type="primary",
                 disabled=not city or date_retour <= date_depart):
        st.session_state.voyage_data.update({
            'query': query, 'destination': city['ville'],
            'date_depart': date_depart, 'date_retour': date_retour, 'nb_jours': nb_jours
        })
        st.session_state.voyage_step = 2
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# ÉTAPE 2 — Sélection vêtements
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.voyage_step == 2:
    dest = st.session_state.voyage_data.get('destination', '')
    nb = st.session_state.voyage_data.get('nb_jours', 0)
    meteo = st.session_state.voyage_meteo

    st.markdown(
        '<p style="font-family:\'Syne\',sans-serif;font-size:1.1rem;font-weight:700;color:#0D1B2A;margin-bottom:0.5rem">'
        f'Qu\'est-ce que tu emmènes à {dest} ? 🧳</p>'
        f'<div style="font-size:0.82rem;color:#8A8A8A;margin-bottom:1rem">{nb} jours — coche les vêtements que tu mets dans ta valise</div>',
        unsafe_allow_html=True
    )

    try:
        wardrobe_result = supabase.table("stg_wardrobe") \
            .select("item_id, item_name, category, color, material") \
            .eq("user_id", USER_ID) \
            .order("category", desc=False) \
            .order("item_name", desc=False) \
            .execute()
        
        wardrobe = pd.DataFrame(wardrobe_result.data) if wardrobe_result.data else pd.DataFrame()
    except Exception as e:
        print(f"❌ Erreur wardrobe: {e}")
        wardrobe = pd.DataFrame()

    if st.button("✨ Suggère-moi l'essentiel", use_container_width=True, type="primary"):
        temp = meteo['temp_avg'] if meteo else 18
        with st.spinner("L'IA prépare ta valise essentielle..."):
            st.session_state.voyage_vetements = suggerer_essentiel(USER_ID, temp, nb)
            st.session_state.voyage_suggested = True
        st.rerun()

    cat_emojis = {"Haut": "👕", "Bas": "👖", "Chaussures": "👟"}

    if st.session_state.voyage_suggested and len(wardrobe) > 0:
        sel_ids = st.session_state.voyage_vetements
        sel_items = wardrobe[wardrobe['item_id'].isin(sel_ids)]
        liste = " · ".join([
            f"{cat_emojis.get(r['category'],'👔')} {r['item_name']}"
            for _, r in sel_items.iterrows()
        ])
        st.markdown(
            '<div style="background:#F0EBF8;border:1px solid #D9C9EC;border-radius:12px;padding:1rem 1.1rem;margin:0.8rem 0;color:#5B3A8C">'
            f'<div style="font-size:0.85rem;font-weight:700;margin-bottom:0.4rem">✨ La sélection de l\'IA ({len(sel_items)} pièces)</div>'
            f'<div style="font-size:0.82rem;line-height:1.5">{liste}</div>'
            '<div style="font-size:0.75rem;color:#8A6BB0;margin-top:0.6rem">Selon la météo, la durée et tes goûts — ajoute ou retire librement ci-dessous</div>'
            '</div>',
            unsafe_allow_html=True
        )

    if len(wardrobe) == 0:
        st.warning("Ta garde-robe est vide — ajoute des vêtements d'abord !")
    else:
        for cat in ["Haut", "Bas", "Chaussures"]:
            cat_items = wardrobe[wardrobe['category'] == cat]
            if len(cat_items) == 0:
                continue
            st.markdown(
                f'<div style="font-size:0.78rem;color:#B8974A;text-transform:uppercase;letter-spacing:0.1em;margin:1rem 0 0.5rem 0">{cat_emojis.get(cat, "👔")} {cat}s</div>',
                unsafe_allow_html=True
            )
            for _, row in cat_items.iterrows():
                item_id = int(row['item_id'])
                is_checked = item_id in st.session_state.voyage_vetements
                checked = st.checkbox(
                    f"{row['item_name']} — {row['color']} · {row['material']}",
                    value=is_checked, key=f"voy_{item_id}"
                )
                if checked and item_id not in st.session_state.voyage_vetements:
                    st.session_state.voyage_vetements.append(item_id)
                elif not checked and item_id in st.session_state.voyage_vetements:
                    st.session_state.voyage_vetements.remove(item_id)

        nb_sel = len(st.session_state.voyage_vetements)
        if nb_sel > 0:
            st.markdown(
                f'<div style="padding:0.8rem 1rem;background:#F7F5F0;border-radius:10px;font-size:0.82rem;color:#0D1B2A;margin-top:1rem"><b>✅ {nb_sel} vêtement(s) sélectionné(s)</b></div>',
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Retour", use_container_width=True, type="secondary"):
            st.session_state.voyage_step = 1
            st.rerun()
    with col2:
        if st.button("Continuer →", use_container_width=True, type="primary",
                     disabled=len(st.session_state.voyage_vetements) == 0):
            st.session_state.voyage_step = 3
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# ÉTAPE 3 — Confirmation
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.voyage_step == 3:
    data = st.session_state.voyage_data
    meteo = st.session_state.voyage_meteo
    emoji_meteo = WEATHER_EMOJIS.get(meteo['label'] if meteo else '', '🌤️')

    st.markdown(
        '<div style="text-align:center;padding:1rem 0">'
        '<div style="font-size:3rem">🧳</div>'
        f'<div style="font-family:\'Syne\',sans-serif;font-size:1.4rem;font-weight:800;color:#0D1B2A;margin-top:0.5rem">{data.get("destination", "")}</div>'
        f'<div style="font-size:0.85rem;color:#8A8A8A;margin-top:0.3rem">{data.get("date_depart").strftime("%d/%m/%Y")} → {data.get("date_retour").strftime("%d/%m/%Y")} · {data.get("nb_jours")} jours</div>'
        '</div>',
        unsafe_allow_html=True
    )

    if meteo:
        st.markdown(
            '<div style="background:white;border:1px solid rgba(13,27,42,0.08);border-radius:14px;padding:1rem;margin:1rem 0;display:flex;align-items:center;justify-content:space-between">'
            f'<div style="font-size:1.5rem">{emoji_meteo}</div>'
            '<div style="text-align:center">'
            f'<div style="font-family:\'Syne\',sans-serif;font-size:1.3rem;font-weight:800;color:#0D1B2A">{meteo["temp_avg"]}°C</div>'
            f'<div style="font-size:0.78rem;color:#8A8A8A">{meteo["label"]}</div>'
            '</div>'
            f'<div style="font-size:0.78rem;color:#B8974A">↑{meteo["temp_max"]}° · ↓{meteo["temp_min"]}°</div>'
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown(f"**👕 {len(st.session_state.voyage_vetements)} vêtements dans la valise**")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Modifier", use_container_width=True, type="secondary"):
            st.session_state.voyage_step = 2
            st.rerun()
    with col2:
        if st.button("✓ Enregistrer mon voyage", use_container_width=True, type="primary"):
            voyage = {
                "user_id": USER_ID, "destination": data['destination'],
                "ville": data['destination'],
                "date_depart": data['date_depart'].strftime("%Y-%m-%d"),
                "date_retour": data['date_retour'].strftime("%Y-%m-%d"),
                "vetements_ids": st.session_state.voyage_vetements
            }
            supabase.table("voyages").insert(voyage).execute()
            st.success(f"✅ Voyage à {data['destination']} enregistré !")
            st.balloons()
            st.session_state.voyage_step = 1
            st.session_state.voyage_data = {}
            st.session_state.voyage_meteo = None
            st.session_state.voyage_vetements = []
            st.session_state.voyage_suggested = False
            st.session_state.voyage_city_choice = None
            time.sleep(2)
            st.switch_page("pages/1_Recommandation.py")

# ── Navigation ────────────────────────────────────────────────────────────────
st.markdown('<div class="sw-divider"></div>', unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns(5)
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
with col5:
    if st.button("🧳\nVoyage", use_container_width=True, type="primary"):
        st.switch_page("pages/6_Voyage.py")