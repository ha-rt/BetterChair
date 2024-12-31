from os import getenv, path
from dotenv import load_dotenv
from .clearer import clear_email
from .tokens import issue_reset_token, authorize_reset_token
from smtplib import SMTP
from email.message import EmailMessage
from re import escape
from hashlib import sha512

load_dotenv()

email_server_loaded = False

try:
    email_server = SMTP(getenv("SMTP_SERVER"), getenv("SMTP_PORT"))
    email_server.starttls()
    email_server.login(getenv("SMTP_LOGIN"), getenv("SMTP_PASSWORD"))
    email_server_loaded = True
except:
    print("EMAILS OFFLINE!! Could not connect to email server")

def compare_passwords(password, salt, db_password):
    encoded_password_hash = (password + salt).encode()

    if sha512(encoded_password_hash).hexdigest() != db_password:
        return False

    return True

def issue_email(email, reset_link, reset_token):
    global email_server

    current_dir = path.dirname(path.abspath(__file__))
    template_file_path = path.join(current_dir, "templates", "account_recovery.txt")

    try:
        with open(template_file_path, "r") as file:
            content = file.read()
    except FileNotFoundError:
        print(f"File not found: {template_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

    content = content.replace("{reset_link}", reset_link)
    content = content.replace("{token}", reset_token)

    signup_email = EmailMessage()
    signup_email.set_content(content)
    signup_email['Subject'] = "Password Reset Request"
    signup_email['From'] = getenv("EMAIL_LOGIN_SENDER")
    signup_email["To"] = f"<{email}>"

    email_server.send_message(signup_email)

def issue_password_reset(database, username, email):
    users = database["Users"]
    query = users.find_one({"username": {"$regex": f"^{escape(username)}$", "$options": "i"}})

    if not query:
        return {"error": "No user found"}, 404

    db_email = query["email"]

    send = True

    if email != db_email:
        send = False

    if send == True:
        issued_token = issue_reset_token(database, username)
        reset_link = f"https://betterchair.oliverm.me/password_reset?token={issued_token}"
        issue_email(db_email, reset_link, issued_token)

    return {"conf": "Your password reset token has been sent if your email was the same as your username!"}, 200

def confirm_password_reset(database, reset_token, password):
    authorized = authorize_reset_token(database, reset_token)

    if authorized[1] != 200:
        return authorized
    
    username = authorized[0]["username"]

    users = database["Users"]
    query = users.find_one({"username": {"$regex": f"^{escape(username)}$", "$options": "i"}})

    if not query:
        return {"error": "No user found"}, 404
        
    db_password = query["password"]
    db_salt = query["salt"]
    
    password_comparsion = compare_passwords(password, db_salt, db_password)
    if password_comparsion == True:
        return {"error": "Your new password can't be the same as your current password."}
    

    password = sha512((password + db_salt).encode('utf-8')).hexdigest()

    try:
        users.update_one({"id": query["id"]}, {"$set": {"password": str(password)}})
        database["RTokens"].delete_one({"token": reset_token})
    except:
        return {"error": "Failed to update the password, try again"}, 500
    
    tokens = database["Tokens"]

    try:
        tokens.delete_many({"id": query["id"]})
    except:
        return {"error": "Failed to delete the previous account tokens"}, 200
    
    return {"conf": "Your password has been reset!"}, 200


if __name__ == "__main__":
    load_dotenv()