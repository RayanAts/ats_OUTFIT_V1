-- ============================================
-- GOLD - Recommendation Engine
-- Croise vêtements + météo + calendrier
-- Score chaque vêtement pour aujourd'hui
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
    WHERE event_date = CAST(GETDATE() AS DATE)

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

        -- Contexte du jour
        wt.fetch_date,
        wt.temp_avg,
        wt.weather_label,
        wt.recommended_warmth,
        cal.context_type,
        cal.context_label,
        cal.formality_required,
        cal.outdoor_exposure,

        -- Score chaleur (0 ou 1)
        CASE
            WHEN ABS(w.warmth_level - wt.recommended_warmth) = 0 THEN 1.0
            WHEN ABS(w.warmth_level - wt.recommended_warmth) = 1 THEN 0.7
            WHEN ABS(w.warmth_level - wt.recommended_warmth) = 2 THEN 0.4
            ELSE 0.1
        END                                         AS warmth_match_score,

        -- Score formalité (0 ou 1)
        CASE
            WHEN ABS(w.formality_level - cal.formality_required) = 0 THEN 1.0
            WHEN ABS(w.formality_level - cal.formality_required) = 1 THEN 0.7
            WHEN ABS(w.formality_level - cal.formality_required) = 2 THEN 0.4
            ELSE 0.1
        END                                         AS formality_match_score,

        -- Score feedback historique (0.5 par défaut = neutre)
        0.5                                         AS preference_score

    FROM wardrobe w
    CROSS JOIN weather wt
    CROSS JOIN calendar cal

),

final AS (

    SELECT
        item_id,
        item_name,
        category,
        subcategory,
        color,
        material,
        warmth_level,
        formality_level,
        fetch_date                                  AS recommendation_date,
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

        -- Score final pondéré
        CAST(
            (warmth_match_score * 0.40) +
            (formality_match_score * 0.40) +
            (preference_score * 0.20)
        AS DECIMAL(5,4))                            AS score_final,

        CAST(SYSDATETIME() AS datetime2(6))         AS dbt_loaded_at

    FROM scoring

)

SELECT
    *,
    RANK() OVER (ORDER BY score_final DESC)         AS rank_today
FROM final