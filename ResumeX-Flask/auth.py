import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

USERS_FILE = "users.json"


def load_users():
    if not os.path.exists(USERS_FILE):
        return []

    with open(USERS_FILE, "r") as file:
        try:
            data = json.load(file)
            if isinstance(data, list):
                return data
            return []
        except:
            return []


def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=4)


def register_user(username, email, password):
    users = load_users()

    for user in users:
        if user["username"] == username:
            return False, "Username already exists."
        if user["email"] == email:
            return False, "Email already exists."

    hashed_password = generate_password_hash(password)

    users.append({
        "username": username,
        "email": email,
        "password": hashed_password
    })

    save_users(users)
    return True, "Registration successful!"


def login_user(username, password):
    users = load_users()

    for user in users:
        if user["username"] == username:
            if check_password_hash(user["password"], password):
                return True, "Login successful!"
            else:
                return False, "Invalid password."

    return False, "User not found."
