import time
import pickle
from selenium import webdriver

from lib import shared

drivers = []

def open_url(url, tab):
    driver = drivers[tab]
    try:
        if args_manual == False:
            driver.get(url)
        else:
            print("Navigate to URL: "+url)
            while driver.current_url != url:
                time.sleep(1)
    except:
        driver.get(url)
    try:
        if args_pause!=0:
            time.sleep(args_pause)
    except:
        pass
    return driver.page_source

def open_tabs(threads, url, session=None):
    global drivers
    for thread in range(threads):
        print(f'Opening tab {str(thread+1)}/{str(threads)}...')
        drivers += [webdriver.Firefox()]
        open_url(url, thread)
        if session != None:
            Cookies.load(thread, session)

def classes_to_css_selector(classes):
    return '.'+classes.replace(' ', '.')

def close_tabs():
    for driver in drivers:
        driver.quit()

class Cookies:
    def dump(tab, session):
        pickle.dump(drivers[tab].get_cookies(), open(shared.sessions_folder+session+".pkl", "wb"))

    def load(tab, session):
        cookies = pickle.load(open(shared.sessions_folder+session+".pkl", "rb"))
        for cookie in cookies:
            drivers[tab].add_cookie(cookie)
