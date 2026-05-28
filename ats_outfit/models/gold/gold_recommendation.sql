-- ============================================
-- GOLD - Recommendation Engine
-- 1 Haut + 1 Bas + 1 Chaussure
-- Scoring : météo + formalité + couleur + matière
-- ============================================

WITH wardrobe AS (
    SELECT *
    FROM {{ ref('dim_wardrobe_scd2') }}
    WHERE is_current = 1
    AND is_active = 1
),

weather AS (
    SELECT TOP 1 *
    FROM {{ ref('stg_weather') }}
    ORDER BY fetch_date DESC
),

calendar AS (
    SELECT TOP 1 *
    FROM {{ ref('stg_calendar') }}
    WHERE event_date >= CAST(GETDATE() AS DATE)
    ORDER BY event_date ASC
),

recent_recs AS (
    SELECT DISTINCT item_id
    FROM smartwardrobe_lakehouse.dbo.recommendation_history
    WHERE recommendation_date >= CAST(DATEADD(day, -3, GETDATE()) AS DATE)
),

scoring AS (
    SELECT
        w.item_id,
        w.item_name,
        w.category,
        w.subcategory,
        w.color,
        w.material,
        w.warmth_level,
        w.formality_level,
        w.season,
        w.condition,
        wt.fetch_date,
        wt.temp_avg,
        wt.weather_label,
        wt.recommended_warmth,
        cal.context_type,
        cal.context_label,
        cal.formality_required,
        cal.outdoor_exposure,

        -- Score chaleur
        CASE
            WHEN ABS(w.warmth_level - wt.recommended_warmth) = 0 THEN 1.0
            WHEN ABS(w.warmth_level - wt.recommended_warmth) = 1 THEN 0.7
            WHEN ABS(w.warmth_level - wt.recommended_warmth) = 2 THEN 0.4
            ELSE 0.1
        END AS warmth_match_score,

        -- Score formalité
        CASE
            WHEN ABS(w.formality_level - cal.formality_required) = 0 THEN 1.0
            WHEN ABS(w.formality_level - cal.formality_required) = 1 THEN 0.7
            WHEN ABS(w.formality_level - cal.formality_required) = 2 THEN 0.4
            ELSE 0.1
        END AS formality_match_score,

        -- Score couleur selon température
        CASE
            -- Temps chaud (>20°C) → couleurs claires favorisées
            WHEN wt.temp_avg >= 20 AND w.color IN ('Blanc', 'Beige', 'Gris', 'Camel') THEN 1.0
            WHEN wt.temp_avg >= 20 AND w.color IN ('Bleu', 'Vert', 'Kaki')            THEN 0.7
            WHEN wt.temp_avg >= 20 AND w.color IN ('Marine', 'Bordeaux', 'Rouge')     THEN 0.5
            WHEN wt.temp_avg >= 20 AND w.color = 'Noir'                               THEN 0.3
            -- Temps froid (<12°C) → couleurs foncées OK
            WHEN wt.temp_avg < 12 AND w.color IN ('Noir', 'Marine', 'Bordeaux')       THEN 1.0
            WHEN wt.temp_avg < 12 AND w.color IN ('Gris', 'Marron', 'Kaki')           THEN 0.8
            WHEN wt.temp_avg < 12 AND w.color IN ('Blanc', 'Beige', 'Camel')          THEN 0.6
            -- Temps intermédiaire → neutre
            ELSE 0.7
        END AS color_score,

        -- Score matière selon température
        CASE
            -- Temps chaud → matières légères
            WHEN wt.temp_avg >= 20 AND w.material IN ('Coton', 'Lin')                 THEN 1.0
            WHEN wt.temp_avg >= 20 AND w.material IN ('Polyester', 'Nylon')           THEN 0.7
            WHEN wt.temp_avg >= 20 AND w.material IN ('Denim', 'Cuir')                THEN 0.5
            WHEN wt.temp_avg >= 20 AND w.material IN ('Laine', 'Cachemire')           THEN 0.2
            -- Temps froid → matières chaudes
            WHEN wt.temp_avg < 12 AND w.material IN ('Laine', 'Cachemire')            THEN 1.0
            WHEN wt.temp_avg < 12 AND w.material IN ('Polyester', 'Nylon')            THEN 0.8
            WHEN wt.temp_avg < 12 AND w.material IN ('Coton', 'Denim')                THEN 0.6
            WHEN wt.temp_avg < 12 AND w.material IN ('Lin')                           THEN 0.3
            -- Temps intermédiaire → neutre
            ELSE 0.7
        END AS material_score,

        -- Préférence historique
        0.5 AS preference_score,

        -- Pénalité récence
        CASE WHEN r.item_id IS NOT NULL THEN 0.3 ELSE 0.0 END AS recency_penalty

    FROM wardrobe w
    CROSS JOIN weather wt
    CROSS JOIN calendar cal
    LEFT JOIN recent_recs r ON w.item_id = r.item_id
),

scored AS (
    SELECT
        *,
        CAST(
            (warmth_match_score  * 0.30) +
            (formality_match_score * 0.30) +
            (color_score         * 0.20) +
            (material_score      * 0.20) -
            recency_penalty
        AS DECIMAL(5,4)) AS score_final
    FROM scoring
),

best_haut AS (
    SELECT TOP 1 *, 1 AS rank_today
    FROM scored WHERE category = 'Haut'
    ORDER BY score_final DESC
),

best_bas AS (
    SELECT TOP 1 *, 2 AS rank_today
    FROM scored WHERE category = 'Bas'
    ORDER BY score_final DESC
),

best_shoes AS (
    SELECT TOP 1 *, 3 AS rank_today
    FROM scored WHERE category = 'Chaussures'
    ORDER BY score_final DESC
),

final AS (
    SELECT * FROM best_haut
    UNION ALL SELECT * FROM best_bas
    UNION ALL SELECT * FROM best_shoes
)

SELECT
    item_id,
    item_name,
    category,
    subcategory,
    color,
    material,
    warmth_level,
    formality_level,
    fetch_date          AS recommendation_date,
    temp_avg,
    weather_label,
    recommended_warmth,
    context_type,
    context_label,
    formality_required,
    outdoor_exposure,
    warmth_match_score,
    formality_match_score,
    color_score,
    material_score,
    preference_score,
    recency_penalty,
    score_final,
    rank_today,
    CAST(SYSDATETIME() AS datetime2(6)) AS dbt_loaded_at
FROM final