import pickle
import json
import time
from selenium import webdriver

LOGIN_URL = 'https://www.facebook.com/login'

# open login page
driver = webdriver.Firefox()
driver.get(LOGIN_URL)
print("Login in browser.")

# wait for user to log in
while driver.current_url == LOGIN_URL:
    time.sleep(1)

# save cookies
cookies = driver.get_cookies()
pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))

# close browser
driver.quit()
print("Successfully saved session.")
