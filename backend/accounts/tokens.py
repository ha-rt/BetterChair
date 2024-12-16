import time
from uuid import uuid4
from pymongo import MongoClient
from dotenv import load_dotenv
from os import getenv

# Authentication Token Document
#
# {
#   token: uuid4,
#   id: uuid4,
#   expiry: unix-time,
# }

def clear_token(database, token):
    tokens = database["Tokens"]
    token = str(token)

    while len(list(tokens.find({"token":token}))) != 0:
        print("WARNING WARNING: Requested Token is found | TOKENS LIKELY RUNNING OUT")
        token = uuid4()

    return str(token)

def issue_token(database, id):
    token = clear_token(database, uuid4())

    database["Tokens"].insert_one( {
        "token": token,
        "id": id,
        "expiry": str(time.time() + (86400 * 14))
    })

    return token

def authorize_token(database, token, id):
    tokens = database["Tokens"]
    query = tokens.find_one({"token": token})

    if not query:
        return 404
    
    if float(query["expiry"]) <= time.time():
        tokens.delete_one({"token": token})
        return 401
    
    if query["id"] != id:
        return 403

    return 200

if __name__ == "__main__":
    load_dotenv()
