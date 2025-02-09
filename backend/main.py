from pymongo import MongoClient
from os import getenv
from flask import Flask, request
from dotenv import load_dotenv
from flask_cors import CORS

from accounts import signup, login, issue_password_reset, confirm_password_reset, get_username_from_id
from committees import *

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

@app.route("/api/create_committee", methods=["POST"])
def create_committee_route():
    information = request.get_json()

    if not information.get("account_token") or not information.get("committee_name") or not information.get("countries") or not information.get("agenda"):
        return {"error": "Missing Arguments"}, 400
    
    if (
        type(information["account_token"]) != str 
        or type(information["committee_name"]) != str 
        or type(information["countries"]) != list 
        or type(information["agenda"]) != str
    ):
        return {"error": "Invalid Arguments"}, 400
    
    for country in information["countries"]:
        if type(country) != str:
            return {"error": "Invalid Arguments"}, 400

    account_token = information["account_token"]
    committee_name = information["committee_name"]
    countries = information["countries"]
    agenda = information["agenda"]

    try:
        result = create_committee(database, account_token, committee_name, countries, agenda)
    except Exception as e:
        return {"error": str(e)}, 500

    return result

@app.route("/api/get_username_from_id", methods=["POST"])
def get_username_route():
    information = request.get_json()

    if not information["id"]:
        return {"error": "Missing Arguments"}, 400
    
    if type(information["id"]) != str:
        return {"error": "Invalid Arguments"}, 400
    
    try:
        result = get_username_from_id(database, id)
    except Exception as e:
        return {"error": str(e)}, 500

    return result

@app.route("/api/get_accessible_committees", methods=["POST"])
def get_accessible_committees_route():
    information = request.get_json()

    if not information.get("account_token"):
        return {"error": "Missing Arguments"}, 400

    if type(information["account_token"]) != str:
        return {"error": "Invalid Arguments"}, 400

    account_token = information["account_token"]

    try:
        result = get_accessable_committees(database, account_token)
    except Exception as e:
        return {"error": str(e)}, 500

    return result

@app.route("/api/edit_committee", methods=["POST"])
def edit_committee_route():
    information = request.get_json()

    if not information.get("account_token") or not information.get("committee_id"):
        return {"error": "Missing Arguments"}, 400

    if (
        type(information["account_token"]) != str 
        or type(information["committee_id"]) != str
    ):
        return {"error": "Invalid Arguments"}, 400

    committee_name = information.get("committee_name")
    countries = information.get("countries")

    if committee_name is None and countries is None:
        return {"error": "At least one of 'committee_name' or 'countries' must be provided"}, 400

    if committee_name is not None and type(committee_name) != str:
        return {"error": "Invalid Arguments"}, 400

    if countries is not None:
        if type(countries) != list or not all(type(country) == str for country in countries):
            return {"error": "Invalid Arguments"}, 400

    account_token = information["account_token"]
    committee_id = information["committee_id"]

    try:
        result = edit_committee(database, account_token, committee_id, committee_name, countries)
    except Exception as e:
        return {"error": str(e)}, 500

    return result

@app.route("/api/delete_committee", methods=["POST"])
def delete_committee_route():
    information = request.get_json()

    if not information.get("account_token") or not information.get("committee_id"):
        return {"error": "Missing Arguments"}, 400

    if (
        type(information["account_token"]) != str 
        or type(information["committee_id"]) != str
    ):
        return {"error": "Invalid Arguments"}, 400

    account_token = information["account_token"]
    committee_id = information["committee_id"]

    try:
        result = delete_committee(database, account_token, committee_id)
    except Exception as e:
        return {"error": str(e)}, 500

    return result

@app.route("/api/get_countries_list", methods=["POST"])
def get_countries_list_route():
    information = request.get_json()

    if not information.get("account_token") or not information.get("committee_id"):
        return {"error": "Missing Arguments"}, 400

    if (
        type(information["account_token"]) != str 
        or type(information["committee_id"]) != str
    ):
        return {"error": "Invalid Arguments"}, 400

    account_token = information["account_token"]
    committee_id = information["committee_id"]

    try:
        result = get_countries_list(database, account_token, committee_id)
    except Exception as e:
        return {"error": str(e)}, 500

    return result

@app.route("/api/update_country_status", methods=["POST"])
def update_country_status_route():
    information = request.get_json()

    if not information.get("account_token") or not information.get("committee_id") or not information.get("country_status_updates"):
        return {"error": "Missing Arguments"}, 400

    if (
        type(information["account_token"]) != str 
        or type(information["committee_id"]) != str 
        or type(information["country_status_updates"]) != dict
    ):
        return {"error": "Invalid Arguments"}, 400

    for country, status in information["country_status_updates"].items():
        if not isinstance(country, str) or not isinstance(status, int) or status < 0 or status > 2:
            return {"error": f"Invalid status {status} for country {country}. Status must be between 0 and 2."}, 400

    account_token = information["account_token"]
    committee_id = information["committee_id"]
    country_status_updates = information["country_status_updates"]

    try:
        result = update_country_status(database, account_token, committee_id, country_status_updates)
    except Exception as e:
        return {"error": str(e)}, 500

    return result

