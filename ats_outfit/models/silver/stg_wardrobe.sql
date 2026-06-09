WITH source AS (
    SELECT * FROM public.vetements
),

cleaned AS (
    SELECT
        id              AS item_id,
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
        created_at
    FROM source
    WHERE is_active = true
    AND item_name IS NOT NULL
)

SELECT * FROM cleaned