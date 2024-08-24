import sqlite3

def delete_all_groups():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    try:
        # Delete all entries in user_groups first to avoid foreign key constraint errors
        c.execute('DELETE FROM user_groups')

        # Delete all groups
        c.execute('DELETE FROM groups')

        # Commit the changes
        conn.commit()
        print("All groups and related user-group data have been deleted.")

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    delete_all_groups()
