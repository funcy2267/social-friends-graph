import argparse
import pickle
import time
import json
import os
from bs4 import BeautifulSoup
from selenium import webdriver

BASE_URL = 'https://m.facebook.com/'

parser = argparse.ArgumentParser(description='Make a connection graph between friends on Facebook.')
parser.add_argument('username', help='username to start with')
parser.add_argument('--depth', '-d', type=int, default=1, help='crawling depth (friends of friends)')
parser.add_argument('--pause', '-p', type=int, default=1, help='seconds to pause before going to next page')
parser.add_argument('--fast', '-f', action='store_true', help='enable fast scanning (do not scroll pages)')
parser.add_argument('--blacklist', '-b', default='blacklist.txt', help='blacklist file to use (usernames separated with newlines)')
parser.add_argument('--output', '-o', default='Friends/', help='output folder (followed by slash)')
parser.add_argument('--limit', '-l', type=int, help='limit users to scan on depth')
parser.add_argument('--cookies', '-c', default='cookies.pkl', help='use custom cookies file')
args = parser.parse_args()

# open url
def open_url(url):
	driver.get(url)
	time.sleep(args.pause)

# get full name from username
def get_full_name(username):
    open_url(BASE_URL+username)
    raw_html = driver.page_source
    content = BeautifulSoup(raw_html, "html.parser").find('h3', {"class": "_6x2x"})
    return(content.prettify().split('\n')[1].strip())

# get list of friends from username
def extract_friends(username):
    if 'profile.php?id=' in username:
        link_joiner = '&'
    else:
        link_joiner = '?'

    open_url(BASE_URL+username+link_joiner+'v=friends')

    if args.fast == False:
        scroll_down()

    raw_html = driver.page_source
    content = BeautifulSoup(raw_html, "html.parser").find('div', {"id": "root"})
    page_a = content.find_all('a', href=True)

    friends = {}
    i=0
    for a in page_a:
        href = a['href']
        username = href[1:]

        try:
            full_name = page_a[i+1].getText()
        except IndexError:
            pass
        
        if not (any(x in username for x in ['home.php', '/']) or username in friends):
            friends[username] = full_name

        i+=1
    return(friends)

# scroll down until page does not change
def scroll_down():
    while True:
        src1 = driver.page_source
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        src2 = driver.page_source

        # check if page source changed
        if src1 == src2:
            break

# save friends data in proper format
def save_to_graph(full_name, friends):
    f = open(args.output+full_name+".md", "a", encoding="utf-8")
    for friend in friends:
        try:
            f.write('[['+friends[friend]+']]'+'\n')
        except UnicodeEncodeError:
            pass
    f.close()

def start_crawling(username, depth):
    users_db = {username: get_full_name(username)}
    queue = [username]
    next_round = []
    users_crawled = []

    # crawling rounds
    for i in range(1, depth+1):
        crawled_i = 0
        for user in queue:
            crawled_i += 1

            # check if the limit has been reached
            if args.limit != None and crawled_i > args.limit:
                break

            # print current progress
            print('\n'+"Current depth:", i)
            print("Current user:", user, "("+users_db[user]+")")
            print("Crawling:", str(crawled_i)+'/'+str(len(queue)))

            # save collected data
            friends = extract_friends(user)
            save_to_graph(users_db[user], friends)
            users_crawled += [user]

            # add user to queue for next round
            for friend in friends:
                users_db[friend] = friends[friend]
                if friend not in (queue, users_crawled, next_round, blacklist):
                    next_round += [friend]

        # update queue
        queue = next_round
        next_round = []

    # dump database to json file
    json.dump(users_db, open("db_dump.json", "w", encoding="utf-8"))

    # print summary
    print('\n'+"Users crawled:", ", ".join(users_crawled))
    print("Total users crawled:", len(users_crawled))

# import blacklist
blacklist = []
if os.path.isfile(args.blacklist):
    blacklist_file = open(args.blacklist, "r")
    for user in blacklist_file.read().split('\n'):
        blacklist += [user]
if blacklist != []:
    print("Blacklisted users:", blacklist)

# create output folder if not exists
if not os.path.isdir(args.output):
    os.mkdir(args.output)

# launch browser
print("Launching Firefox...")
driver = webdriver.Firefox()
open_url('https://www.facebook.com')

# import cookies
cookies = pickle.load(open(args.cookies, "rb"))
for cookie in cookies:
    driver.add_cookie(cookie)

# start crawling
start_crawling(args.username, args.depth)
print("Finished.")

# close browser
driver.close()
