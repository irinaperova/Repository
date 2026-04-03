import csv
from connect import get_connection, create_table


# ── CREATE ────────────────────────────────────────────────────────────────────

def insert_contact(first_name, last_name, phone):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO phonebook (first_name, last_name, phone) VALUES (%s, %s, %s);",
            (first_name, last_name, phone)
        )
        conn.commit()
        print(f"Contact '{first_name} {last_name}' added.")
    except Exception as e:
        conn.rollback()
        print(f"Error inserting contact: {e}")
    finally:
        cursor.close()
        conn.close()


def import_from_csv(filepath="contacts.csv"):
    conn = get_connection()
    cursor = conn.cursor()
    inserted = 0
    skipped = 0
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                cursor.execute(
                    "INSERT INTO phonebook (first_name, last_name, phone) VALUES (%s, %s, %s) ON CONFLICT (phone) DO NOTHING;",
                    (row["first_name"], row.get("last_name", ""), row["phone"])
                )
                if cursor.rowcount:
                    inserted += 1
                else:
                    skipped += 1
            except Exception as e:
                conn.rollback()
                print(f"Error on row {row}: {e}")
    conn.commit()
    cursor.close()
    conn.close()
    print(f"CSV import done: {inserted} inserted, {skipped} skipped (duplicates).")


def input_contact():
    first_name = input("First name: ").strip()
    last_name = input("Last name (optional): ").strip()
    phone = input("Phone: ").strip()
    if first_name and phone:
        insert_contact(first_name, last_name, phone)
    else:
        print("First name and phone are required.")


# ── READ ──────────────────────────────────────────────────────────────────────

def search_contacts(pattern=None):
    conn = get_connection()
    cursor = conn.cursor()
    if pattern:
        cursor.execute(
            """
            SELECT id, first_name, last_name, phone FROM phonebook
            WHERE first_name ILIKE %s
               OR last_name  ILIKE %s
               OR phone LIKE %s
            ORDER BY first_name;
            """,
            (f"%{pattern}%", f"%{pattern}%", f"{pattern}%")
        )
    else:
        cursor.execute("SELECT id, first_name, last_name, phone FROM phonebook ORDER BY first_name;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def print_contacts(rows):
    if not rows:
        print("No contacts found.")
        return
    print(f"\n{'ID':<5} {'First Name':<15} {'Last Name':<15} {'Phone':<20}")
    print("-" * 57)
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<15} {row[2] or '':<15} {row[3]:<20}")
    print()


# ── UPDATE ────────────────────────────────────────────────────────────────────

def update_by_username(old_first_name, new_first_name=None, new_phone=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if new_first_name:
            cursor.execute(
                "UPDATE phonebook SET first_name = %s WHERE first_name = %s;",
                (new_first_name, old_first_name)
            )
            print(f"Updated first name '{old_first_name}' → '{new_first_name}' ({cursor.rowcount} row(s)).")
        if new_phone:
            name = new_first_name if new_first_name else old_first_name
            cursor.execute(
                "UPDATE phonebook SET phone = %s WHERE first_name = %s;",
                (new_phone, name)
            )
            print(f"Updated phone for '{name}' → '{new_phone}' ({cursor.rowcount} row(s)).")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error updating contact: {e}")
    finally:
        cursor.close()
        conn.close()


# ── DELETE ────────────────────────────────────────────────────────────────────

def delete_by_username(first_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM phonebook WHERE first_name = %s;", (first_name,))
    conn.commit()
    print(f"Deleted {cursor.rowcount} contact(s) with first name '{first_name}'.")
    cursor.close()
    conn.close()


def delete_by_phone(phone):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM phonebook WHERE phone = %s;", (phone,))
    conn.commit()
    print(f"Deleted {cursor.rowcount} contact(s) with phone '{phone}'.")
    cursor.close()
    conn.close()


# ── MENU ──────────────────────────────────────────────────────────────────────

def menu():
    create_table()
    while True:
        print("\n=== PhoneBook ===")
        print("1. Show all contacts")
        print("2. Search contacts")
        print("3. Add contact (manual input)")
        print("4. Import contacts from CSV")
        print("5. Update contact")
        print("6. Delete contact by first name")
        print("7. Delete contact by phone")
        print("0. Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            print_contacts(search_contacts())

        elif choice == "2":
            pattern = input("Search (name or phone prefix): ").strip()
            print_contacts(search_contacts(pattern))

        elif choice == "3":
            input_contact()

        elif choice == "4":
            path = input("CSV file path [contacts.csv]: ").strip() or "contacts.csv"
            import_from_csv(path)

        elif choice == "5":
            name = input("First name to update: ").strip()
            new_name = input("New first name (leave blank to skip): ").strip()
            new_phone = input("New phone (leave blank to skip): ").strip()
            update_by_username(name, new_name or None, new_phone or None)

        elif choice == "6":
            name = input("First name to delete: ").strip()
            delete_by_username(name)

        elif choice == "7":
            phone = input("Phone to delete: ").strip()
            delete_by_phone(phone)

        elif choice == "0":
            print("Goodbye!")
            break

        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    menu()
