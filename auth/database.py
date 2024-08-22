import sqlite3

def initialize_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Create the users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT,
            profile_picture BLOB
        )
    ''')

    # Create the groups table
    c.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT
        )
    ''')

    # Create a user_groups table to link users to groups
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_groups (
            user_id INTEGER,
            group_id INTEGER,
            is_admin BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (group_id) REFERENCES groups(id),
            PRIMARY KEY (user_id, group_id)
        )
    ''')

    # Create the matches table
    c.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matchday INTEGER,
            season TEXT,
            home_team TEXT,
            away_team TEXT
        )
    ''')

    # Create the predictions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            match_id INTEGER,
            home_goals INTEGER,
            away_goals INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (match_id) REFERENCES matches (id)
        )
    ''')

    conn.commit()
    conn.close()

def execute_query(query, params=()):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    conn.close()

def fetch_one(query, params=()):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute(query, params)
    result = c.fetchone()
    conn.close()
    if result:
        return dict(zip([column[0] for column in c.description], result))
    return None

def fetch_all(query, params=()):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute(query, params)
    results = c.fetchall()
    conn.close()
    return [dict(zip([column[0] for column in c.description], row)) for row in results]
