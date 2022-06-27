import argparse
import pickle
import time
import json
import os
from bs4 import BeautifulSoup
from selenium import webdriver

# parse arguments
parser = argparse.ArgumentParser(description='Make a connection graph between friends on Facebook.')
parser.add_argument('username', help='username to start with')
parser.add_argument('--depth', '-d', type=int, default=1, help='crawling depth (friends of friends)')
parser.add_argument('--pause', '-p', type=int, default=1, help='seconds to pause between scans')
parser.add_argument('--fast', '-f', action="store_true", help='enable fast scanning (do not scroll pages)')
parser.add_argument('--blacklist', '-b', default='blacklist.txt', help='blacklist file to use (usernames separated with newlines)')
parser.add_argument('--output', '-o', default='Friends/', help='output folder (followed by slash)')
args = parser.parse_args()

# define functions
def get_full_name(username):
    driver.get('https://m.facebook.com/'+username)
    time.sleep(args.pause)
    raw_html = driver.page_source
    content = BeautifulSoup(raw_html, "html.parser").find('h3', {"class": "_6x2x"})
    return(content.prettify().split('\n')[1].strip())

def extract_friends(username):
    driver.get('https://m.facebook.com/'+username+'?v=friends')
    time.sleep(args.pause)
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
        if not ('home.php' in username or '/' in username or username in friends):
            friends[username] = full_name
        i+=1
    return(friends)

def scroll_down():
    while True:
        src1 = driver.page_source
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        src2 = driver.page_source
        if src1 == src2:
            break

def start_crawling(username, depth):
    users_db = {username: get_full_name(username)}
    queue = [username]
    next_round = []
    users_crawled = []

    for i in range(depth):
        crawled_i = 0
        for user in queue:
            crawled_i += 1

            # print current progress
            print('\n'+"Current depth: "+str(i))
            print("Current user: "+user+" ("+users_db[user]+")")
            print("Crawling: "+str(crawled_i)+'/'+str(len(queue)))

            friends = extract_friends(user)
            save_to_graph(users_db[user], friends)
            users_crawled += [user]

            # add user to queue for next round/depth
            for friend in friends:
                users_db[friend] = friends[friend]
                if not (friend in queue or friend in users_crawled or friend in next_round or friend in blacklist):
                    next_round += [friend]
        
        queue = next_round
        next_round = []
    
    json.dump(users_db, open("db_dump.json", "w", encoding="utf-8"))

def save_to_graph(full_name, friends):
    for friend in friends:
        try:
            f = open(args.output+full_name+".md", "a", encoding="utf-8")
            f.write('[['+friends[friend]+']]'+'\n')
            f.close()
        except UnicodeEncodeError:
            pass

# get blacklist
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

print("Launching Firefox...")

# import cookies
driver = webdriver.Firefox()
driver.get("https://www.facebook.com")
cookies = pickle.load(open("cookies.pkl", "rb"))
for cookie in cookies:
    driver.add_cookie(cookie)

# start crawling
start_crawling(args.username, args.depth)
driver.close()
