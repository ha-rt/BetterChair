from uuid import uuid4
from pymongo import MongoClient
from os import getenv, path
from dotenv import load_dotenv
from hashlib import sha512
from .clearer import clear_email, clear_username
from .tokens import issue_token
from smtplib import SMTP
from email.message import EmailMessage

load_dotenv()

email_server_loaded = False

try:
    email_server = SMTP(getenv("SMTP_SERVER"), getenv("SMTP_PORT"))
    email_server.starttls()
    email_server.login(getenv("SMTP_LOGIN"), getenv("SMTP_PASSWORD"))
    email_server_loaded = True
except:
    print("EMAILS OFFLINE!! Could not connect to email server")

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

def issue_email(email):
    global email_server

    current_dir = path.dirname(path.abspath(__file__))
    template_file_path = path.join(current_dir, "templates", "account_creation.txt")

    try:
        with open(template_file_path, "r") as file:
            content = file.read()
    except FileNotFoundError:
        print(f"File not found: {template_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

    signup_email = EmailMessage()
    signup_email.set_content(content)
    signup_email['Subject'] = "Account Registration Confirmation"
    signup_email['From'] = getenv("EMAIL_LOGIN_SENDER")
    signup_email["To"] = f"<{email}>"

    email_server.send_message(signup_email)


def signup(database, data):
    data["password"] = data["password"].encode('utf-8')

    cleared_id = clear_id(database, uuid4())
    cleared_username = clear_username(database, data["username"])
    cleared_email = clear_email(data["email"])

    if cleared_email != 200:
        return cleared_email

    if cleared_username != 200:
        return cleared_username
    
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
        return 500, "Failed to create account"
    
    global email_server_loaded

    if email_server_loaded == True:
        try:
            issue_email(data["email"])
        except Exception as e:
            print(f"Failed to issue email, yet SMTP Passed? {e}")  
    
    issued_token = issue_token(database, cleared_id)

    return {"token": issued_token}, 200

if __name__ == "__main__":
    load_dotenv()