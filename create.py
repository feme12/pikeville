import sqlite3
import bcrypt

# Create a SQLite database and a users table
conn = sqlite3.connect('user.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
''')
conn.commit()

def create_user(username, password, role):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, hashed_password, role))
    conn.commit()

if __name__ == "__main__":
    print("User Account Creation")

    username = input("Enter the username: ")
    password = input("Enter the password: ")
    role = input("Enter the user role (admin or user): ")

    # Check if the role is either "admin" or "user"
    if role not in ("admin", "user"):
        print("Invalid role. Please enter 'admin' or 'user'.")
    else:
        create_user(username, password, role)
        print(f"User account for '{username}' created with role '{role}'.")