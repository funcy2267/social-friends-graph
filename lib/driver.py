import time
import copy
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

from lib import shared

driver_helper = json.load(open("lib/driver_helper.json", "r", encoding="utf-8"))

drivers = []

class Shared:
    def open_url(url, tab):
        driver = drivers[tab]
        driver.get(url)
        time.sleep(args_pause)

        return driver.page_source

    def open_tabs(threads, cookies_file):
        global drivers
        fprofile = webdriver.FirefoxProfile()
        fprofile.set_preference("general.useragent.override", USER_AGENT_STRING)
        for thread in range(threads):
            print(f'Opening tab {str(thread+1)}/{str(threads)}...')
            drivers += [webdriver.Firefox(fprofile)]
            Shared.open_url(DEFAULT_URL, thread)
            shared.cookies_load(drivers[thread], cookies_file)

    def scroll_down_list(tab, max_scrolls):
        if max_scrolls == 0:
            return
        driver = drivers[tab]
        match args_service:
            case "facebook":
                scroll_down_script = 'window.scrollTo(0, document.body.scrollHeight);'
            case "instagram":
                scroll_down_script = 'var container = document.getElementsByClassName("{friends_list}")[0]; container.scrollTop = container.scrollHeight;'.format(friends_list = driver_helper["instagram"]["friends_list"])
        scrolls = 0
        src1 = 1
        src2 = 2
        while src1 != src2:
            src1 = driver.page_source
            driver.execute_script(scroll_down_script)
            time.sleep(1)
            src2 = driver.page_source
            scrolls += 1
            if max_scrolls and scrolls >= max_scrolls:
                break

    def close_tabs():
        for driver in drivers:
            driver.quit()

class Facebook:
    # get full name of user
    def get_full_name(username, tab=None, page_src=None):
        try:
            if page_src == None:
                raw_html = Shared.open_url(BASE_URL+username, tab)
                content = BeautifulSoup(raw_html, "html.parser").find('h3', {"class": driver_helper["facebook"]["full_name_content"]})
                full_name = content.prettify().split('\n')[1].strip()
            else:
                full_name = page_src[0][page_src[1]].getText()
        except:
            full_name = ''
        if full_name == '':
            full_name = username
        return full_name

    def save_pfp(username, tab=None, page_src=None):
        try:
            if page_src == None:
                Shared.open_url(BASE_URL+username, tab)
                pfp = drivers[tab].find_element(By.CLASS_NAME, driver_helper["facebook"]["profile_pic"])
            else:
                pfp = page_src[0][page_src[1]]
            pfp.screenshot(db_folder+'images/'+username+'.png')
        except:
            pass

    def get_link_joiner(username):
        if 'profile.php?id=' in username:
            return '&'
        else:
            return '?'

    # get list of friends from user
    def get_friends(username, tab):
        link_joiner = Facebook.get_link_joiner(username)
        Shared.open_url(BASE_URL+username+link_joiner+'v=friends', tab)
        Shared.scroll_down_list(tab, args_max_scrolls)
        raw_html = drivers[tab].page_source
        content = BeautifulSoup(raw_html, "html.parser").find('div', {"id": driver_helper["facebook"]["friends_list_content"]})
        page_div = content.find_all('div', {"class": driver_helper["facebook"]["friends_list_page_div"]})
        page_a = []
        for div in page_div:
            page_a += [div.find('a', href=True)]
        page_i = drivers[tab].find_elements(By.CLASS_NAME, driver_helper["facebook"]["profile_pic"])

        banned_usernames = ['home.php', 'buddylist.php', '']
        banned_in_usernames = ['/']
        friends = copy.deepcopy(shared.users_db_structure)
        friends["users"] = {username: {"friends": []}}
        i=0
        for a in page_a:
            href = a['href']
            href_username = href[1:]
            friend_username = href_username.split(Facebook.get_link_joiner(href_username))[0]
            friend_full_name = Facebook.get_full_name(friend_username, page_src=[page_a, i])
            if not args_nopfp:
                Facebook.save_pfp(friend_username, page_src=[page_i, i])

            if not any(x for x in [any(x in friend_username for x in banned_in_usernames), any(friend_username == x for x in banned_usernames), friend_username in friends["users"][username]["friends"]]):
                friends["users"][username]["friends"] += [friend_username]
                friends["full_names"][friend_username] = friend_full_name
            i+=1
        return friends

class Instagram:
    # get full name of user
    def get_full_name(username, tab=None, page_src=None):
        try:
            if page_src == None:
                raw_html = Shared.open_url(BASE_URL+username, tab)
                content = BeautifulSoup(raw_html, "html.parser").find('span', {"class": driver_helper["instagram"]["full_name_content_1"]})
                full_name = content.prettify().split('\n')[1].strip()
            else:
                full_name = page_src[0][page_src[1]].find('span', {"class": driver_helper["instagram"]["full_name_content_2"]}).get_text()
        except:
            full_name = ''
        if full_name == '':
            full_name = username
        return full_name

    def save_pfp(username, tab=None, page_src=None):
        try:
            if page_src == None:
                Shared.open_url(BASE_URL+username, tab)
                pfp = drivers[tab].find_elements(By.CSS_SELECTOR, driver_helper["instagram"]["profile_pic"])[1]
            else:
                pfp = page_src[0][page_src[1]]
            pfp.screenshot(db_folder+'images/'+username+'.png')
        except:
            pass

    # get list of friends from user
    def get_friends(username, source, tab):
        Shared.open_url(BASE_URL+username, tab)
        match source:
            case "following":
                source_button = 1
            case "followers":
                source_button = 0
        drivers[tab].find_elements(By.CSS_SELECTOR, driver_helper["instagram"]["show_list"])[source_button].click()
        time.sleep(args_pause)
        Shared.scroll_down_list(tab, args_max_scrolls)
        raw_html = drivers[tab].page_source
        content = BeautifulSoup(raw_html, "html.parser").find('div', {"class": driver_helper["instagram"]["friends_list"]})
        page_div = content.find('div')
        page_span = page_div.find_all('span', {"class": driver_helper["instagram"]["friends_list_page_span_1"]})
        page_span2 = page_div.find_all('span', {"class": driver_helper["instagram"]["friends_list_page_span_2"]})
        page_img = drivers[tab].find_elements(By.CLASS_NAME, driver_helper["instagram"]["page_img"])

        friends = copy.deepcopy(shared.users_db_structure)
        friends["users"] = {username: {source: []}}
        i=0
        for span in page_span:
            friend_username = span.get_text()
            friend_full_name = Instagram.get_full_name(friend_username, page_src=[page_span2, i])
            if not args_nopfp:
                Instagram.save_pfp(friend_username, page_src=[page_img, i])

            if friend_username not in friends["users"][username][source]:
                friends["users"][username][source] += [friend_username]
                friends["full_names"][friend_username] = friend_full_name
            i+=1
        return friends
