-- ============================================
-- GOLD - Recommendation Engine
-- 1 Haut + 1 Bas + 1 Chaussure
-- Avec rotation pour éviter les répétitions
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

-- Vêtements recommandés ces 3 derniers jours
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
        CASE
            WHEN ABS(w.warmth_level - wt.recommended_warmth) = 0 THEN 1.0
            WHEN ABS(w.warmth_level - wt.recommended_warmth) = 1 THEN 0.7
            WHEN ABS(w.warmth_level - wt.recommended_warmth) = 2 THEN 0.4
            ELSE 0.1
        END AS warmth_match_score,
        CASE
            WHEN ABS(w.formality_level - cal.formality_required) = 0 THEN 1.0
            WHEN ABS(w.formality_level - cal.formality_required) = 1 THEN 0.7
            WHEN ABS(w.formality_level - cal.formality_required) = 2 THEN 0.4
            ELSE 0.1
        END AS formality_match_score,
        0.5 AS preference_score,
        -- Pénalité si recommandé récemment
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
            (warmth_match_score * 0.40) +
            (formality_match_score * 0.40) +
            (preference_score * 0.20) -
            recency_penalty
        AS DECIMAL(5,4)) AS score_final
    FROM scoring
),

best_haut AS (
    SELECT TOP 1 *, 1 AS rank_today
    FROM scored
    WHERE category = 'Haut'
    ORDER BY score_final DESC
),

best_bas AS (
    SELECT TOP 1 *, 2 AS rank_today
    FROM scored
    WHERE category = 'Bas'
    ORDER BY score_final DESC
),

best_shoes AS (
    SELECT TOP 1 *, 3 AS rank_today
    FROM scored
    WHERE category = 'Chaussures'
    ORDER BY score_final DESC
),

final AS (
    SELECT * FROM best_haut
    UNION ALL
    SELECT * FROM best_bas
    UNION ALL
    SELECT * FROM best_shoes
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
    fetch_date AS recommendation_date,
    temp_avg,
    weather_label,
    recommended_warmth,
    context_type,
    context_label,
    formality_required,
    outdoor_exposure,
    warmth_match_score,
    formality_match_score,
    preference_score,
    recency_penalty,
    score_final,
    rank_today,
    CAST(SYSDATETIME() AS datetime2(6)) AS dbt_loaded_at
FROM final