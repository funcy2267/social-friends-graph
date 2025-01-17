import argparse
import time
from urllib.parse import urlparse, urlunparse

from lib import shared, driver

import services.handler

parser = argparse.ArgumentParser(description='Session manager.')
parser.add_argument('service', choices=services.handler.AVAILABLE_SERVICES, help='select one of available services')
parser.add_argument('session', help='session name')
parser.add_argument('--browser', '-b', action='store_true', help='open browser with loaded session')
args = parser.parse_args()

def clean_url(url):
    parsed_url = urlparse(url)
    cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
    while cleaned_url.endswith('/'):
        cleaned_url = cleaned_url[:-1]
    return cleaned_url

values = services.handler.set_service(args.service)

if args.browser:
    driver.open_tabs(1, values["urls"]["DEFAULT_URL"], session=args.session)
    driver.open_url(values["urls"]["DEFAULT_URL"])
    input("Press enter to close browser window.")
    if input("Update cookies file? [y/n]: ") =="y":
        shared.cookies_dump(driver, args.cookies)
        print("Cookies updated.")
    driver.close_tabs()
    exit()

# open login page
driver.open_tabs(1, values["urls"]["LOGIN_URL"])
print("Login in browser.")

# wait for user to log in
while clean_url(driver.drivers[0].current_url) != values["urls"]["LOGIN_END_URL"]:
    time.sleep(1)

# save cookies
driver.Cookies.dump(0, args.session)
print("Successfully saved session.")

driver.close_tabs()
