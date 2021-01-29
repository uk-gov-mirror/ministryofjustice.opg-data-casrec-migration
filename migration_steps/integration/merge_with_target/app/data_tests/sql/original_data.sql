select
    pat."Case" as caserecnumber,
    count(pat."Forename") over (partition by pat."Case") as person_count,
    count(pat."Adrs1") over (partition by pat."Case")  as address_count,
   (select count(*) from schema.order orders where orders."Case" = pat."Case") as case_count,
   (select count(*) from schema.order orders where orders."Case" = pat."Case") as supervision_level_log_count
from schema.pat pat
where pat."Case" in (test_case_list);
