from uuid import uuid4
import json
import bson.json_util as json_util

from .clearer import clear_id, clear_name
from accounts import get_id_from_token, authorize_token

# Committee Document
#
# {
#   id: uuid4
#   owner: uuid4
#   name: string
#   countries: dict
#   status: string
#   agenda: string
#   active_cache: dict
#   saved_cache: dict
# }

def parse_json(data):
    return json.loads(json_util.dumps(data))

def create_committee(database, account_token, committee_name, countries, agenda):
    cleared_id = clear_id(database, uuid4())
    cleared_name = clear_name(database, committee_name)

    if cleared_name != 200:
        return cleared_name
    
    owner = get_id_from_token(database, account_token)

    if owner == 404:
        return {"error": "Failed to authorize"}, 400
    
    clear_owner = authorize_token(database, account_token, owner)

    if clear_owner != 200:
        return clear_owner
    
    countries = {country: {"status":0, "index":index} for index, country in enumerate(countries)}

    committee_document = {
        "id": cleared_id,
        "owner": owner,
        "name": committee_name,
        "countries": countries,
        "status": "rc",
        "agenda": agenda,
        "active_cache": {},
        "saved_cache": []
    }

    try:
        database["Committees"].insert_one(committee_document)
    except:
        return {"error": "Failed to create the committee"}, 500

    return {"committee": f"Committee {committee_name} has been created."}, 200

def get_accessable_committees(database, account_token):
    owner = get_id_from_token(database, account_token)

    if owner == 404:
        return {"error": "Failed to authorize"}, 400
    
    clear_owner = authorize_token(database, account_token, owner)

    if clear_owner != 200:
        return clear_owner
    
    try:
        query = database["Committees"].find({"owner": owner})
    except:
        return {"error": "Failed to return the committees"}, 500
    
    query = parse_json(list(query))
    # query = [{key: convert_objectid(value) for key, value in doc.items()} for doc in query]

    try:
        return {"committees": query}, 200
    except:
        return {"error": "Failed to return the committees"}, 500

def edit_committee(database, account_token, committee_id, committee_name, countries):
    owner = get_id_from_token(database, account_token)

    if owner == 404:
        return {"error": "Failed to authorize"}, 400
    
    clear_owner = authorize_token(database, account_token, owner)

    if clear_owner != 200:
        return clear_owner

    committee_document = {}
    if committee_name is not None:
        committee_document["name"] = committee_name
    if countries is not None:
        countries = {country: 0 for country in countries}
        committee_document["countries"] = countries

    if not committee_document: 
        return {"error": "No document info provided"}, 400
    
    try:
        result = database["Committees"].update_one(
            {"id": committee_id}, 
            {"$set": committee_document}
        )
        if result.matched_count == 0:
            return {"error": "Committee not found"}, 404
    except Exception as e:
        return {"error": f"Failed to update the committee: {str(e)}"}, 500

    return {"committee": f"Committee {committee_name} has been updated."}, 200

def delete_committee(database, account_token, committee_id):
    owner = get_id_from_token(database, account_token)

    if owner == 404:
        return {"error": "Failed to authorize"}, 400
    
    clear_owner = authorize_token(database, account_token, owner)

    if clear_owner != 200:
        return clear_owner
    
    try:
        database["Committees"].delete_one({"id": committee_id})
    except Exception as e:
        return {"error": f"Failed to update the committee: {str(e)}"}, 500

    return {"committee": f"Committee {committee_id} has been deleted."}, 200

def get_countries_list(database, account_token, committee_id):
    owner = get_id_from_token(database, account_token)

    if owner == 404:
        return {"error": "Failed to authorize"}, 400

    clear_owner = authorize_token(database, account_token, owner)

    if clear_owner != 200:
        return clear_owner

    try:
        committee_document = database["Committees"].find_one({"id": committee_id, "owner": owner})
        if not committee_document:
            return {"error": "Committee not found or access denied"}, 404

        countries = committee_document.get("countries", {})
        return {"countries": countries}, 200
    except Exception as e:
        return {"error": f"Failed to retrieve countries: {str(e)}"}, 500

