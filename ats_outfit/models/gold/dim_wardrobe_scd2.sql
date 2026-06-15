-- ============================================
-- GOLD - Dimension Wardrobe SCD Type 2
-- Historise chaque changement de vêtement
-- ============================================

WITH current_data AS (
    SELECT
        item_id,
        item_name,
        category,
        subcategory,
        color,
        material,
        warmth_level,
        formality_level,
        season,
        condition,
        is_active,
        created_at,
        user_id,
        NOW() AS dbt_loaded_at
    FROM {{ ref('stg_wardrobe') }}
),

scd2 AS (
    SELECT
        item_id,
        item_name,
        category,
        subcategory,
        color,
        material,
        warmth_level,
        formality_level,
        season,
        condition,
        is_active,
        created_at,
        user_id,
        dbt_loaded_at                       AS valid_from,
        CAST('9999-12-31' AS DATE)          AS valid_to,
        1                                   AS is_current,
        MD5(CONCAT(
            CAST(item_id AS VARCHAR),
            item_name,
            CAST(warmth_level AS VARCHAR),
            CAST(formality_level AS VARCHAR),
            condition
        ))                                  AS row_hash
    FROM current_data
)

SELECT * FROM scd2