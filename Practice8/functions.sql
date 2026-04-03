-- ─────────────────────────────────────────────────────────────────────────────
-- Function 1: search contacts by pattern (name, surname, or phone prefix)
-- Usage: SELECT * FROM search_contacts('Ali');
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION search_contacts(p_pattern TEXT)
RETURNS TABLE(
    id         INT,
    first_name VARCHAR,
    last_name  VARCHAR,
    phone      VARCHAR
) AS $$
BEGIN
    RETURN QUERY
        SELECT
            pb.id,
            pb.first_name,
            pb.last_name,
            pb.phone
        FROM phonebook pb
        WHERE pb.first_name ILIKE '%' || p_pattern || '%'
           OR pb.last_name  ILIKE '%' || p_pattern || '%'
           OR pb.phone      LIKE  p_pattern || '%'
        ORDER BY pb.first_name;
END;
$$ LANGUAGE plpgsql;


-- ─────────────────────────────────────────────────────────────────────────────
-- Function 2: paginated query (LIMIT / OFFSET)
-- Usage: SELECT * FROM get_contacts_paginated(5, 0);
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(
    id         INT,
    first_name VARCHAR,
    last_name  VARCHAR,
    phone      VARCHAR
) AS $$
BEGIN
    RETURN QUERY
        SELECT
            pb.id,
            pb.first_name,
            pb.last_name,
            pb.phone
        FROM phonebook pb
        ORDER BY pb.id
        LIMIT  p_limit
        OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;
