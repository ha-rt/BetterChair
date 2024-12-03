import time
from datetime import timedelta
from uuid import uuid4
from pymongo import MongoClient
import dotenv
from os import getenv

dotenv.load_dotenv()

# Authentication Token Document
#
# {
#   token: uuid4,
#   id: uuid4,
#   expiry: unix-time,
# }

def generate_expiry():
    current_time = time.gmtime(time.time())
    expiry = time.mktime(current_time) + (14 * 86400)
    
    return(expiry)

def clear_id(database, id):
    tokens = database["Tokens"]
    id = str(id)

    while len(list(tokens.find({"token":id}))) != 0:
        print("WARNING WARNING: Requested ID is found | IDS LIKELY RUNNING OUT")
        id = uuid4()

    return str(id)

def issue_token(database, id):
    token = clear_id(database, uuid4())

    database["Tokens"].insert_one( {
        "token": token,
        "id": id,
        "expiry": str(generate_expiry())
    })

    return token

def authorize_token(database, token):
    tokens = database["Tokens"]
    data_search = tokens.find({"token": token})

    pass