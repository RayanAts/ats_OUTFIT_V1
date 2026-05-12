WITH source AS (

    SELECT *
    FROM smartwardrobe_lakehouse.dbo.bronze_weather

),

enriched AS (

    SELECT
        fetch_date,
        latitude,
        longitude,
        temp_max,
        temp_min,
        CAST((temp_max + temp_min) / 2.0 AS DECIMAL(5,2))  AS temp_avg,
        precipitation_mm,
        windspeed_max_kmh,
        weathercode
    FROM source

),

cleaned AS (

    SELECT
        fetch_date,
        latitude,
        longitude,
        temp_max,
        temp_min,
        temp_avg,
        precipitation_mm,
        windspeed_max_kmh,
        weathercode,
        CASE
            WHEN weathercode = 0                THEN 'Ciel dégagé'
            WHEN weathercode BETWEEN 1 AND 3    THEN 'Nuageux'
            WHEN weathercode BETWEEN 45 AND 48  THEN 'Brouillard'
            WHEN weathercode BETWEEN 51 AND 67  THEN 'Pluie'
            WHEN weathercode BETWEEN 71 AND 77  THEN 'Neige'
            WHEN weathercode BETWEEN 80 AND 82  THEN 'Averses'
            WHEN weathercode BETWEEN 95 AND 99  THEN 'Orage'
            ELSE 'Inconnu'
        END                                     AS weather_label,
        CASE
            WHEN temp_avg >= 20                 THEN 1
            WHEN temp_avg BETWEEN 12 AND 19     THEN 2
            WHEN temp_avg BETWEEN 5 AND 11      THEN 3
            WHEN temp_avg < 5                   THEN 4
            ELSE 2
        END                                     AS recommended_warmth,
        CAST(SYSDATETIME() AS datetime2(6))     AS dbt_loaded_at
    FROM enriched

)

SELECT * FROM cleaned