-- ============================================
-- SILVER - Staging Calendar

-- ============================================
WITH source AS (
    SELECT * FROM public.calendrier
    WHERE date_evenement >= CURRENT_DATE
    ORDER BY date_evenement ASC
),

cleaned AS (
    SELECT
        date_evenement      AS event_date,
        type_contexte       AS context_type,
        label_contexte      AS context_label,
        formalite_requise   AS formality_required,
        exposition_exterieure AS outdoor_exposure,
        NOW()               AS dbt_loaded_at
    FROM source
)

SELECT * FROM cleaned