import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Add the is_admin column to the user_groups table
try:
    c.execute('ALTER TABLE user_groups ADD COLUMN is_admin BOOLEAN DEFAULT 0;')
    conn.commit()
    print("is_admin column added successfully.")
except sqlite3.OperationalError as e:
    print(f"Error occurred: {e}")

# Close the connection
conn.close()