def update_country_status(database, account_token, committee_id, country_status_updates):
    owner = get_id_from_token(database, account_token)

    if owner == 404:
        return {"error": "Failed to authorize"}, 400

    clear_owner = authorize_token(database, account_token, owner)

    if clear_owner != 200:
        return clear_owner

    try:
        committee_document = database["Committees"].find_one({"id": committee_id, "owner": owner})
        if not committee_document:
            return {"error": "Committee not found or access denied"}, 404

        updated_countries = committee_document.get("countries", {})

        for country, status in country_status_updates.items():
            if not isinstance(status, int) or status < 0 or status > 2:
                return {"error": f"Invalid status {status} for country {country}. Status must be between 0 and 2."}, 400
            
            if not country in updated_countries.keys():
                return {"error": f"Updated country {country}, is not in the countries list"}, 400
            
            updated_countries[country]["status"] = status

        result = database["Committees"].update_one(
            {"id": committee_id, "owner": owner},
            {"$set": {"countries": updated_countries}}
        )
        
        if result.matched_count == 0:
            return {"error": "Failed to update committee"}, 500

    except Exception as e:
        return {"error": f"Failed to update status: {str(e)}"}, 500

    return {"message": "Country status updated successfully."}, 200

def update_committee_status(database, account_token, committee_id, new_status):
    valid_status_values = ["rc", "psl", "ssl", "vm", "umc", "mc", "rt", "mv", "adj", "ssp"]

    owner = get_id_from_token(database, account_token)

    if owner == 404:
        return {"error": "Failed to authorize"}, 400

    clear_owner = authorize_token(database, account_token, owner)

    if clear_owner != 200:
        return clear_owner
    
    if new_status == "nai":
        new_status = "psl"

    if new_status not in valid_status_values:

        return {"error": f"Invalid status value. Valid statuses are {', '.join(valid_status_values)}."}, 400

    try:
        committee_document = database["Committees"].find_one({"id": committee_id, "owner": owner})

        if not committee_document:
            return {"error": "Committee not found or access denied"}, 404

        active_cache = committee_document.get("active_cache", [])
        saved_cache = committee_document.get("saved_cache", {})

        if active_cache != {}:
            saved_cache.append(active_cache)

        result = database["Committees"].update_one(
            {"id": committee_id, "owner": owner},
            {
                "$set": {
                    "status": new_status,
                    "active_cache": {},
                },
                "$push": {
                    "saved_cache": {"$each": [active_cache]}
                }
            }
        )

        if result.matched_count == 0:
            return {"error": "Failed to update committee status"}, 500

    except Exception as e:
        return {"error": f"Failed to update status: {str(e)}"}, 500

    return {"message": f"Committee status updated to {new_status} successfully."}, 200

def get_committee_status(database, account_token, committee_id):
    owner = get_id_from_token(database, account_token)

    if owner == 404:
        return {"error": "Failed to authorize"}, 400

    clear_owner = authorize_token(database, account_token, owner)

    if clear_owner != 200:
        return clear_owner

    try:
        committee_document = database["Committees"].find_one({"id": committee_id, "owner": owner})

        if not committee_document:
            return {"error": "Committee not found or access denied"}, 404

        status = committee_document.get("status", "Not set")
        return {"status": status}, 200

    except Exception as e:
        return {"error": f"Failed to retrieve committee status: {str(e)}"}, 500

def get_status_info(database, account_token, committee_id):
    owner = get_id_from_token(database, account_token)

    if owner == 404:
        return {"error": "Failed to authorize"}, 400

    clear_owner = authorize_token(database, account_token, owner)

    if clear_owner != 200:
        return clear_owner

    try:
        committee_document = database["Committees"].find_one({"id": committee_id, "owner": owner})

        if not committee_document:
            return {"error": "Committee not found or access denied"}, 404

        active_cache = committee_document.get("active_cache", [])

    except Exception as e:
        return {"error": f"Failed to retrieve status: {str(e)}"}, 500

    return {"active_cache": active_cache}, 200

def set_status_info(database, account_token, committee_id, new_active_cache):
    owner = get_id_from_token(database, account_token)

    if owner == 404:
        return {"error": "Failed to authorize"}, 400

    clear_owner = authorize_token(database, account_token, owner)

    if clear_owner != 200:
        return clear_owner

    try:
        committee_document = database["Committees"].find_one({"id": committee_id, "owner": owner})

        if not committee_document:
            return {"error": "Committee not found or access denied"}, 404

        committee_document["active_cache"] = new_active_cache

        result = database["Committees"].update_one(
            {"id": committee_id, "owner": owner},
            {"$set": {"active_cache": new_active_cache}}
        )

        if result.matched_count == 0:
            return {"error": "Failed to update active cache"}, 500

    except Exception as e:
        return {"error": f"Failed to update active cache: {str(e)}"}, 500

    return {"message": "Active cache updated successfully"}, 200

