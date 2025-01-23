import json
import copy
import re

user_data_folder = 'user_data/'
calibrated_driver_values_file = 'calibrated_driver_values.json'
databases_folder = user_data_folder+'Databases/'
db_images_folder = 'images/'
sessions_folder = user_data_folder+'Sessions/'
users_db_file = 'users_db.json'
users_db_structure = {"display_names": {}, "users": {}, "users_errors": []}

# Recursively merge or update dict-like objects with lists.
def deep_update(d, u):
    for k, v in u.items():
        if isinstance(v, dict) and k in d:
            deep_update(d[k], v)
        elif isinstance(v, list):
            if k not in d:
                d[k] = []
            for x in v:
                if x not in d[k]:
                    d[k] += [x]
        else:
            d[k] = v
    return d

def format_file_name(filename):
    return re.sub(r'[<>:"/\\|?*]', '', filename)

class Database:
    def format_graph(users_db):
        merge_db = copy.deepcopy(users_db_structure)
        relations = {"friends": "friends", "following": "followers", "followers": "following"}
        for user in users_db["users"]:
            for k, v in relations.items():
                if k in users_db["users"][user]:
                    for friend in users_db["users"][user][k]:
                        merge_db = deep_update(merge_db, {"users": {friend: {v: [user]}}})
        return deep_update(users_db, merge_db)

    def dump(database, users_db):
        json.dump(users_db, open(databases_folder+database+'/'+users_db_file, "w", encoding="utf-8"), indent=2)

    def load(database):
        return json.load(open(databases_folder+database+'/'+users_db_file, "r", encoding="utf-8"))
