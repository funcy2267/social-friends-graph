import time
import json
import os
import random
import string
import argparse
from selenium.webdriver.common.by import By

from lib import shared, driver
import services.handler

parser = argparse.ArgumentParser(description='Calibration tool for web scraping.')
parser.add_argument('user', help='username to perform calibration on')
parser.add_argument('service', choices=services.handler.AVAILABLE_SERVICES, help='select one of available services')
parser.add_argument('session', help='session name')
args = parser.parse_args()

def generate_random_classname(length):
    start_char = random.choice(string.ascii_lowercase)
    remaining_chars = random.choices(string.ascii_lowercase + string.digits, k=length-1)
    return ''.join([start_char] + remaining_chars)

def get_element(url, xpath=None):
    driver.open_url(url)
    used_driver = driver.drivers[0]
    used_driver.execute_script(f'let classname = "{classname}";'+js_code)
    used_driver.execute_script(f"document.head.insertAdjacentHTML('beforeend', `<style>{css_code.replace(".classname", "."+classname)}</style>`);")

    while used_driver.find_elements(By.CSS_SELECTOR, '.'+classname) == []:
        time.sleep(1)

    element = used_driver.find_element(By.CSS_SELECTOR, f'.{classname}')
    if xpath!=None:
        element = element.find_element(By.XPATH, xpath)
    return element

def get_selected_element_classes(element):
    classes = element.get_attribute("class").split(" ")
    try:
        classes.remove(classname)
        classes.remove(classname+"Fade")
    except:
        pass
    return " ".join(classes)

calibration_assets_folder = 'calibration/'
js_code = open(calibration_assets_folder+"script.js", 'r').read()
css_code = open(calibration_assets_folder+"style.css", 'r').read()

values = services.handler.set_service(args.service)
if "driver" not in values.keys():
    print("This service doesn't support calibration.")
    exit()

calibrated_driver_values = {args.service:{}}
if os.path.exists(shared.user_data_folder+shared.calibrated_driver_values_file):
    shared.deep_update(calibrated_driver_values, json.load(open(shared.user_data_folder+shared.calibrated_driver_values_file, "r", encoding="utf-8")))

# calibration process
input("During calibration, you will be asked to locate and hover over certain elements on the page. Once you hover over an element, wait 5 seconds and it will be selected. Instructions will be displayed in the terminal. Press enter to continue.")
driver.open_tabs(1, values["urls"]["DEFAULT_URL"], session=args.session)
classname = generate_random_classname(10)
for html_element in values["driver"].keys():
    if "xpath_overwrite" in values["driver"][html_element].keys():
        xpath_overwrite = values["driver"][html_element]["xpath_overwrite"]
    else:
        xpath_overwrite = None
    print("Hover:", values["driver"][html_element]["description"])
    element = get_element(values["urls"]["BASE_URL"]+values["driver"][html_element]["location"].replace("example.user", args.user), xpath=xpath_overwrite)
    calibrated_driver_values[args.service][html_element] = get_selected_element_classes(element)
    print("Element selected.")
    time.sleep(3)

# finish
json.dump(calibrated_driver_values, open(shared.user_data_folder+shared.calibrated_driver_values_file, "w", encoding="utf-8"), indent=2)
driver.close_tabs()
print(f"Calibration for service {args.service} successful.")
