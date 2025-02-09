from pymongo import MongoClient
from dotenv import load_dotenv
from os import getenv
from hashlib import sha512
from .tokens import issue_token
from re import escape

def compare_passwords(password, salt, db_password):
    encoded_password_hash = (password + salt).encode()

    if sha512(encoded_password_hash).hexdigest() != db_password:
        return False

    return True

def get_username_from_id(database, id):
    users = database["Users"]
    query = users.find_one({"id": id})

    if not query:
        return 404

    if not query["username"]:
        return 404

    return query["username"]

def login(database, username, password):
    users = database["Users"]
    query = users.find_one({"username": {"$regex": f"^{escape(username)}$", "$options": "i"}})

    if not query:
        return {"error": "No user found"}, 404

    db_password = query["password"]
    db_salt = query["salt"]

    password_result = compare_passwords(password, db_salt, db_password)

    if password_result != True:
        return {"error": "Incorrect Password"}, 403
    
    issued_token = issue_token(database, query["id"])

    return {"token": issued_token}, 200

if __name__ == "__main__":
    load_dotenv()