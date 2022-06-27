from selenium import webdriver
import pickle
import json
import time

driver = webdriver.Firefox()
driver.get("https://www.facebook.com")
print("Login in browser.")

# wait for user to log in
while driver.current_url != "https://www.facebook.com/?sk=welcome":
    time.sleep(1)

# save cookies
cookies = driver.get_cookies()
pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))

driver.quit()
print("Successfully saved session.")