def add_motion(database, account_token, committee_id, motion_type, country, info):
    owner = get_id_from_token(database, account_token)

    if owner == 404:
        return {"error": "Failed to authorize"}, 400

    clear_owner = authorize_token(database, account_token, owner)

    if clear_owner != 200:
        return clear_owner

    valid_motion_types = ["umc", "mc", "rt", "vp", "ssp", "adj", "nai"]

    if motion_type not in valid_motion_types:
        return {"error": f"Invalid motion type {motion_type}. Valid types are {valid_motion_types}."}, 400

    try:
        committee_document = database["Committees"].find_one({"id": committee_id, "owner": owner})

        if not committee_document:
            return {"error": "Committee not found or access denied"}, 404
        
        current_status = committee_document.get("status", "Not set")

        if current_status != "vm":
            return {"error": "Motion can only be added when the committee status is 'vm' (Voting for Motion)."}, 400

        active_cache = committee_document.get("active_cache", {})
        motions = active_cache.get("motions", [])

        motion_index = len(motions)

        motion_document = {
            "motion_id": str(uuid4()),
            "country": country,
            "type": motion_type,
            "information": info,
            "status": "v", 
            "index": motion_index 
        }

        motions.append(motion_document)
        active_cache["motions"] = motions

        database["Committees"].update_one(
            {"id": committee_id, "owner": owner},
            {"$set": {"active_cache": active_cache}}
        )

    except Exception as e:
        return {"error": f"Failed to add motion: {str(e)}"}, 500

    return {"message": "Motion added successfully", "motion": motion_document}, 200

def pass_motion(database, account_token, committee_id, motion_id):
    owner = get_id_from_token(database, account_token)

    if owner == 404:
        return {"error": "Failed to authorize"}, 400

    clear_owner = authorize_token(database, account_token, owner)

    if clear_owner != 200:
        return clear_owner

    try:
        committee_document = database["Committees"].find_one({"id": committee_id, "owner": owner})

        if not committee_document:
            return {"error": "Committee not found or access denied"}, 404

        active_cache = committee_document.get("active_cache", {})
        motions = active_cache.get("motions", [])

        target_motion = next((motion for motion in motions if motion["motion_id"] == motion_id), None)

        if not target_motion:
            return {"error": "Motion not found"}, 404

        for motion in motions:
            if motion["motion_id"] != motion_id:
                motion["status"] = "f"

        target_motion["status"] = "p"

        active_cache["motions"] = motions

        database["Committees"].update_one(
            {"id": committee_id, "owner": owner},
            {"$set": {"active_cache": active_cache}}
        )

        motion_type = target_motion["type"]
        update_committee_status(database, account_token, committee_id, motion_type)

        set_status_info(database, account_token, committee_id, target_motion["information"])

    except Exception as e:
        return {"error": f"Failed to pass motion: {str(e)}"}, 500

    return {"message": "Motion passed successfully, all other motions set to failed."}, 200

def fail_motion(database, account_token, committee_id, motion_id):
    owner = get_id_from_token(database, account_token)

    if owner == 404:
        return {"error": "Failed to authorize"}, 400

    clear_owner = authorize_token(database, account_token, owner)

    if clear_owner != 200:
        return clear_owner

    try:
        committee_document = database["Committees"].find_one({"id": committee_id, "owner": owner})

        if not committee_document:
            return {"error": "Committee not found or access denied"}, 404

        active_cache = committee_document.get("active_cache", {})
        motions = active_cache.get("motions", [])

        target_motion = next((motion for motion in motions if motion["motion_id"] == motion_id), None)

        if not target_motion:
            return {"error": "Motion not found"}, 404

        target_motion["status"] = "f"

        active_cache["motions"] = motions

        database["Committees"].update_one(
            {"id": committee_id, "owner": owner},
            {"$set": {"active_cache": active_cache}}
        )

    except Exception as e:
        return {"error": f"Failed to fail motion: {str(e)}"}, 500

    return {"message": "Motion failed successfully."}, 200