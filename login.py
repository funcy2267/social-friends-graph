import pickle
import json
import time
from selenium import webdriver

# open login page
driver = webdriver.Firefox()
driver.get("https://www.facebook.com/login")
print("Login in browser.")

# wait for user to log in
while driver.current_url != "https://www.facebook.com/?sk=welcome":
    time.sleep(1)

# save cookies
cookies = driver.get_cookies()
pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))

# close browser
driver.quit()
print("Successfully saved session.")
