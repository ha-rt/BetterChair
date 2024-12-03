import re
import os

username_regex = re.compile(r"[^a-zA-Z0-9_]")
email_regex = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
banned_names_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'banned_names.txt')

def clear_email(email):
    if not email_regex.search(email):
        return 400, "Invalid Email"
    
    return 200

def clear_username(database, username):
    users = database["Users"]
    found_users = users.find({"username":username})
    
    for user in found_users:
        if user["username"] == username:
            return 409, "Username in use"

        continue

    if username_regex.search(username.lower()) or username.lower() in {line.strip().lower() for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'banned_names.txt'))}:
        return 400, "Bad Username"

    return 200