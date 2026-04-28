import csv
import json
from pathlib import Path
from typing import Optional

from connect import get_connection

BASE = Path(__file__).resolve().parent


def run_sql_file(filename: str) -> None:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute((BASE / filename).read_text())
    print(f"Executed {filename}")


def init_db() -> None:
    run_sql_file("schema.sql")
    run_sql_file("procedures.sql")


def get_group_id(cur, group_name: str) -> int:
    group_name = group_name.strip() or "Other"
    cur.execute("INSERT INTO groups(name) VALUES (%s) ON CONFLICT(name) DO NOTHING", (group_name,))
    cur.execute("SELECT id FROM groups WHERE LOWER(name)=LOWER(%s)", (group_name,))
    return cur.fetchone()[0]


def add_contact(name: str, email: str = "", birthday: Optional[str] = None, group_name: str = "Other") -> int:
    with get_connection() as conn, conn.cursor() as cur:
        group_id = get_group_id(cur, group_name)
        cur.execute(
            """
            INSERT INTO contacts(name, email, birthday, group_id)
            VALUES (%s, %s, NULLIF(%s, '')::DATE, %s)
            ON CONFLICT(name) DO UPDATE SET
                email = EXCLUDED.email,
                birthday = EXCLUDED.birthday,
                group_id = EXCLUDED.group_id
            RETURNING id
            """,
            (name, email or None, birthday or "", group_id),
        )
        return cur.fetchone()[0]


def add_phone(contact_name: str, phone: str, phone_type: str = "mobile") -> None:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("CALL add_phone(%s, %s, %s)", (contact_name, phone, phone_type))


def list_contacts(group: str = "", email_query: str = "", sort_by: str = "name", limit: int = 10, offset: int = 0):
    allowed_sort = {"name": "c.name", "birthday": "c.birthday NULLS LAST", "date": "c.created_at"}
    sort_sql = allowed_sort.get(sort_by, "c.name")
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT c.id, c.name, COALESCE(c.email,''), c.birthday, COALESCE(g.name,''),
                   COALESCE(string_agg(p.phone || ' (' || p.type || ')', ', '), '') AS phones,
                   c.created_at
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            LEFT JOIN phones p ON p.contact_id = c.id
            WHERE (%s = '' OR LOWER(g.name) = LOWER(%s))
              AND (%s = '' OR LOWER(COALESCE(c.email,'')) LIKE LOWER('%%' || %s || '%%'))
            GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
            ORDER BY {sort_sql}
            LIMIT %s OFFSET %s
            """,
            (group, group, email_query, email_query, limit, offset),
        )
        return cur.fetchall()


def print_rows(rows):
    if not rows:
        print("No contacts found.")
        return
    for row in rows:
        print(f"#{row[0]} | {row[1]} | email: {row[2]} | birthday: {row[3]} | group: {row[4]} | phones: {row[5]}")


def search(query: str):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM search_contacts(%s)", (query,))
        return cur.fetchall()


def export_json(filename: str = "contacts.json") -> None:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT c.id, c.name, c.email, c.birthday, g.name,
                   COALESCE(json_agg(json_build_object('phone', p.phone, 'type', p.type))
                            FILTER (WHERE p.id IS NOT NULL), '[]')
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            LEFT JOIN phones p ON p.contact_id = c.id
            GROUP BY c.id, c.name, c.email, c.birthday, g.name
            ORDER BY c.name
            """
        )
        data = []
        for cid, name, email, birthday, group, phones in cur.fetchall():
            data.append({
                "id": cid,
                "name": name,
                "email": email,
                "birthday": birthday.isoformat() if birthday else None,
                "group": group,
                "phones": phones,
            })
    Path(filename).write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"Exported to {filename}")


def import_json(filename: str = "contacts.json") -> None:
    data = json.loads(Path(filename).read_text())
    with get_connection() as conn, conn.cursor() as cur:
        for item in data:
            name = item["name"]
            cur.execute("SELECT id FROM contacts WHERE LOWER(name)=LOWER(%s)", (name,))
            exists = cur.fetchone()
            if exists:
                answer = input(f"Contact {name} exists. overwrite/skip? ").strip().lower()
                if answer.startswith("s"):
                    continue
                cur.execute("DELETE FROM phones WHERE contact_id=%s", (exists[0],))
            group_id = get_group_id(cur, item.get("group") or "Other")
            cur.execute(
                """
                INSERT INTO contacts(name, email, birthday, group_id)
                VALUES (%s, %s, NULLIF(%s, '')::DATE, %s)
                ON CONFLICT(name) DO UPDATE SET email=EXCLUDED.email, birthday=EXCLUDED.birthday, group_id=EXCLUDED.group_id
                RETURNING id
                """,
                (name, item.get("email"), item.get("birthday") or "", group_id),
            )
            cid = cur.fetchone()[0]
            for ph in item.get("phones", []):
                cur.execute("INSERT INTO phones(contact_id, phone, type) VALUES (%s, %s, %s)", (cid, ph["phone"], ph.get("type", "mobile")))
    print("Import complete")


def import_csv(filename: str = "contacts.csv") -> None:
    with open(filename, newline="", encoding="utf-8") as f, get_connection() as conn, conn.cursor() as cur:
        reader = csv.DictReader(f)
        for row in reader:
            group_id = get_group_id(cur, row.get("group", "Other"))
            cur.execute(
                """
                INSERT INTO contacts(name, email, birthday, group_id)
                VALUES (%s, %s, NULLIF(%s, '')::DATE, %s)
                ON CONFLICT(name) DO UPDATE SET email=EXCLUDED.email, birthday=EXCLUDED.birthday, group_id=EXCLUDED.group_id
                RETURNING id
                """,
                (row["name"], row.get("email"), row.get("birthday", ""), group_id),
            )
            cid = cur.fetchone()[0]
            cur.execute("INSERT INTO phones(contact_id, phone, type) VALUES (%s, %s, %s)", (cid, row.get("phone", ""), row.get("type", "mobile")))
    print("CSV imported")


def paginate():
    group = input("Group filter empty/all: ").strip()
    email = input("Email search empty/all: ").strip()
    sort_by = input("Sort by name/birthday/date: ").strip() or "name"
    limit, offset = 5, 0
    while True:
        rows = list_contacts(group, email, sort_by, limit, offset)
        print_rows(rows)
        cmd = input("next / prev / quit: ").lower().strip()
        if cmd == "next":
            offset += limit
        elif cmd == "prev":
            offset = max(0, offset - limit)
        else:
            break


def menu():
    init_db()
    while True:
        print("\n1 Add contact  2 Add phone  3 Search  4 Filter/paginate  5 Import CSV  6 Export JSON  7 Import JSON  0 Exit")
        choice = input("> ").strip()
        if choice == "1":
            add_contact(input("Name: "), input("Email: "), input("Birthday YYYY-MM-DD: "), input("Group: "))
        elif choice == "2":
            add_phone(input("Contact name: "), input("Phone: "), input("Type home/work/mobile: ") or "mobile")
        elif choice == "3":
            print_rows(search(input("Query: ")))
        elif choice == "4":
            paginate()
        elif choice == "5":
            import_csv(input("CSV file: ") or str(BASE / "contacts.csv"))
        elif choice == "6":
            export_json(input("JSON file: ") or "contacts.json")
        elif choice == "7":
            import_json(input("JSON file: ") or "contacts.json")
        elif choice == "0":
            break


if __name__ == "__main__":
    menu()
