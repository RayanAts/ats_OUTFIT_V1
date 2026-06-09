WITH source AS (
    SELECT * FROM public.meteo
    ORDER BY fetch_date DESC
    LIMIT 1
),

cleaned AS (
    SELECT
        fetch_date,
        fetch_time,
        ville           AS city,
        temp_actuelle   AS temp_current,
        temp_max,
        temp_min,
        temp_moyenne    AS temp_avg,
        precipitation_mm,
        vitesse_vent_max AS windspeed_max_kmh,
        weathercode,
        label_meteo     AS weather_label,
        chaleur_recommandee AS recommended_warmth,
        NOW()           AS dbt_loaded_at
    FROM source
)

SELECT * FROM cleaned