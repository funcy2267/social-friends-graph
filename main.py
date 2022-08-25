import argparse
import json
import os
import driver
from multiprocessing.pool import ThreadPool

parser = argparse.ArgumentParser(description='Make a connection graph between friends on Facebook.')
parser.add_argument('--user', '-u', default='profile.php', help='username to start scanning (if not specified, scanning will start from your profile)')
parser.add_argument('--depth', '-d', type=int, default=1, help='crawling depth (friends of friends)')
parser.add_argument('--pause', '-p', type=int, default=1, help='seconds to pause before going to next page')
parser.add_argument('--noscroll', '-n', action='store_true', help='do not scroll pages')
parser.add_argument('--force', '-f', action='store_true', help='rescan already scanned users')
parser.add_argument('--blacklist', '-b', help='blacklist users (usernames separated with spaces)')
parser.add_argument('--output', '-o', default='Friends/', help='output folder (followed by slash)')
parser.add_argument('--limit', '-l', type=int, help='limit users in queue to scan')
parser.add_argument('--cookies', '-c', default='cookies.pkl', help='use custom cookies file')
parser.add_argument('--threads', '-t', type=int, default=1, help='number of threads')
parser.add_argument('--autosave', '-a', action='store_true', help='save results on every depth')
args = parser.parse_args()

users_db_file = args.output+'users_db.json'

def dump_db(users_db):
    print("Saving database...")
    json.dump(users_db, open(users_db_file, "w", encoding="utf-8"), indent=2)

def exec_queue(queue, tab):
    display_thread = str(tab+1)
    print("In queue (thread "+display_thread+"):", queue, '\n')

    result = {"full_names": {}, "friends": {}}
    queue_index = 1
    for user in queue:
        if args.limit != None and queue_index > args.limit:
            print("Limit reached.")
            break

        print("Current user:", user, "(thread "+display_thread+", "+str(queue_index)+'/'+str(len(queue))+")")
        result_get = driver.get_friends(user, tab)
        for x in ["friends", "full_names"]:
            result[x].update(result_get[x])

        queue_index += 1
    return(result)

def start_crawling(username, depth):
    if os.path.isfile(users_db_file):
        users_db = json.load(open(users_db_file, "r", encoding="utf-8"))
    else:
        users_db = {"full_names": {}, "friends": {}}

    if username not in users_db["full_names"]:
        users_db["full_names"][username] = driver.get_full_name(username, 0)

    # import blacklist
    blacklist = []
    if args.blacklist != None:
        blacklist += args.blacklist.split(" ")
        print("Blacklisted users:", blacklist)

    # import already scanned users
    already_scanned = []
    if not args.force:
        already_scanned += list(users_db["friends"])
        print("Already scanned users:", already_scanned)

    # scanning system
    queue = [username]
    next_round = []
    users_scanned = []
    next_result = {"full_names": {}, "friends": {}}
    for depth_index in range(depth):
        display_depth = str(depth_index+1)
        print('\n'+"Current depth:", display_depth)

        # divide queue
        queue_divided = {}
        for thread in range(args.threads):
            queue_divided[thread] = []
            for i in range(thread, len(queue), args.threads):
                queue_divided[thread] += [queue[i]]

        # start threads
        thread_pools = {}
        thread_results = {}
        for thread in queue_divided:
            thread_pools[thread] = ThreadPool(processes=1)
            thread_results[thread] = thread_pools[thread].apply_async(exec_queue, (queue_divided[thread], thread))

        # get results from threads
        queue_result = next_result
        next_result = {"full_names": {}, "friends": {}}
        for thread in thread_results:
            thread_result = thread_results[thread].get()
            for x in ["friends", "full_names"]:
                queue_result[x].update(thread_result[x])

        # update users database
        users_db["full_names"].update(queue_result["full_names"])
        for user in queue_result["friends"]:
            friends = queue_result["friends"][user]

            if user not in users_scanned:
                users_scanned += [user]

            if user == username and user in already_scanned:
                for friend in users_db["friends"][user]:
                    if friend not in queue_result["friends"][user]:
                        queue_result["friends"][user] += [friend]

            if user not in users_db["friends"]:
                users_db["friends"][user] = []
            for friend in friends:
                if friend not in users_db["friends"][user]:
                    users_db["friends"][user] += [friend]
                if not any(friend in x for x in [queue, users_scanned, next_round, blacklist, already_scanned]):
                    next_round += [friend]
                elif friend in already_scanned:
                    next_result["friends"][friend] = users_db["friends"][friend]

        if args.autosave:
            dump_db(users_db)

        queue = next_round
        next_round = []

    if not args.autosave:
        dump_db(users_db)

    # print summary
    print('\n'+"Users scanned:", ", ".join(users_scanned))
    print("Total users scanned:", len(users_scanned))

print("Using "+args.output+" as database.")
# create output folder if not exists
if not os.path.isdir(args.output):
    os.mkdir(args.output)

# import arguments to driver
driver.args_pause = args.pause
driver.args_noscroll = args.noscroll

# prepare browser threads
print("Launching Firefox...")
driver.open_tabs(args.threads, args.cookies)
print("All tabs have been opened.")

# start crawling
print("Starting...")
start_crawling(args.user, args.depth)

# close browser threads
print("Closing tabs...")
driver.close_tabs()

print("Finished.")
