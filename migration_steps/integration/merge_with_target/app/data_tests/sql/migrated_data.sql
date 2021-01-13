select
    persons.caserecnumber,
    count(*) over (partition by persons.caserecnumber)  as person_count,
    (select count(*) from schema.addresses where addresses.person_id = persons.id) as address_count,
    (select count(*) from schema.person_caseitem where cast(person_caseitem.person_id as int) = persons.id) as case_count
from schema.persons persons
where persons.caserecnumber in (test_case_list)
