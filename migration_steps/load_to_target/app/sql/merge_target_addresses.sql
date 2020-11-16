UPDATE {schema}.persons persons
SET sirius_id = map.sirius_persons_id
FROM {schema}.sirius_map_clients map
WHERE map.caserecnumber = persons.caserecnumber;

UPDATE {schema}.addresses
SET sirius_person_id = persons.sirius_id
FROM {schema}.persons persons WHERE persons.id = CAST(addresses.person_id AS INTEGER)
