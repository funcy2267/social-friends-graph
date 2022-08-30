import os
import argparse
import json

parser = argparse.ArgumentParser(description='Database management tool.')
parser.add_argument('--database', '-d', default='Friends/', help='database folder (followed by slash)')
parser.add_argument('--generate', '-g', action='store_true', help='generate graph from database')
parser.add_argument('--usernames', '-u', action='store_true', help='use usernames for generating graph')
parser.add_argument('--clean', '-c', action='store_true', help='cleanup database')
parser.add_argument('--merge', '-m', help='destination database to merge')
args = parser.parse_args()

users_db_file_name = 'users_db.json'
users_db = json.load(open(args.database+users_db_file_name, "r", encoding="utf-8"))

if args.generate:
    full_names = users_db["full_names"]
    friends = users_db["friends"]

    for user in friends:
        print("Processing:", user)
        user_friends = friends[user]
        if user_friends != []:
            if not args.usernames:
                user_name = full_names[user]
            else:
                user_name = user
            f = open(args.database+user_name+".md", "a", encoding="utf-8")
            for friend in user_friends:
                if not args.usernames:
                    friend_name = full_names[friend]
                else:
                    friend_name = friend
                f.write('[['+friend_name+']]'+'\n')
            f.close()
    print("Generated graph: "+args.database)

if args.clean:
    files = os.listdir(args.database)
    for f in files:
        if ".md" in f:
            print("Processing:", f)
            f_path = args.database+f
            f_read = open(f_path, "r", encoding="utf-8")
            up_content = set(f_read.readlines())
            up_f = open(f_path, "w", encoding="utf-8")
            up_f.writelines(up_content)
            up_f.close()
    print("Cleaned database: "+args.database)

if args.merge:
    f_dst = args.merge+users_db_file_name
    db_src = users_db
    db_dst = json.load(open(f_dst, "r", encoding="utf-8"))

    db_dst["full_names"] = db_src["full_names"] | db_dst["full_names"]
    for user in db_src["friends"]:
        if user not in db_dst["friends"]:
            db_dst["friends"][user] = []
        for friend in db_src["friends"][user]:
            if friend not in db_dst["friends"][user]:
                db_dst["friends"][user] += [friend]

    json.dump(db_dst, open(f_dst, "w", encoding="utf-8"), indent=2)
    print("Merged database: "+args.database+" => "+args.merge)
