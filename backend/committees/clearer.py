from re import compile, escape
from uuid import uuid4

name_regex = compile(r"[^a-zA-Z0-9_]")

def clear_id(database, id):
    Committees = database["Committees"]
    id = str(id)

    while len(list(Committees.find({"id":id}))) != 0:
        print("WARNING WARNING: Requested ID is found | IDS LIKELY RUNNING OUT")
        id = uuid4()

    return str(id)

def clear_name(database, name):
    if name_regex.search(name.lower()):
        return {"error": "Bad Committee Name"}, 400

    return 200
