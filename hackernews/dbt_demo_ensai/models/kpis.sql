SELECT
    partition_date,
    SUM(points) AS total_points,
    SUM(comments) AS total_comments,
FROM {{ source("christophe", "hackernews") }}
GROUP BY ALL