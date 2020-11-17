SELECT
sirius_id as target_id, *
FROM {schema}.persons
WHERE sirius_id IS NOT NULL
ORDER BY sirius_id DESC
