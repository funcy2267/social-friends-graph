import time
import copy
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

from lib import shared

drivers = []

class Shared:
    def open_url(url, tab, max_scrolls=0):
        driver = drivers[tab]
        driver.get(url)
        time.sleep(args_pause)

        if max_scrolls != 0:
            Shared.scroll_down_list(tab, max_scrolls)

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
        driver = drivers[tab]
        match args_service:
            case "facebook":
                scroll_down_script = 'window.scrollTo(0, document.body.scrollHeight);'
            case "instagram":
                scroll_down_script = 'var container = document.getElementsByClassName("_aano")[0]; container.scrollTop = container.scrollHeight;'
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
                content = BeautifulSoup(raw_html, "html.parser").find('h3', {"class": "_6x2x"})
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
                pfp = drivers[tab].find_element(By.CLASS_NAME, "profpic")
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
        raw_html = Shared.open_url(BASE_URL+username+link_joiner+'v=friends', tab, max_scrolls=args_max_scrolls)
        content = BeautifulSoup(raw_html, "html.parser").find('div', {"id": "root"})
        page_div = content.find_all('div', {"class": "_84l2"})
        page_a = []
        for div in page_div:
            page_a += [div.find('a', href=True)]
        page_i = drivers[tab].find_elements(By.CLASS_NAME, "profpic")

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
                content = BeautifulSoup(raw_html, "html.parser").find('span', {"class": "x1lliihq x1plvlek xryxfnj x1n2onr6 x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1i0vuye xvs91rp x1s688f x5n08af x10wh9bi x1wdrske x8viiok x18hxmgj"})
                full_name = content.prettify().split('\n')[1].strip()
            else:
                full_name = page_src[0][page_src[1]].find('span', {"class": "x1lliihq x193iq5w x6ikm8r x10wlt62 xlyipyv xuxw1ft"}).get_text()
        except:
            full_name = ''
        if full_name == '':
            full_name = username
        return full_name

    def save_pfp(username, tab=None, page_src=None):
        try:
            if page_src == None:
                Shared.open_url(BASE_URL+username, tab)
                pfp = drivers[tab].find_elements(By.CSS_SELECTOR, ".xpdipgo.x972fbf.xcfux6l.x1qhh985.xm0m39n.xk390pu.x5yr21d.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xl1xv1r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x11njtxf.xh8yej3")[1]
            else:
                pfp = page_src[0][page_src[1]]
            pfp.screenshot(db_folder+'images/'+username+'.png')
        except:
            pass

    # get list of friends from user
    def get_friends(username, source, tab):
        raw_html = Shared.open_url(BASE_URL+username+'/'+source, tab, max_scrolls=args_max_scrolls)
        content = BeautifulSoup(raw_html, "html.parser").find('div', {"class": "_aano"})
        page_div = content.find('div')
        page_span = page_div.find_all('span', {"class": "_ap3a _aaco _aacw _aacx _aad7 _aade"})
        page_span2 = page_div.find_all('span', {"class": "x1lliihq x1plvlek xryxfnj x1n2onr6 x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1i0vuye xvs91rp xo1l8bm x1roi4f4 x10wh9bi x1wdrske x8viiok x18hxmgj"})
        page_img = drivers[tab].find_elements(By.CLASS_NAME, "_aarf")

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
