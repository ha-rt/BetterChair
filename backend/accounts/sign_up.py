from uuid import uuid4
from pymongo import MongoClient
from os import getenv
from dotenv import load_dotenv
from hashlib import sha512
from clearer import clear_email, clear_username

load_dotenv()

# User Document
#
# {
#   id: uuid4
#   email: string
#   username: string
#   password: sha512
#   salt: string
# }

def clear_id(database, id):
    users = database["Users"]
    id = str(id)

    while len(list(users.find({"id":id}))) != 0:
        print("WARNING WARNING: Requested ID is found | IDS LIKELY RUNNING OUT")
        id = uuid4()

    return str(id)

def signup(database, data):
    data = {datapiece: str(data[datapiece]) for datapiece in data}
    data["password"] = data["password"].encode('utf-8')

    cleared_id = clear_id(database, uuid4())
    cleared_username = clear_username(database, data["username"])
    cleared_email = clear_email(data["email"])

    if cleared_email != 200:
        return clear_email

    if cleared_username != 200:
        return clear_username
    
    salt = uuid4().hex

    user_document = {
        "id": cleared_id,
        "email": data["email"],
        "username": data["username"],
        "password": sha512(data["password"] + salt.encode('utf-8')).hexdigest(),
        "salt": salt
    }

    try:
        database["Users"].insert_one(user_document)
    except:
        return 400, "Failed"
    
    return 200