import argparse
import os
import copy
from multiprocessing.pool import ThreadPool

from lib import shared, driver

parser = argparse.ArgumentParser(description='Make a connection graph between friends.')
parser.add_argument('users', help='usernames to scan (separated with spaces)')
parser.add_argument('service', choices=['facebook', 'instagram'], help='select one of available services')
parser.add_argument('--database', '-d', default='Friends', help='database name')
parser.add_argument('--source', '-s', choices=['following', 'followers', 'all'], default='following', help='select one of available options')
parser.add_argument('--depth', '-D', type=int, default=1, help='crawling depth (friends of friends)')
parser.add_argument('--pause', '-p', type=int, default=3, help='seconds to pause after loading a page')
parser.add_argument('--max-scrolls', '-m', type=int, help='maximum number of scrolls down per page')
parser.add_argument('--force', '-f', action='store_true', help='rescan already scanned users')
parser.add_argument('--nopfp', action='store_true', help='do not save profile pictures in database')
parser.add_argument('--blacklist', '-b', help='blacklist usernames')
parser.add_argument('--limit', '-l', type=int, help='limit number of users to scan')
parser.add_argument('--cookies', '-c', default='cookies.pkl', help='use custom cookies file for session')
parser.add_argument('--threads', '-t', type=int, default=1, help='number of threads for scanning')
parser.add_argument('--autosave', '-a', type=int, help='save results every given amount of users scanned')
args = parser.parse_args()

users_scanned = []

def exec_queue(queue, tab):
    display_thread = str(tab+1)
    print(f'In queue (thread {display_thread}): {queue}\n')

    result = copy.deepcopy(shared.users_db_structure)
    i = 0
    for user in queue:
        print(f'Current user: {user} ({str(i+1)}/{str(len(queue))}, thread {display_thread})')

        # handle different services
        try:
            match args.service:
                case "facebook":
                    result_get = driver.Facebook.get_friends(user, tab)
                case "instagram":
                    match args.source:
                        case "following":
                            result_get = driver.Instagram.get_friends(user, "following", tab)
                        case "followers":
                            result_get = driver.Instagram.get_friends(user, "followers", tab)
                        case "all":
                            result_get = driver.Instagram.get_friends(user, "following", tab)
                            result_get = shared.deep_update(result_get, driver.Instagram.get_friends(user, "followers", tab))
        except:
            print(f'Error while scanning user: {user}')
            result_get = {}

        result = shared.deep_update(result, result_get)
        i += 1
    return result

