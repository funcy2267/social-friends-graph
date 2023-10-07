import pickle
import time
from bs4 import BeautifulSoup
from selenium import webdriver

FB_BASE_URL = 'https://m.facebook.com/'
USER_AGENT_STRING = "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko"

# open url
def open_url(url, tab, scroll_down=False):
    driver = drivers[tab]
    driver.get(url)

    if scroll_down == True:
        while True:
            src1 = driver.page_source
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            src2 = driver.page_source
            if src1 == src2:
                break

    time.sleep(args_pause)
    return(driver.page_source)

# get full name of user
def get_full_name(username, tab):
    raw_html = open_url(FB_BASE_URL+username, tab)
    content = BeautifulSoup(raw_html, "html.parser").find('h3', {"class": "_6x2x"})
    return(content.prettify().split('\n')[1].strip())

def get_link_joiner(username):
    link_joiners = ['?', '&']
    if 'profile.php?id=' in username:
        link_joiner = link_joiners[1]
    else:
        link_joiner = link_joiners[0]
    return(link_joiner)

# get list of friends from user
def get_friends(username, tab):
    link_joiner = get_link_joiner(username)
    raw_html = open_url(FB_BASE_URL+username+link_joiner+'v=friends', tab, scroll_down=not args_noscroll)
    content = BeautifulSoup(raw_html, "html.parser").find('div', {"id": "root"})
    page_a = content.find_all('a', href=True)

    banned_usernames = ['home.php', 'buddylist.php', '']
    banned_in_usernames = ['/']
    friends = {"full_names": {}, "friends": {username: []}}
    i=0
    for a in page_a:
        href = a['href']
        href_username = href[1:]
        friend_username = href_username.split(get_link_joiner(href_username))[0]
        try:
            friend_full_name = page_a[i+1].getText()
        except IndexError:
            pass
        if not any(x for x in [any(x in friend_username for x in banned_in_usernames), any(friend_username == x for x in banned_usernames), friend_username in friends["friends"][username]]):
            friends["friends"][username] += [friend_username]
            friends["full_names"][friend_username] = friend_full_name
        i+=1
    return(friends)

def open_tabs(threads, cookies_file):
    global drivers
    drivers = []
    fprofile = webdriver.FirefoxProfile()
    fprofile.set_preference("general.useragent.override", USER_AGENT_STRING)
    for thread in range(threads):
        print("Opening tab", str(thread+1)+'/'+str(threads)+"...")
        drivers += [webdriver.Firefox(fprofile)]
        open_url('https://www.facebook.com', thread)
        cookies = pickle.load(open(cookies_file, "rb"))
        for cookie in cookies:
            drivers[thread].add_cookie(cookie)

def close_tabs():
    for x in drivers:
        x.close()
