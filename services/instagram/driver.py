import copy
import time
from selenium.webdriver.common.by import By

from lib import driver, shared

def get_display_name(username, tab=0):
    driver.open_url(values["urls"]["BASE_URL"]+username, tab=tab)
    return driver.drivers[tab].find_element(By.CSS_SELECTOR, driver.classes_to_css_selector(calibrated_driver_values["full_name"])).text

def save_pfp(username, tab=0):
    driver.open_url(values["urls"]["BASE_URL"]+username, tab=tab)
    pfp = driver.drivers[tab].find_elements(By.CSS_SELECTOR, driver.classes_to_css_selector(calibrated_driver_values["profile_pic"]))[0]
    pfp.screenshot(save_pfp_location+username+'.png')

def get_friends(username, source, tab=0):
    driver.open_url(values["urls"]["BASE_URL"]+username, tab=tab)
    match source:
        case "following":
            source_button = 1
        case "followers":
            source_button = 0
    driver.drivers[tab].find_elements(By.CSS_SELECTOR, driver.classes_to_css_selector(calibrated_driver_values["show_list"]))[source_button].click()
    time.sleep(args_pause)
    scroll_down_list(tab, args_max_scrolls)
    friends_list_element = driver.drivers[tab].find_elements(By.CSS_SELECTOR, driver.classes_to_css_selector(calibrated_driver_values["friend_handle"]))[0].find_element(By.XPATH, '../../../../../../../../../../../../../../../../..')
    if friends_list_element.find_elements(By.XPATH, "./div")[-1].get_attribute('class') != '':
        driver.drivers[tab].execute_script("arguments[0].innerHTML = '';", friends_list_element.find_elements(By.XPATH, "./div")[-2])
    time.sleep(args_pause)
    friends_list = driver.drivers[tab].find_elements(By.CSS_SELECTOR, driver.classes_to_css_selector(calibrated_driver_values["friend_handle"]))
    friends_display_name_list = driver.drivers[tab].find_elements(By.CSS_SELECTOR, driver.classes_to_css_selector(calibrated_driver_values["friend_display_name"]))
    friends_pfp_list = driver.drivers[tab].find_elements(By.CSS_SELECTOR, driver.classes_to_css_selector(calibrated_driver_values["friend_pfp"]))

    friends = copy.deepcopy(shared.users_db_structure)
    friends["users"] = {username: {source: []}}
    i=0
    for friend in friends_list:
        friend_username = friend.text
        friend_display_name = friends_display_name_list[i].find_element(By.TAG_NAME, 'span').text
        if not args_nopfp:
            try:
                friend_pfp = friends_pfp_list[i+2]
                friend_pfp.screenshot(save_pfp_location+friend_username+'.png')
            except IndexError:
                pass

        if friend_username not in friends["users"][username][source]:
            friends["users"][username][source] += [friend_username]
            friends["display_names"][friend_username] = friend_display_name
        i+=1
    return friends

def scroll_down_list(tab, max_scrolls):
    if max_scrolls == 0:
        return
    friends_list = driver.drivers[tab].find_elements(By.CSS_SELECTOR, driver.classes_to_css_selector(calibrated_driver_values["friend_handle"]))[0].find_element(By.XPATH, '../../../../../../../../../../../../../../../../..')
    scroll_down_script = f'var container = document.getElementsByClassName("{friends_list.get_attribute("class")}")[0]; container.scrollTop = container.scrollHeight;'
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