@app.route("/api/update_committee_status", methods=["POST"])
def update_committee_status_route():
    information = request.get_json()

    if not information.get("account_token") or not information.get("committee_id") or not information.get("new_status"):
        return {"error": "Missing Arguments"}, 400

    if (
        type(information["account_token"]) != str 
        or type(information["committee_id"]) != str 
        or type(information["new_status"]) != str
    ):
        return {"error": "Invalid Arguments"}, 400

    account_token = information["account_token"]
    committee_id = information["committee_id"]
    new_status = information["new_status"]

    try:
        result = update_committee_status(database, account_token, committee_id, new_status)
    except Exception as e:
        return {"error": str(e)}, 500

    return result

@app.route("/api/get_committee_status", methods=["POST"])
def get_committee_status_route():
    information = request.get_json()

    if not information.get("account_token") or not information.get("committee_id"):
        return {"error": "Missing Arguments"}, 400

    if (
        type(information["account_token"]) != str 
        or type(information["committee_id"]) != str
    ):
        return {"error": "Invalid Arguments"}, 400

    account_token = information["account_token"]
    committee_id = information["committee_id"]

    try:
        result = get_committee_status(database, account_token, committee_id)
    except Exception as e:
        return {"error": str(e)}, 500

    return result

@app.route("/api/get_status_info", methods=["POST"])
def get_status_info_route():
    information = request.get_json()

    if not information.get("account_token") or not information.get("committee_id"):
        return {"error": "Missing Arguments"}, 400

    if (
        type(information["account_token"]) != str 
        or type(information["committee_id"]) != str
    ):
        return {"error": "Invalid Arguments"}, 400

    account_token = information["account_token"]
    committee_id = information["committee_id"]

    try:
        result = get_status_info(database, account_token, committee_id)
    except Exception as e:
        return {"error": str(e)}, 500

    return result

@app.route("/api/set_status_info", methods=["POST"])
def set_status_info_route():
    information = request.get_json()

    if not information.get("account_token") or not information.get("committee_id") or not information.get("new_active_cache"):
        return {"error": "Missing Arguments"}, 400

    if (
        type(information["account_token"]) != str 
        or type(information["committee_id"]) != str
        or type(information["new_active_cache"]) != dict
    ):
        return {"error": "Invalid Arguments"}, 400

    account_token = information["account_token"]
    committee_id = information["committee_id"]
    new_active_cache = information["new_active_cache"]

    try:
        result = set_status_info(database, account_token, committee_id, new_active_cache)
    except Exception as e:
        return {"error": str(e)}, 500

    return result

@app.route("/api/add_motion", methods=["POST"])
def add_motion_route():
    information = request.get_json()

    if not information.get("account_token") or not information.get("committee_id") or not information.get("motion_type") or not information.get("country") or not information.get("info"):
        return {"error": "Missing Arguments"}, 400

    if (
        type(information["account_token"]) != str 
        or type(information["committee_id"]) != str
        or type(information["motion_type"]) != str
        or type(information["country"]) != str
        or type(information["info"]) != dict
    ):
        return {"error": "Invalid Arguments"}, 400

    account_token = information["account_token"]
    committee_id = information["committee_id"]
    motion_type = information["motion_type"]
    country = information["country"]
    info = information["info"]

    try:
        result = add_motion(database, account_token, committee_id, motion_type, country, info)
    except Exception as e:
        return {"error": str(e)}, 500

    return result

@app.route("/api/pass_motion", methods=["POST"])
def pass_motion_route():
    information = request.get_json()

    if not information.get("account_token") or not information.get("committee_id") or not information.get("motion_id"):
        return {"error": "Missing Arguments"}, 400

    if (
        type(information["account_token"]) != str 
        or type(information["committee_id"]) != str
        or type(information["motion_id"]) != str
    ):
        return {"error": "Invalid Arguments"}, 400

    account_token = information["account_token"]
    committee_id = information["committee_id"]
    motion_id = information["motion_id"]

    try:
        result = pass_motion(database, account_token, committee_id, motion_id)
    except Exception as e:
        return {"error": str(e)}, 500

    return result

@app.route("/api/fail_motion", methods=["POST"])
def fail_motion_route():
    information = request.get_json()

    if not information.get("account_token") or not information.get("committee_id") or not information.get("motion_id"):
        return {"error": "Missing Arguments"}, 400

    if (
        type(information["account_token"]) != str 
        or type(information["committee_id"]) != str
        or type(information["motion_id"]) != str
    ):
        return {"error": "Invalid Arguments"}, 400

    account_token = information["account_token"]
    committee_id = information["committee_id"]
    motion_id = information["motion_id"]

    try:
        result = fail_motion(database, account_token, committee_id, motion_id)
    except Exception as e:
        return {"error": str(e)}, 500

    return result

if __name__ == "__main__":    
    app.run(port=8088, debug=True)