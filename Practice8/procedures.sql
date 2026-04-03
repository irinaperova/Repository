-- ─────────────────────────────────────────────────────────────────────────────
-- Procedure 1: upsert_contact
-- If a contact with the given first_name exists → update phone.
-- Otherwise → insert a new row.
-- Usage: CALL upsert_contact('Alice', 'Johnson', '+77011111111');
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE PROCEDURE upsert_contact(
    p_first_name VARCHAR,
    p_last_name  VARCHAR,
    p_phone      VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phonebook WHERE first_name = p_first_name) THEN
        UPDATE phonebook
        SET phone = p_phone
        WHERE first_name = p_first_name;
        RAISE NOTICE 'Updated phone for %', p_first_name;
    ELSE
        INSERT INTO phonebook (first_name, last_name, phone)
        VALUES (p_first_name, p_last_name, p_phone);
        RAISE NOTICE 'Inserted new contact: %', p_first_name;
    END IF;
END;
$$;


-- ─────────────────────────────────────────────────────────────────────────────
-- Procedure 2: insert_many_contacts
-- Bulk insert from parallel arrays of names and phones.
-- Validates phone format: must start with + and contain 10-15 digits.
-- Invalid entries are saved to the invalid_contacts table.
-- Usage: CALL insert_many_contacts(ARRAY['Bob','Bad'], ARRAY['+77021234567','abc']);
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE PROCEDURE insert_many_contacts(
    p_names  VARCHAR[],
    p_phones VARCHAR[]
)
LANGUAGE plpgsql AS $$
DECLARE
    i       INT;
    v_name  VARCHAR;
    v_phone VARCHAR;
BEGIN
    -- Clear previous invalid records for this run
    DELETE FROM invalid_contacts;

    FOR i IN 1 .. array_length(p_names, 1) LOOP
        v_name  := p_names[i];
        v_phone := p_phones[i];

        -- Validate: phone must match +7XXXXXXXXXX (or similar international format)
        IF v_phone !~ '^\+?[0-9]{10,15}$' THEN
            INSERT INTO invalid_contacts (first_name, phone, reason)
            VALUES (v_name, v_phone, 'Invalid phone format');
            RAISE NOTICE 'Invalid phone for % : %', v_name, v_phone;
        ELSE
            BEGIN
                INSERT INTO phonebook (first_name, phone)
                VALUES (v_name, v_phone)
                ON CONFLICT (phone) DO NOTHING;
            EXCEPTION WHEN OTHERS THEN
                INSERT INTO invalid_contacts (first_name, phone, reason)
                VALUES (v_name, v_phone, SQLERRM);
            END;
        END IF;
    END LOOP;
END;
$$;


-- ─────────────────────────────────────────────────────────────────────────────
-- Procedure 3: delete_contact
-- Deletes a contact by first_name OR by phone (pass NULL for the unused one).
-- Usage: CALL delete_contact('Alice', NULL);
--        CALL delete_contact(NULL, '+77011234567');
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE PROCEDURE delete_contact(
    p_first_name VARCHAR DEFAULT NULL,
    p_phone      VARCHAR DEFAULT NULL
)
LANGUAGE plpgsql AS $$
DECLARE
    rows_deleted INT;
BEGIN
    IF p_first_name IS NOT NULL THEN
        DELETE FROM phonebook WHERE first_name = p_first_name;
        GET DIAGNOSTICS rows_deleted = ROW_COUNT;
        RAISE NOTICE 'Deleted % row(s) by name "%"', rows_deleted, p_first_name;

    ELSIF p_phone IS NOT NULL THEN
        DELETE FROM phonebook WHERE phone = p_phone;
        GET DIAGNOSTICS rows_deleted = ROW_COUNT;
        RAISE NOTICE 'Deleted % row(s) by phone "%"', rows_deleted, p_phone;

    ELSE
        RAISE EXCEPTION 'Provide at least one of: p_first_name, p_phone';
    END IF;
END;
$$;
