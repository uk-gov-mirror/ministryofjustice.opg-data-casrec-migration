-- NOTE
-- Add corresponding drop function in drop_transformation_functions.sql

-- capitalise
CREATE OR REPLACE FUNCTION transf_capitalise(source varchar)
RETURNS varchar AS $$
DECLARE
BEGIN
    RETURN upper(source);
END;
$$ LANGUAGE plpgsql;

-- convert_to_bool
CREATE OR REPLACE FUNCTION transf_convert_to_bool(source varchar)
RETURNS boolean AS $$
DECLARE
BEGIN
    RETURN source = '1.0';
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION getCasrecAddress(ad1 varchar, ad2 varchar, ad3 varchar, ad4 varchar)
RETURNS varchar AS $$
DECLARE
    addressConcat varchar;
BEGIN
    addressConcat := '';

    IF (NULLIF(TRIM(ad1), '') IS NOT NULL) THEN
        addressConcat := addressConcat || ',' || ad1;
    END IF;
    IF (NULLIF(TRIM(ad2), '') IS NOT NULL) THEN
        addressConcat := addressConcat || ',' || ad2;
    END IF;
    IF (NULLIF(TRIM(ad3), '') IS NOT NULL) THEN
        addressConcat := addressConcat || ',' || ad3;
    END IF;
    IF (NULLIF(TRIM(ad4), '') IS NOT NULL) THEN
        addressConcat := addressConcat || ',' || ad4;
    END IF;

    RETURN right(addressConcat,-1);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION getSiriusAddress(addressLines anyelement, town varchar, county varchar)
    RETURNS varchar AS $$
DECLARE
    address_concat varchar;
    x varchar;
BEGIN
    address_concat := array_to_string(ARRAY(SELECT json_array_elements_text(addressLines)), ',');

    IF (NULLIF(TRIM(town), '') IS NOT NULL) THEN
        address_concat = address_concat || ',' || town::text;
    END IF;

    IF (NULLIF(TRIM(county), '') IS NOT NULL) THEN
        address_concat = address_concat || ',' || county::text;
    END IF;

    RETURN address_concat;
END;
$$ LANGUAGE plpgsql;
