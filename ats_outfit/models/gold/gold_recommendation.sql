-- ============================================
-- GOLD - Recommendation Engine
-- 1 Haut + 1 Bas + 1 Chaussure
-- Scoring : météo + formalité + couleur + matière + préférences user
-- ============================================

WITH wardrobe AS (
    SELECT *
    FROM {{ ref('dim_wardrobe_scd2') }}
    WHERE is_current = 1
    AND is_active = true
),

weather AS (
    SELECT *
    FROM {{ ref('stg_weather') }}
    ORDER BY fetch_date DESC
    LIMIT 1
),

calendar AS (
    SELECT *
    FROM {{ ref('stg_calendar') }}
    WHERE event_date >= CURRENT_DATE
    ORDER BY event_date ASC
),

recent_recs AS (
    SELECT DISTINCT nom_vetement
    FROM public.historique_recommandations
    WHERE date_recommandation >= CURRENT_DATE - INTERVAL '3 days'
),

-- ── Apprentissage par utilisateur ─────────────────────────────────────────────
-- Vêtements aimés (signal = +1)
liked AS (
    SELECT
        user_id,
        nom_vetement,
        COUNT(*) AS nb_likes
    FROM public.retours
    WHERE signal = 1
    GROUP BY user_id, nom_vetement
),

-- Vêtements refusés (signal = -1)
disliked AS (
    SELECT
        user_id,
        nom_vetement,
        COUNT(*) AS nb_dislikes
    FROM public.retours
    WHERE signal = -1
    GROUP BY user_id, nom_vetement
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
        w.user_id,
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
            WHEN wt.temp_avg >= 20 AND w.color IN ('Blanc', 'Beige', 'Gris', 'Camel', 'Crème') THEN 1.0
            WHEN wt.temp_avg >= 20 AND w.color IN ('Bleu', 'Bleu ciel', 'Vert', 'Kaki')        THEN 0.7
            WHEN wt.temp_avg >= 20 AND w.color IN ('Marine', 'Bordeaux', 'Rose', 'Violet')     THEN 0.5
            WHEN wt.temp_avg >= 20 AND w.color = 'Noir'                                         THEN 0.3
            WHEN wt.temp_avg < 12 AND w.color IN ('Noir', 'Marine', 'Bordeaux', 'Violet')      THEN 1.0
            WHEN wt.temp_avg < 12 AND w.color IN ('Gris', 'Marron', 'Kaki', 'Taupe')           THEN 0.8
            WHEN wt.temp_avg < 12 AND w.color IN ('Blanc', 'Beige', 'Camel', 'Crème')          THEN 0.6
            ELSE 0.7
        END AS color_score,

        -- Score matière selon température
        CASE
            WHEN wt.temp_avg >= 20 AND w.material IN ('Coton', 'Lin')                 THEN 1.0
            WHEN wt.temp_avg >= 20 AND w.material IN ('Polyester', 'Nylon')           THEN 0.7
            WHEN wt.temp_avg >= 20 AND w.material IN ('Denim', 'Cuir')                THEN 0.5
            WHEN wt.temp_avg >= 20 AND w.material IN ('Laine', 'Cachemire')           THEN 0.2
            WHEN wt.temp_avg < 12 AND w.material IN ('Laine', 'Cachemire')            THEN 1.0
            WHEN wt.temp_avg < 12 AND w.material IN ('Polyester', 'Nylon')            THEN 0.8
            WHEN wt.temp_avg < 12 AND w.material IN ('Coton', 'Denim')                THEN 0.6
            WHEN wt.temp_avg < 12 AND w.material IN ('Lin')                           THEN 0.3
            ELSE 0.7
        END AS material_score,

        -- ── Score préférence utilisateur ──────────────────────────────────────
        -- Bonus si l'utilisateur a déjà aimé ce vêtement
        CASE
            WHEN l.nb_likes >= 3 THEN 0.30   -- Très aimé → gros bonus
            WHEN l.nb_likes = 2  THEN 0.20   -- Bien aimé → bonus moyen
            WHEN l.nb_likes = 1  THEN 0.10   -- Aimé une fois → petit bonus
            ELSE 0.0
        END AS preference_bonus,

        -- Pénalité si l'utilisateur a refusé ce vêtement
        CASE
            WHEN d.nb_dislikes >= 3 THEN 0.50  -- Très refusé → gros malus
            WHEN d.nb_dislikes = 2  THEN 0.35  -- Refusé 2 fois → malus moyen
            WHEN d.nb_dislikes = 1  THEN 0.20  -- Refusé une fois → petit malus
            ELSE 0.0
        END AS preference_penalty,

        -- Pénalité récence (déjà recommandé dans les 3 derniers jours)
        CASE WHEN r.nom_vetement IS NOT NULL THEN 0.3 ELSE 0.0 END AS recency_penalty

    FROM wardrobe w
    CROSS JOIN weather wt
    JOIN calendar cal ON cal.user_id = w.user_id
        AND cal.event_date = (
            SELECT MIN(event_date)
            FROM {{ ref('stg_calendar') }}
            WHERE user_id = w.user_id
            AND event_date >= CURRENT_DATE
        )
    LEFT JOIN recent_recs r      ON w.item_name = r.nom_vetement
    LEFT JOIN liked l            ON w.item_name = l.nom_vetement AND w.user_id = l.user_id
    LEFT JOIN disliked d         ON w.item_name = d.nom_vetement AND w.user_id = d.user_id
),

scored AS (
    SELECT
        *,
        ROUND(CAST(
            (warmth_match_score    * 0.25) +
            (formality_match_score * 0.25) +
            (color_score           * 0.15) +
            (material_score        * 0.15) +
            preference_bonus             -
            preference_penalty           -
            recency_penalty
        AS NUMERIC), 4) AS score_final
    FROM scoring
),

best_haut AS (
    SELECT *, 1 AS rank_today
    FROM (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY score_final DESC) AS rn
        FROM scored WHERE category = 'Haut'
    ) t WHERE rn <= 6
),

best_bas AS (
    SELECT *, 2 AS rank_today
    FROM (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY score_final DESC) AS rn
        FROM scored WHERE category = 'Bas'
    ) t WHERE rn <= 6
),

best_shoes AS (
    SELECT *, 3 AS rank_today
    FROM (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY score_final DESC) AS rn
        FROM scored WHERE category = 'Chaussures'
    ) t WHERE rn <= 6
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
    user_id,
    fetch_date              AS recommendation_date,
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
    preference_bonus,
    preference_penalty,
    recency_penalty,
    score_final,
    rank_today,
    NOW()                   AS dbt_loaded_at
FROM final