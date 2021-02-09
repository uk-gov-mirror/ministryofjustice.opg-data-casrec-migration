SELECT u.id,
u.firstname as user_first_name,
u.lastname as user_last_name,
u.email as user_email,
u.phone_main as user_phone_number,
u.registration_date,
u.last_logged_in,
c.firstname as client_first_name,
c.lastname as client_last_name,
COUNT(r.id) as submitted_reports
FROM dd_user as u
LEFT JOIN deputy_case as dc on u.id = dc.user_id
LEFT JOIN client as c on dc.client_id = c.id
LEFT JOIN report as r on c.id = r.client_id
WHERE r.submit_date is not null AND u.role_name = 'ROLE_LAY_DEPUTY' AND u.last_logged_in > :oneYearAgo
GROUP BY u.id, u.firstname, u.lastname, u.email, u.registration_date, u.last_logged_in, c.firstname, c.lastname
