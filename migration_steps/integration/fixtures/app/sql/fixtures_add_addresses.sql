INSERT INTO addresses (person_id, address_lines, isairmailrequired) (
    SELECT id as person_id, '["m","o","o"]' as address_lines, CAST(0 AS BOOLEAN) as isairmailrequired
    FROM persons
    WHERE clientsource = 'SKELETON'
    ORDER BY id DESC
);
