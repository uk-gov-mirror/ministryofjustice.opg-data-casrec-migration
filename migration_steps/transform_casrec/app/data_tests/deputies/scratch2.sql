with tr as (
select
       cases.caserecnumber,
       count(od.id) over (partition by cases.caserecnumber) as order_deputy_count,
       count(persons.id) over (partition by cases.caserecnumber) as persons_count,
       count(addresses.id) over (partition by cases.caserecnumber) as addresses_count,
       persons.firstname, persons.surname,
       addresses.postcode

from transform.cases
left outer join transform.order_deputy od on cases.id = od.order_id
left outer join transform.persons on od.deputy_id = persons.id and persons.type = 'actor_deputy'
left outer join transform.addresses on persons.id = addresses.person_id
order by cases.caserecnumber, firstname, surname, postcode
    ),

orig as (
    select "order"."Case" as caserecnumber,
    count(deputyship.*) over (partition by "order"."Case") as order_deputy_count,
    count(deputy.*) over (partition by "order"."Case") as persons_count,
    count(deputy_address.*) over (partition by "order"."Case") as addresses_count,
       "Dep Forename" as firstname, "Dep Surname" as surname,
        "Dep Postcode" as postcode
    from casrec_csv.order
             left outer join casrec_csv.deputyship on "order"."CoP Case" = deputyship."CoP Case"
             left outer join casrec_csv.deputy on deputyship."Deputy No" = deputy."Deputy No"
             left outer join casrec_csv.deputy_address on deputyship."Dep Addr No" = deputy_address."Dep Addr No"
    order by "order"."Case", "Dep Forename", "Dep Surname", "Dep Postcode"
),

     joined as (
         select
                tr.caserecnumber as transformed_casrecnumber,
                tr.firstname as transformed_firstname,
                tr.surname as transformed_surname,
                tr.postcode as transformed_postcode,
                orig.caserecnumber as original_casrecnumber,
                orig.firstname as original_firstname,
                orig.surname as original_surname,
                orig.postcode as original_postcode
         from tr
                  inner join orig on tr.caserecnumber = orig.caserecnumber
         order by tr.caserecnumber
     )

select * from joined;
                where transformed_casrecnumber = original_casrecnumber
--                 and transformed_firstname != original_firstname
--                 and transformed_surname != original_surname
                and transformed_postcode != original_postcode and transformed_postcode is not null and original_postcode is not null
--                 and transformed_firstname = original_firstname
--                 and transformed_surname = original_surname
--                 and transformed_postcode = original_postcode
;



select * from casrec_csv."order" where "Case" = '99328514';
select * from casrec_csv.deputyship where "CoP Case" in ('9932851401','9932851402');
select * from casrec_csv.deputyship where "Dep Addr No" in ('418');
select * from casrec_csv.deputy where "Deputy No" in ('4192');
select * from casrec_csv.deputy where "Deputy No" in ('4192', '51790');
select * from casrec_csv.deplink where "Deputy No" in ('4192') and "Dep Addr No" in ('418') and "In Use" = 'Y';
select * from casrec_csv.deputy_address where "Dep Addr No" in ('418', '4009', '74340', '119924');


select * from transform.cases where caserecnumber = '99328514';
select * from transform.order_deputy where order_id in  (1831, 1832);
select * from transform.persons where id in (1372);
select * from transform.addresses where person_id in (1372);


select
    persons.firstname, persons.surname,
       addresses.postcode
from transform.persons
left outer join transform.addresses on persons.id = addresses.person_id
where persons.casrec_mapping_file_name = 'deputy_persons_mapping'
and persons.surname = 'Bates'
order by firstname, surname, postcode;


select distinct
    "Dep Forename" as firstname,
       "Dep Surname" as surname,
       "Dep Postcode" as postcode
from casrec_csv.deputy
left outer join casrec_csv.deputyship on deputy."Deputy No" = deputyship."Deputy No"
left outer join casrec_csv.deputy_address on deputyship."Dep Addr No" = deputy_address."Dep Addr No"
where "Dep Surname" = 'Bates'
order by "Dep Forename", "Dep Surname", "Dep Postcode";





select
--        count(*)
    "order"."Case" as caserecnumber,
       deputyship."CoP Case",
       deputy."Dep Forename" as firstname,
       deputy."Dep Surname" as surname,
       deputy_address."Dep Postcode" as postcode
from casrec_csv.order
left outer join casrec_csv.deputyship on "order"."CoP Case" = deputyship."CoP Case"
left outer join casrec_csv.deputy on deputyship."Deputy No" = deputy."Deputy No"
left outer join casrec_csv.deputy_address on deputyship."Dep Addr No" = deputy_address."Dep Addr No"
where "order"."Case" = '99328514'
order by "order"."Case", "Dep Forename", "Dep Surname", "Dep Postcode";



select distinct
       deputy_address."Dep Postcode",
       deputy_address."Dep Addr No",
       deputyship."Deputy No",
                deputy."Dep Forename", "Dep Surname",
                "order"."Case"
from casrec_csv.deputy_address
inner join casrec_csv.deputyship on deputyship."Dep Addr No" = deputy_address."Dep Addr No"
inner join casrec_csv.deputy on deputy."Deputy No" = deputyship."Deputy No"
inner join casrec_csv."order" on "order"."CoP Case" = deputyship."CoP Case"
where deputy_address."Dep Postcode" = 'BT7X 9RY'

select * from transform.persons where casrec_mapping_file_name = 'deputy_persons_mapping'
select * from casrec_csv.deputy

SELECT distinct surname from transform.persons where casrec_mapping_file_name = 'deputy_persons_mapping'