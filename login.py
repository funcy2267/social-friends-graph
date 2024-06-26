import argparse
import time
from selenium import webdriver

from lib import shared

parser = argparse.ArgumentParser(description='Session manager.')
parser.add_argument('service', choices=['facebook', 'instagram'], help='select one of available services')
parser.add_argument('--cookies', '-c', default='cookies.pkl', help='use custom cookies file for session')
parser.add_argument('--browser', '-b', action='store_true', help='open browser with loaded session')
args = parser.parse_args()

match args.service:
    case "facebook":
        DEFAULT_URL = 'https://www.facebook.com'
        LOGIN_URL = 'https://www.facebook.com/login'
        END_URL = 'https://www.facebook.com'
    case "instagram":
        DEFAULT_URL = 'https://www.instagram.com'
        LOGIN_URL = 'https://www.instagram.com/accounts/login'
        END_URL = 'https://www.instagram.com'

driver = webdriver.Firefox()
if not args.browser:
    # open login page
    driver.get(LOGIN_URL)
    print("Login in browser.")

    # wait for user to log in
    while shared.clean_url(driver.current_url) != END_URL:
        time.sleep(1)

    # save cookies
    shared.cookies_dump(driver, args.cookies)
    print("Successfully saved session.")
else:
    driver.get(DEFAULT_URL)
    shared.cookies_load(driver, args.cookies)
    driver.get(DEFAULT_URL)
    input("Press enter to close browser window.")
    if input("Update cookies file? [y/n]") =="y":
        shared.cookies_dump(driver, args.cookies)
        print("Cookies updated.")
driver.quit()
