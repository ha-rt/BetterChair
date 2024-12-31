from pymongo import MongoClient
from os import getenv
from flask import Flask, request
from dotenv import load_dotenv
from flask_cors import CORS

from accounts import signup, login, issue_password_reset, confirm_password_reset

load_dotenv()

database = MongoClient(getenv("MONGO_DB_URI"))["BetterMUN"]
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://127.0.0.1:5500"}})

# Accounts

# Required Info: Username, Email, Password
@app.route("/api/sign_up", methods=["POST"])
def signup_route():
    information = request.get_json()

    if not information.get("username") or not information.get("email") or not information.get("password"):
        return {"error": "Missing Arguments"}, 400
    
    if type(information["username"]) != str or type(information["email"]) != str or type(information["password"]) != str:
        return {"error": "Invalid Arguments"}, 400

    try:
        account = signup(database, information)
    except Exception as e:
        return {"error": str(e)}, 500
    
    print(account)

    return account

# Required Info: Username, Password
@app.route("/api/log_in", methods=["POST"])
def login_route():
    information = request.get_json()

    if not information.get("username") or not information.get("password"):
        return {"error": "Missing Arguments"}, 400

    if type(information["username"]) != str or type(information["password"]) != str:
        return {"error": "Invalid Arguments"}, 400

    username = information["username"]
    password = information["password"]

    try:
        account = login(database, username, password)
    except Exception as e:
        return {"error": str(e)}, 500
    
    return account

@app.route("/api/issue_reset_password", methods=["POST"])
def reset_password_issue_route():
    information = request.get_json()

    if not information.get("username") or not information.get("email"):
        return {"error": "Missing Arguments"}, 400
    
    if type(information["username"]) != str or type(information["email"]) != str:
        return {"error": "Invalid Arguments"}, 400
    
    username = information["username"]
    email = information["email"]

    try:
        reset_password = issue_password_reset(database, username, email)
    except Exception as e:
        return {"error": str(e)}, 500
    
    return reset_password

@app.route("/api/reset_password", methods=["POST"])
def reset_password_route():
    information = request.get_json()

    if not information.get("password_reset_token") or not information.get("password"):
        return {"error": "Missing Arguments"}, 400
    
    if type(information["password_reset_token"]) != str or type(information["password"]) != str:
        return {"error": "Invalid Arguments"}, 400
    
    password_reset_token = information["password_reset_token"]
    password = information["password"]

    try:
        reset_password = confirm_password_reset(database, password_reset_token, password)
    except Exception as e:
        return {"error": str(e)}, 500
    
    return reset_password

if __name__ == "__main__":    
    app.run(port=8088, debug=True)