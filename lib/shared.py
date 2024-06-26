import json
import copy
import pickle
from urllib.parse import urlparse, urlunparse

user_data_folder = 'user_data/'
users_db_file = 'users_db.json'
users_db_structure = {"full_names": {}, "users": {}}

def deep_update(d, u):
    # Recursively merge or update dict-like objects with lists.
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

def split_list(l, x):
    if x != None:
        if l != []:
            return [l[i:i+x] for i in range(0, len(l), x)]
        else:
            return [l]
    else:
        return [l]

def clean_url(url):
    parsed_url = urlparse(url)
    cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
    while cleaned_url.endswith('/'):
        cleaned_url = cleaned_url[:-1]
    return cleaned_url

def db_dump(database, users_db):
    json.dump(users_db, open(user_data_folder+database+'/'+users_db_file, "w", encoding="utf-8"), indent=2)

def db_load(database):
    return json.load(open(user_data_folder+database+'/'+users_db_file, "r", encoding="utf-8"))

def cookies_dump(driver, cookies_file):
    pickle.dump(driver.get_cookies(), open(cookies_file, "wb"))

def cookies_load(driver, cookies_file):
    cookies = pickle.load(open(cookies_file, "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)

def db_format_graph(users_db):
    merge_db = copy.deepcopy(users_db_structure)
    relations = {"friends": "friends", "following": "followers", "followers": "following"}
    for user in users_db["users"]:
        for k, v in relations.items():
            if k in users_db["users"][user]:
                for friend in users_db["users"][user][k]:
                    merge_db = deep_update(merge_db, {"users": {friend: {v: [user]}}})
    return deep_update(users_db, merge_db)
