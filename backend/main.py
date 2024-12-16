from pymongo import MongoClient
from os import getenv
from flask import Flask, request
from dotenv import load_dotenv

from accounts import signup, login

load_dotenv()

database = MongoClient(getenv("MONGO_DB_URI"))["BetterMUN"]
app = Flask(__name__)


# Accounts

# Required Info: Username, Email, Password
@app.route("/api/sign_up")
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
@app.route("/api/log_in")
def login_route():
    information = request.get_json()

    if not information.get("username") or not information.get("email") or not information.get("password"):
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

if __name__ == "__main__":    
    app.run(port=8088, debug=True)