def start_crawling(username, depth):
    try:
        users_db = shared.db_load(args.database)
    except:
        users_db = copy.deepcopy(shared.users_db_structure)

    if username not in users_db["full_names"]:
        match args.service:
            case "facebook":
                username_full_name = driver.Facebook.get_full_name(username, tab=0)
            case "instagram":
                username_full_name = driver.Instagram.get_full_name(username, tab=0)
        users_db["full_names"][username] = username_full_name
    if not args.nopfp and username+'.png' not in os.listdir(db_folder+"images/"):
        match args.service:
            case "facebook":
                username_full_name = driver.Facebook.save_pfp(username, tab=0)
            case "instagram":
                username_full_name = driver.Instagram.save_pfp(username, tab=0)

    # import blacklist
    blacklist = []
    if args.blacklist != None:
        blacklist += args.blacklist.split(" ")
        print(f'Blacklisted users: {blacklist}')

    # import already scanned users
    already_scanned = []
    if not args.force:
        for user in users_db["users"]:
            if user not in already_scanned:
                already_scanned += [user]
        print(f'Already scanned users: {already_scanned}')

    # scanning system
    queue = []
    next_result = copy.deepcopy(shared.users_db_structure)
    if username in already_scanned:
        next_result["users"][username] = copy.deepcopy(users_db["users"][username])
    else:
        queue += [username]
    next_round = []
    global users_scanned
    for depth_index in range(depth):
        print(f'\nCurrent depth: {depth_index+1}')

        for queue_chunk in shared.split_list(queue, args.autosave):
            # divide queue
            queue_divided = {}
            for thread in range(args.threads):
                queue_divided[thread] = []
                for i in range(thread, len(queue_chunk), args.threads):
                    queue_divided[thread] += [queue_chunk[i]]

            # start threads
            thread_pools = {}
            thread_results = {}
            for thread in queue_divided:
                thread_pools[thread] = ThreadPool(processes=1)
                thread_results[thread] = thread_pools[thread].apply_async(exec_queue, (queue_divided[thread], thread))

            # get results from threads
            queue_result = copy.deepcopy(next_result)
            next_result = copy.deepcopy(shared.users_db_structure)
            for thread in thread_results:
                thread_result = thread_results[thread].get()
                queue_result = shared.deep_update(queue_result, thread_result)

            # fix empty full names
            for user in queue_result["full_names"]:
                if queue_result["full_names"][user] == '':
                    queue_result["full_names"][user] = user

            # update users database
            users_db = shared.deep_update(users_db, queue_result)
            for user in queue_result["users"]:
                for x in queue_result["users"][user]:
                    for friend in queue_result["users"][user][x]:
                        if not any(friend in i for i in [queue, users_scanned, next_round, blacklist, already_scanned]):
                            if not args.limit or (args.limit and len(users_scanned)+len(next_round) < args.limit):
                                next_round += [friend]
                        elif friend in already_scanned:
                            next_result["users"][friend] = copy.deepcopy(users_db["users"][friend])
                if user not in users_scanned:
                    users_scanned += [user]

            if args.autosave and queue_chunk != []:
                shared.db_dump(args.database, users_db)
                print("Database saved. (Autosave)")

        queue = next_round
        next_round = []

    if not args.autosave:
        shared.db_dump(args.database, users_db)
        print("Database saved.")

    # print summary
    print(f'\nUsers scanned: {users_scanned} | {len(users_scanned)} users')

print(f'Using {args.database} as database.')
db_folder = shared.user_data_folder+args.database+'/'

# create required folders if not exists
required_folders = [shared.user_data_folder, db_folder, db_folder+"images/"]
for folder in required_folders:
    if not os.path.isdir(folder):
        os.mkdir(folder)

# check service in database
service_file = 'service.txt'
service_file_overwrite = False
if service_file in os.listdir(db_folder):
    with open(db_folder+service_file, 'r') as file:
        if file.read() != args.service:
            if input("Caution! You selected different platform than database has. It might cause mismatch and inconsistency in database. Are you sure you want to continue? [y/n]: ") == 'y':
                service_file_overwrite = True
            else:
                exit()
else:
    service_file_overwrite = True
if service_file_overwrite:
    with open(db_folder+service_file, 'w') as file:
        file.write(args.service)
        file.close()

# import arguments to driver
driver.db_folder = db_folder
driver.args_pause = args.pause
driver.args_max_scrolls = args.max_scrolls
driver.args_service = args.service
driver.args_nopfp = args.nopfp

# prepare browser threads
print("Launching Firefox...")
match args.service:
    case "facebook":
        driver.USER_AGENT_STRING = "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko"
        driver.DEFAULT_URL = 'https://www.facebook.com/'
        driver.BASE_URL = 'https://m.facebook.com/'
    case "instagram":
        driver.USER_AGENT_STRING = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
        driver.DEFAULT_URL = 'https://www.instagram.com/'
        driver.BASE_URL = 'https://www.instagram.com/'
driver.Shared.open_tabs(args.threads, args.cookies)
print("All tabs have been opened.")

# start crawling
print("Starting...")
for user in args.users.split(" "):
    print(f'User: {user} (depth: {args.depth})')
    start_crawling(user, args.depth)

# close browser threads
print("Closing tabs...")
driver.Shared.close_tabs()

print("Finished.")
