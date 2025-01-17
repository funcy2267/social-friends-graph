import json

from lib import shared

import services.facebook.driver
import services.instagram.driver
import services.bluesky.driver

AVAILABLE_SERVICES = ['facebook', 'instagram', 'bluesky']

def set_service(service, mode=None):
    values = json.load(open(f"services/{service}/values.json", "r", encoding="utf-8"))
    if mode == "scan":
        global service_driver
        match service:
            case 'facebook':
                service_driver = services.facebook.driver
            case 'instagram':
                service_driver = services.instagram.driver
            case 'bluesky':
                service_driver = services.bluesky.driver
        service_driver.values = values
        try:
            service_driver.calibrated_driver_values = json.load(open(f"{shared.user_data_folder}/calibrated_driver_values.json", "r", encoding="utf-8"))[service]
        except:
            pass
    return values

def get_display_name(user, tab=0):
    return service_driver.get_display_name(user, tab=tab)

def get_friends(user, source, tab=0):
    if source == "all":
        result_following = service_driver.get_friends(user, "following", tab=tab)
        result_followers = service_driver.get_friends(user, "followers", tab=tab)
        return shared.deep_update(result_following, result_followers)
    else:
        return service_driver.get_friends(user, source, tab=tab)

def save_pfp(user, tab=0):
    service_driver.save_pfp(user, tab=tab)
