import argparse
import pickle
import time
import json
import os
from multiprocessing.pool import ThreadPool
from bs4 import BeautifulSoup
from selenium import webdriver

parser = argparse.ArgumentParser(description='Make a connection graph between friends on Facebook.')
parser.add_argument('--user', '-u', default='profile.php', help='username to start scanning (if not specified, scanning will start from your profile)')
parser.add_argument('--depth', '-d', type=int, default=1, help='crawling depth (friends of friends)')
parser.add_argument('--pause', '-p', type=int, default=1, help='seconds to pause before going to next page')
parser.add_argument('--noscroll', action='store_true', help='do not scroll pages')
parser.add_argument('--fast', '-f', action='store_true', help='add to blacklist users that are already in database')
parser.add_argument('--blacklist', '-b', help='blacklist users (usernames separated with spaces)')
parser.add_argument('--output', '-o', default='Friends/', help='output folder (followed by slash)')
parser.add_argument('--limit', '-l', type=int, help='limit users in queue to scan')
parser.add_argument('--cookies', '-c', default='cookies.pkl', help='use custom cookies file')
parser.add_argument('--threads', '-t', type=int, default=1, help='number of threads')
args = parser.parse_args()

BASE_URL = 'https://m.facebook.com/'
db_index_file = args.output+'db_index.txt'

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

    time.sleep(args.pause)
    return(driver.page_source)

# get full name of user
def get_full_name(username, tab):
    raw_html = open_url(BASE_URL+username, tab)
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
    raw_html = open_url(BASE_URL+username+link_joiner+'v=friends', tab, scroll_down=not args.noscroll)
    content = BeautifulSoup(raw_html, "html.parser").find('div', {"id": "root"})
    page_a = content.find_all('a', href=True)

    banned_usernames = ['home.php', 'buddylist.php', '']
    banned_in_usernames = ['/']
    friends = {}
    i=0
    for a in page_a:
        href = a['href']
        href_username = href[1:]
        username = href_username.split(get_link_joiner(href_username))[0]
        try:
            full_name = page_a[i+1].getText()
        except IndexError:
            pass
        if not any(x for x in [any(x in username for x in banned_in_usernames), any(username == x for x in banned_usernames), username in friends]):
            friends[username] = full_name
        i+=1
    return(friends)

# save friends data in proper format
def save_to_graph(full_name, friends):
    f = open(args.output+full_name+".md", "a", encoding="utf-8")
    for friend in friends:
        try:
            f.write('[['+friends[friend]+']]'+'\n')
        except UnicodeEncodeError:
            pass
    f.close()

def exec_queue(queue, tab):
    print("In queue ["+str(tab+1)+"]:", queue, '\n')
    result = {}
    queue_index = 1
    for user in queue:
        if args.limit != None and queue_index > args.limit:
            print("Limit reached.")
            break
        print("Current user:", user, "(thread "+str(tab+1)+"; "+str(queue_index)+'/'+str(len(queue))+")")
        result[user] = get_friends(user, tab)
        queue_index += 1
    return(result)

def start_crawling(username, depth):
    users_db = {username: get_full_name(username, 0)}
    queue = [username]
    next_round = []
    users_scanned = []

    # depth, thread and queue system
    for current_depth in range(depth):
        print('\n'+"Current depth:", current_depth+1)
        queue_divided = {}
        for thread in range(args.threads):
            queue_divided[thread] = []
            for i in range(thread, len(queue), args.threads):
                queue_divided[thread] += [queue[i]]

        thread_pools = {}
        thread_results = {}
        for thread in queue_divided:
            thread_pools[thread] = ThreadPool(processes=1)
            thread_results[thread] = thread_pools[thread].apply_async(exec_queue, (queue_divided[thread], thread))

        queue_result = {}
        for thread in thread_results:
            queue_result.update(thread_results[thread].get())

        for user in queue_result:
            friends = queue_result[user]
            users_db.update(friends)
            save_to_graph(users_db[user], friends)
            users_scanned += [user]

            for friend in friends:
                if not any(friend in x for x in [queue, users_scanned, next_round, blacklist]):
                    next_round += [friend]

        queue = next_round
        next_round = []

    # update database index
    with open(db_index_file, "a") as f:
        f.write('\n'.join(users_scanned)+'\n')
        f.close()

    # dump users database to json
    json.dump(users_db, open(args.output+'last_users_db.json', "w", encoding="utf-8"))

    # print summary
    print('\n'+"Users scanned:", ", ".join(users_scanned))
    print("Total users scanned:", len(users_scanned))

# import blacklist
blacklist = []
if args.blacklist != None:
    blacklist += args.blacklist.split(" ")
if args.fast == True:
    if os.path.isfile(db_index_file):
        with open(db_index_file, "r") as f:
            for user in f.read().split('\n'):
                if user != '':
                    blacklist += [user]
if blacklist != []:
    print("Blacklisted users:", blacklist)

# create output folder if not exists
if not os.path.isdir(args.output):
    os.mkdir(args.output)

# prepare browser threads
print("Launching Firefox...")
drivers = []
for thread in range(args.threads):
    print("Opening tab", str(thread+1)+'/'+str(args.threads)+"...")
    drivers += [webdriver.Firefox()]
    open_url('https://www.facebook.com', thread)
    cookies = pickle.load(open(args.cookies, "rb"))
    for cookie in cookies:
        drivers[thread].add_cookie(cookie)
print("All tabs have been opened.")

# start crawling
start_crawling(args.user, args.depth)

# close browser threads
for driver in drivers:
    driver.close()
print("Finished.")
