from re import compile, escape
from os import path

username_regex = compile(r"[^a-zA-Z0-9_]")
email_regex = compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
banned_names_file = path.join(path.dirname(path.abspath(__file__)), 'banned_names.txt')

def clear_email(email):
    if not email_regex.search(email):
        return {"error": "Invalid Email"}, 400
    
    return 200

def clear_username(database, username):
    users = database["Users"]
    found_users = users.find_one({"username": {"$regex": f"^{escape(username)}$", "$options": "i"}})

    if found_users:
        return {"error": "Username in use"}, 409


    if username_regex.search(username.lower()) or username.lower() in {line.strip().lower() for line in open(path.join(path.dirname(path.abspath(__file__)), 'banned_names.txt'))}:
        return {"error": "Bad Username"}, 400

    return 200