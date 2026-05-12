-- ============================================
-- SILVER - Staging Calendar
-- Source : Table Delta bronze_calendar
-- ============================================

WITH source AS (

    SELECT *
    FROM smartwardrobe_lakehouse.dbo.bronze_calendar

),

cleaned AS (

    SELECT
        CAST(event_date AS DATE)                AS event_date,
        TRIM(context_type)                      AS context_type,
        formality_required,
        CASE
            WHEN outdoor_exposure = 1 THEN 1
            ELSE 0
        END                                     AS outdoor_exposure,
        CASE
            WHEN context_type = 'réunion_client' THEN 'Formel'
            WHEN context_type = 'bureau'         THEN 'Semi-formel'
            WHEN context_type = 'soirée'         THEN 'Élégant'
            WHEN context_type = 'casual'         THEN 'Casual'
            WHEN context_type = 'sport'          THEN 'Sport'
            ELSE 'Casual'
        END                                     AS context_label,
        CAST(SYSDATETIME() AS datetime2(6))     AS dbt_loaded_at
    FROM source

)

SELECT * FROM cleaned