import copy
import time
from selenium.webdriver.common.by import By

from lib import driver, shared

def get_display_name(username, tab=0):
    driver.open_url(values["urls"]["BASE_URL"]+username, tab=tab)
    return driver.drivers[tab].find_element(By.CSS_SELECTOR, driver.classes_to_css_selector(calibrated_driver_values["full_name"])).text.strip()

def save_pfp(username, tab=0):
    driver.open_url(values["urls"]["BASE_URL"]+username, tab=tab)
    pfp = driver.drivers[tab].find_elements(By.CSS_SELECTOR, driver.classes_to_css_selector(calibrated_driver_values["profile_pic"]))[1]
    pfp.screenshot(save_pfp_location+shared.format_file_name(username)+'.png')

def get_friends(username, source, tab=0):
    driver.open_url(values["urls"]["BASE_URL"]+username+get_link_joiner(username)+'sk=friends_all', tab=tab)
    scroll_down_list(tab, args_max_scrolls)
    friends_list = driver.drivers[tab].find_elements(By.CSS_SELECTOR, driver.classes_to_css_selector(calibrated_driver_values["friend_entry"]))
    friends_pfp_list = driver.drivers[tab].find_elements(By.CSS_SELECTOR, driver.classes_to_css_selector(calibrated_driver_values["friend_pfp"]))

    friends = copy.deepcopy(shared.users_db_structure)
    friends["users"] = {username: {source: []}}
    i=0
    for friend in friends_list:
        friend_username = friend.get_attribute("href").split('/')[3]
        friend_full_name = friend.find_element(By.TAG_NAME, 'span').text
        if not args_nopfp:
            try:
                friend_pfp = friends_pfp_list[i]
                friend_pfp.screenshot(save_pfp_location+shared.format_file_name(friend_username)+'.png')
            except IndexError:
                pass

        if friend_username not in friends["users"][username]["friends"]:
            friends["users"][username][source] += [friend_username]
            friends["display_names"][friend_username] = friend_full_name
        i+=1
    return friends

def scroll_down_list(tab, max_scrolls):
    if max_scrolls == 0:
        return

    scroll_down_script = 'window.scrollTo(0, document.body.scrollHeight);'
    scrolls = 0
    src1 = 1
    src2 = 2
    while src1 != src2:
        src1 = driver.drivers[tab].page_source
        driver.drivers[tab].execute_script(scroll_down_script)
        time.sleep(1)
        src2 = driver.drivers[tab].page_source
        scrolls += 1
        if max_scrolls and scrolls >= max_scrolls:
            break

def get_link_joiner(username):
        if 'profile.php?id=' in username:
            return '&'
        else:
            return '?'
