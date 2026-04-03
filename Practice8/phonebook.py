from connect import get_connection, create_table


# ── helpers ───────────────────────────────────────────────────────────────────

def load_sql(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def print_rows(rows, headers=None):
    if not rows:
        print("  (no rows)")
        return
    if headers:
        widths = [max(len(str(h)), max(len(str(r[i])) for r in rows))
                  for i, h in enumerate(headers)]
        fmt = "  " + "  ".join(f"{{:<{w}}}" for w in widths)
        print(fmt.format(*headers))
        print("  " + "-" * (sum(widths) + 2 * len(widths)))
        for row in rows:
            print(fmt.format(*[v or "" for v in row]))
    else:
        for row in rows:
            print(" ", row)
    print()


# ── setup ─────────────────────────────────────────────────────────────────────

def setup():
    create_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(load_sql("functions.sql"))
    cursor.execute(load_sql("procedures.sql"))
    conn.commit()
    cursor.close()
    conn.close()
    print("Functions and procedures loaded.\n")


# ── wrappers ──────────────────────────────────────────────────────────────────

def search_contacts(pattern):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM search_contacts(%s);", (pattern,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_contacts_paginated(limit, offset):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM get_contacts_paginated(%s, %s);", (limit, offset))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def upsert_contact(first_name, last_name, phone):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("CALL upsert_contact(%s, %s, %s);", (first_name, last_name, phone))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Upsert done for '{first_name}'.")


def insert_many_contacts(names, phones):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("CALL insert_many_contacts(%s, %s);", (names, phones))
    conn.commit()
    # Fetch invalid contacts saved by the procedure
    cursor.execute("SELECT first_name, phone, reason FROM invalid_contacts;")
    invalid = cursor.fetchall()
    cursor.close()
    conn.close()
    if invalid:
        print("Invalid contacts:")
        print_rows(invalid, ["First Name", "Phone", "Reason"])
    else:
        print("All contacts inserted successfully.")


def delete_contact(first_name=None, phone=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("CALL delete_contact(%s, %s);", (first_name, phone))
    conn.commit()
    cursor.close()
    conn.close()
    print("Delete done.")


# ── menu ──────────────────────────────────────────────────────────────────────

def menu():
    setup()
    while True:
        print("=== PhoneBook (Practice 8) ===")
        print("1. Search contacts by pattern")
        print("2. Show contacts (paginated)")
        print("3. Upsert contact (insert or update)")
        print("4. Bulk insert contacts (with validation)")
        print("5. Delete contact by first name")
        print("6. Delete contact by phone")
        print("0. Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            pattern = input("Pattern: ").strip()
            rows = search_contacts(pattern)
            print_rows(rows, ["ID", "First Name", "Last Name", "Phone"])

        elif choice == "2":
            limit  = int(input("Rows per page: ").strip())
            offset = int(input("Offset (skip rows): ").strip())
            rows = get_contacts_paginated(limit, offset)
            print_rows(rows, ["ID", "First Name", "Last Name", "Phone"])

        elif choice == "3":
            first_name = input("First name: ").strip()
            last_name  = input("Last name (optional): ").strip()
            phone      = input("Phone: ").strip()
            upsert_contact(first_name, last_name or None, phone)

        elif choice == "4":
            print("Enter contacts as 'FirstName Phone', one per line. Empty line to finish:")
            names, phones = [], []
            while True:
                line = input("  > ").strip()
                if not line:
                    break
                parts = line.split()
                if len(parts) == 2:
                    names.append(parts[0])
                    phones.append(parts[1])
                else:
                    print("  Format: FirstName Phone")
            if names:
                insert_many_contacts(names, phones)

        elif choice == "5":
            name = input("First name to delete: ").strip()
            delete_contact(first_name=name)

        elif choice == "6":
            phone = input("Phone to delete: ").strip()
            delete_contact(phone=phone)

        elif choice == "0":
            print("Goodbye!")
            break

        else:
            print("Invalid choice.\n")


if __name__ == "__main__":
    menu()
