SELECT sirius_id as target_id, *
FROM {schema}.addresses
WHERE sirius_id IS NOT NULL
