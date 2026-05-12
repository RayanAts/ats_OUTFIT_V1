WITH source AS (

    SELECT *
    FROM smartwardrobe_lakehouse.dbo.bronze_wardrobe

),

cleaned AS (

    SELECT
        item_id,
        TRIM(item_name)                         AS item_name,
        TRIM(category)                          AS category,
        TRIM(subcategory)                       AS subcategory,
        TRIM(color)                             AS color,
        TRIM(material)                          AS material,
        warmth_level,
        formality_level,
        TRIM(season)                            AS season,
        TRIM(condition)                         AS condition,
        CASE 
            WHEN is_active = 1 THEN 1
            ELSE 0 
        END                                     AS is_active,
        created_at,
        CAST(SYSDATETIME() AS datetime2(6))     AS dbt_loaded_at
    FROM source
    WHERE item_id IS NOT NULL

)

SELECT * FROM cleaned