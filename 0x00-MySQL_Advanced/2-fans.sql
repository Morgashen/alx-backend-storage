-- Script to rank country origins of bands by number of fans
-- This query assumes the metal_bands table has been imported

SELECT 
    origin AS origin,
    SUM(fans) AS nb_fans
FROM 
    metal_bands
GROUP BY 
    origin
ORDER BY 
    nb_fans DESC;
