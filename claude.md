# Contexte du projet ATS — SmartWardrobe

## Architecture des fichiers
- app/ → Application Streamlit
  - pages/1_Recommandation.py → Page principale recommandation
  - pages/2_Garde_robe.py → Affichage garde-robe
  - pages/3_Historique.py → Historique et stats
  - pages/5_Ajouter.py → Formulaire ajout vêtement
  - connector.py → Connexion Supabase (NE PAS MODIFIER)
  - recommender.py → Requêtes données (NE PAS MODIFIER)
  - feedback.py → Sauvegarde feedbacks (NE PAS MODIFIER)
  - onelake.py → Upload Supabase (NE PAS MODIFIER)
  - styles.py → CSS global design system
  - main.py → Page de connexion
- ats_outfit/ → Projet dbt (NE PAS MODIFIER)
- nightly_pipeline.py → Pipeline automatique (NE PAS MODIFIER)

## Stack technique
- Base de données : Supabase (PostgreSQL)
- Transformations : dbt Core (PostgreSQL)
- Frontend : Streamlit
- Pipeline nightly : nightly_pipeline.py
- Hébergement : Streamlit Cloud (à venir)

## Design system
- Couleur principale : Navy #0D1B2A
- Couleur accent : Gold #B8974A1
- Fond : #F7F5F0
- Typo titres : Syne
- Typo corps : DM Sans

## Règles ABSOLUES
- Travailler UNIQUEMENT sur les fichiers explicitement mentionnés
- NE JAMAIS modifier connector.py, recommender.py, feedback.py, onelake.py
- NE JAMAIS modifier les fichiers dans ats_outfit/
- NE JAMAIS modifier nightly_pipeline.py
- NE JAMAIS installer de nouvelles librairies sans demander
- Toujours montrer les changements AVANT de les appliquer
- Faire des modifications MINIMALES — ne changer que ce qui est demandé
- Attendre confirmation avant chaque modification