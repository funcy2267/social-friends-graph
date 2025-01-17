import copy
import requests
import json

from lib import shared

def get_display_name(username, tab=0):
    response = parse_api_response(values["urls"]["BASE_URL"]+'xrpc/app.bsky.actor.getProfile?actor='+username)
    return response["displayName"]

def save_pfp(username, tab=0):
    response = parse_api_response(values["urls"]["BASE_URL"]+'xrpc/app.bsky.actor.getProfile?actor='+username)
    open(save_pfp_location+username+'.png', 'wb').write(requests.get(response["avatar"]).content)

def get_friends(username, source, tab=0):
    match source:
        case "following":
            api_endpoint = "getFollows"
            api_value = "follows"
        case "followers":
            api_endpoint = "getFollowers"
            api_value = "followers"
    response = parse_api_response(values["urls"]["BASE_URL"]+'xrpc/app.bsky.graph.'+api_endpoint+'?actor='+username)

    friends = copy.deepcopy(shared.users_db_structure)
    friends["users"] = {username: {source: []}}
    i=0
    for friend in response[api_value]:
        friend_username = friend["handle"]
        friend_display_name = friend["displayName"]
        if not args_nopfp:
            open(save_pfp_location+friend_username+'.png', 'wb').write(requests.get(friend["avatar"]).content)

        if friend_username not in friends["users"][username][source]:
            friends["users"][username][source] += [friend_username]
            friends["display_names"][friend_username] = friend_display_name
        i+=1
    return friends

def parse_api_response(url):
    return json.loads(requests.get(url).text)
