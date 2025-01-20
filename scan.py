import argparse
import os
import copy
from multiprocessing.pool import ThreadPool

from lib import shared, driver

import services.handler

parser = argparse.ArgumentParser(description='Connection scanning tool.')
parser.add_argument('users', help='usernames to scan (separated with spaces)')
parser.add_argument('service', choices=services.handler.AVAILABLE_SERVICES, help='select one of available services')
parser.add_argument('database', help='database name')
parser.add_argument('source', choices=['all', 'following', 'followers', 'friends'], help='select one of available sources')
parser.add_argument('--session', '-s', help='session name')
parser.add_argument('--depth', '-D', type=int, default=1, help='crawling depth (friends of friends)')
parser.add_argument('--pause', '-p', type=int, default=3, help='seconds to pause after loading a page')
parser.add_argument('--max-scrolls', '-m', type=int, help='maximum number of scrolls down per page')
parser.add_argument('--manual', '-M', action='store_true', help='in manual mode you have to navigate between pages by yourself')
parser.add_argument('--force', '-f', action='store_true', help='rescan already scanned users')
parser.add_argument('--nopfp', action='store_true', help='do not save profile pictures in database')
parser.add_argument('--blacklist', '-b', help='blacklist usernames to avoid scanning')
parser.add_argument('--limit', '-l', type=int, help='limit number of users to scan')
parser.add_argument('--threads', '-t', type=int, default=1, help='number of threads for scanning')
parser.add_argument('--autosave', '-a', type=int, help='save results every given amount of users scanned')
args = parser.parse_args()

def split_list(l, x):
    if x != None:
        if l != []:
            return [l[i:i+x] for i in range(0, len(l), x)]
        else:
            return [l]
    else:
        return [l]

# execute queue for thread
def exec_queue(queue, tab):
    display_thread = str(tab+1)
    print(f'In queue (thread {display_thread}): {queue}\n')
    result = copy.deepcopy(shared.users_db_structure)
    i = 0
    for user in queue:
        print(f'Current user: {user} ({str(i+1)}/{str(len(queue))}, thread {display_thread})')
        try:
            result_get = services.handler.get_friends(user, args.source, tab=tab)
        except:
            print(f'Error while scanning users friends: {user}')
            result_get = {}
        result = shared.deep_update(result, result_get)
        i += 1
    return result

def start_crawling(username, depth):
    # import database
    try:
        users_db = shared.Database.load(args.database)
    except:
        users_db = copy.deepcopy(shared.users_db_structure)

    # save data about user
    if username not in users_db["display_names"] or args.force==True:
        try:
            users_db["display_names"][username] = services.handler.get_display_name(username)
        except:
            print(f"Error while getting user display name: {username}")
    if not args.nopfp and (username+'.png' not in os.listdir(services.handler.service_driver.save_pfp_location) or args.force==True):
        try:
            services.handler.save_pfp(username)
        except:
            print(f"Error while getting user profile picture: {username}")

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
        for queue_chunk in split_list(queue, args.autosave):
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

            # autosave
            if args.autosave and queue_chunk != []:
                shared.Database.dump(args.database, users_db)
                print("Database saved. (Autosave)")

        queue = next_round
        next_round = []

    if not args.autosave:
        shared.Database.dump(args.database, users_db)
        print("Database saved.")

    # print summary
    print(f'\nUsers scanned: {users_scanned} | {len(users_scanned)} users')

print(f'Using {args.database} as database.')
db_folder = shared.databases_folder+args.database+'/'

# create required folders if not exists
required_folders = [db_folder, db_folder+shared.db_images_folder]
for folder in required_folders:
    if not os.path.isdir(folder):
        os.mkdir(folder)

# check service in database
service_file = 'service.txt'
service_file_overwrite = False
if service_file in os.listdir(db_folder):
    with open(db_folder+service_file, 'r') as file:
        if file.read() != args.service:
            if input("Caution! You selected different service than database has. It might cause mismatch and inconsistency in database. Are you sure you want to continue? [y/n]: ") == 'y':
                service_file_overwrite = True
            else:
                exit()
else:
    service_file_overwrite = True
if service_file_overwrite:
    with open(db_folder+service_file, 'w') as file:
        file.write(args.service)
        file.close()

# prepare scanning
values = services.handler.set_service(args.service, mode="scan")
if args.session:
    print(f'Using {args.session} as session.')
    print("Launching Firefox...")
    driver.open_tabs(args.threads, values["urls"]["DEFAULT_URL"], session=args.session)
    print("All tabs have been opened.")

# import arguments to driver
driver.args_pause = args.pause
driver.args_manual = args.manual
services.handler.service_driver.save_pfp_location = db_folder+shared.db_images_folder
services.handler.service_driver.args_max_scrolls = args.max_scrolls
services.handler.service_driver.args_nopfp = args.nopfp
services.handler.service_driver.args_pause = args.pause

# start crawling
users_scanned = []
print("Starting...")
for user in args.users.split(" "):
    print(f'User: {user} (depth: {args.depth})')
    start_crawling(user, args.depth)

# close browser threads
if args.session:
    print("Closing tabs...")
    driver.close_tabs()

print("Finished.")
