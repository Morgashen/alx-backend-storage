-- Script to list Glam rock bands ranked by their longevity
-- This query assumes the metal_bands table has been imported

SELECT
    band_name,
    CASE
        WHEN split IS NULL THEN (2022 - formed)
        ELSE (split - formed)
    END AS lifespan
FROM
    metal_bands
WHERE
    style LIKE '%Glam rock%'
ORDER BY
    lifespan DESC;
