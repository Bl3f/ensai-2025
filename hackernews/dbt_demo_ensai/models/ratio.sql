SELECT
    partition_date,
    total_points / total_comments AS ratio
FROM {{ ref("kpis") }}
GROUP BY ALL