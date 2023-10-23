import streamlit as st
import requests
import json
import time
import sqlite3
import bcrypt
from streamlit_option_menu import option_menu

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

def get_user(username):
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    return cursor.fetchone()

def list_users():
    cursor.execute('SELECT * FROM users')
    return cursor.fetchall()

def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

# Create a SessionState class to store user login state and rank
class SessionState:
    def __init__(self):
        self.login = False
        self.rank = None

# Create an instance of the SessionState class
session_state = SessionState()

application_open = True

def apply():
    error = st.empty()
    success = st.empty()
    st.header("Application")

    if application_open:
        form = st.form("Apply")
        questions1 = form.text_input("Question1")
        if form.form_submit_button("Submit"):
            if questions1 != "":
                webhook_url = 'https://discord.com/api/webhooks/1165598311399555094/4ASJGIKIoAiqjmLxw9bIDWJtyqBgaLWoABAKnZDHjj8al4E1HkUfKUJ9jsrCoovrQCk_'

                payload = {
                    "content": None,
                    "embeds": [
                        {
                            "title": "**NEW APPLICATION**",
                            "description": f"**QUESTION1**\n{questions1}",
                            "color": 10197915
                        }
                    ],
                    "attachments": []
                }
                headers = {
                    'Content-Type': 'application/json'
                }

                response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)

                if response.status_code == 204:
                    print('Embedded message sent successfully!')
                    success.success("Application Was Sent")
                    questions1.text_input_element.value = ""
                else:
                    print(f'Failed to send embedded message with status code {response.status_code}')
                    print(response.text)
                    error.error(f"Failed to send embedded message with status code {response.status_code}")
                    time.sleep(5)
                    error.empty()
            else:
                error.error("You forgot to fill in one of the questions.")
                time.sleep(5)
                error.empty()
    else:
        st.warning("Applications are currently closed")

def login():
    error = st.empty()
    success = st.empty()
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = get_user(username)

        if user and verify_password(user[2], password):
            session_state.login = True  # Set the user's login state to True
            session_state.rank = user[3]  # Store the user's rank
            success.success("Login successful.")
            time.sleep(5)
            success.empty()
        else:
            error.error("Incorrect Username or Password")
            time.sleep(5)
            error.empty()

def admin_menu():
    st.sidebar.subheader("Admin Menu")
    admin_selected = option_menu(
        menu_title="Admin Menu",
        options=["Users", "Create New User", "Change Users Role"],
        icons=["person", "person", "person"],
        menu_icon="cast",
        default_index=0,
        styles={
            "nav-link-selected": {"background-color": "grey", "font-weight": "bold"},
        }
    )
    return admin_selected

def admin_users_page():
    st.subheader("Admin Users Page")
    users = list_users()
    for user in users:
        st.write(f"Username: {user[1]}, Role: {user[3]}")

def admin_create_page():
    st.subheader("Admin Create New User Page")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    new_role = st.radio("Role", ["admin", "user"])

    if st.button("Create User"):
        create_user(new_username, new_password, new_role)
        st.success(f"User '{new_username}' created with role '{new_role}'")

def admin_change_roles_page():
    st.subheader("Admin Change Users Role Page")
    username_to_modify = st.text_input("Username to Modify")
    new_role = st.radio("New Role", ["admin", "user"])

    if st.button("Change Role"):
        cursor.execute('UPDATE users SET role = ? WHERE username = ?', (new_role, username_to_modify))
        conn.commit()
        st.success(f"Role of user '{username_to_modify}' changed to '{new_role}'")

def home():
    st.write("Pikeville Hub")

def main():
    st.set_page_config(page_title="Pikeville Hub", page_icon="logo.png")
    st.sidebar.image("logo.png")
    warning_message = """
    <div style="
        background-color: rgba(255, 165, 0, 0.6);
        border-style: solid;
        border-color: orange;
        color: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
    ">
        <div style="font-weight: bold;">WARNING:</div>
        <div>This page is still under development and may not work correctly.</div>
    </div>
    """

    st.sidebar.markdown(warning_message, unsafe_allow_html=True)
    st.sidebar.subheader("")

    with st.sidebar:
        selected = option_menu(
            menu_title="Main Menu",
            options=["Home", "Admin Login", "Apply"],
            icons=["house", "lock", "file-earmark-text"],
            menu_icon="cast",
            default_index=0,
            styles={
                "nav-link-selected": {"background-color": "grey", "font-weight": "bold"},
            }
        )

    if selected == "Admin Login":
        login()
    if selected == "Apply":
        apply()
    if selected == "Home":
        home()

    if session_state.login and session_state.rank == 'admin':
        admin_selected = admin_menu()

        if admin_selected == "Users":
            admin_users_page()
        elif admin_selected == "Create New User":
            admin_create_page()
        elif admin_selected == "Change Users Role":
            admin_change_roles_page()

if __name__ == "__main__":
    main()
