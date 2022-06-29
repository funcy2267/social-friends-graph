import argparse
import pickle
import json
import time
from selenium import webdriver

LOGIN_URL = 'https://www.facebook.com/login'
TFA_URL = 'https://www.facebook.com/checkpoint'

parser = argparse.ArgumentParser(description='Facebook login helper.')
parser.add_argument('--cookies', '-c', default='cookies.pkl', help='use custom cookies file')
args = parser.parse_args()

# open login page
driver = webdriver.Firefox()
driver.get(LOGIN_URL)
print("Login in browser.")

# wait for user to log in
while any(x in driver.current_url for x in [LOGIN_URL, TFA_URL]):
    time.sleep(1)

# save cookies
cookies = driver.get_cookies()
pickle.dump(driver.get_cookies(), open(args.cookies, "wb"))

# close browser
driver.quit()
print("Successfully saved session.")
