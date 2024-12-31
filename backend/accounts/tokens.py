import time
from uuid import uuid4
from pymongo import MongoClient
from dotenv import load_dotenv
from os import getenv

# Reset Token Docujment

# {
#     token: uuid4,
#     username: str,
#     expiry: unix-time,
# }
def clear_reset_token(database, token):
    tokens = database["RTokens"]
    token = str(token)

    while len(list(tokens.find({"token":token}))) != 0:
        print("WARNING WARNING: Requested RToken is found | RTOKENS LIKELY RUNNING OUT")
        token = uuid4()

    return str(token)

def issue_reset_token(database, username):
    token = clear_token(database, uuid4())

    database["RTokens"].insert_one( {
        "token": token,
        "username": username,
        "expiry": str(time.time() + (60 * 90))
    })

    return token

def authorize_reset_token(database, token):
    tokens = database["RTokens"]
    query = tokens.find_one({"token": token})

    if not query:
        return {"error": "No reset token found."}, 404
    
    if float(query["expiry"]) <= time.time():
        tokens.delete_one({"token": token})
        return {"error": "This reset token is expired"}, 401

    return {"username": query["username"]}, 200

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
