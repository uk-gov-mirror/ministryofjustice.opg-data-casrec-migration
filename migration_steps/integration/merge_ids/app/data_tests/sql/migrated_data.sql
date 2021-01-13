select
    persons.caserecnumber,
    count(persons.firstname) over (partition by persons.caserecnumber)  as person_count,
    count(addresses.id) over (partition by addresses.person_id) as address_count
from schema.persons persons
left outer join schema.addresses addresses on addresses.person_id = persons.id
where persons.caserecnumber in (test_case_list)
