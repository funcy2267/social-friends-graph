import os
import argparse
import json

parser = argparse.ArgumentParser(description='Database management tool.')
parser.add_argument('--database', '-d', default='Friends/', help='database folder (followed by slash)')
parser.add_argument('--generate', '-g', action='store_true', help='generate graph from database')
parser.add_argument('--clean', '-c', action='store_true', help='cleanup database')
parser.add_argument('--merge', '-m', help='destination database to merge')
args = parser.parse_args()

if args.generate:
    users_db = json.load(open(args.database+"users_db.json", "r", encoding="utf-8"))

    full_names = users_db["full_names"]
    friends = users_db["friends"]

    for user in friends:
        print("Processing:", user)
        user_friends = friends[user]
        if user_friends != []:
            f = open(args.database+full_names[user]+".md", "a", encoding="utf-8")
            for friend in user_friends:
                f.write('[['+full_names[friend]+']]'+'\n')
            f.close()

if args.clean:
    files = os.listdir(args.database)
    for f in files:
        if ".md" in f:
            print("Processing:", f)
            f_path = args.database+f
            up_content = set(open(f_path).readlines())
            up_f = open(f_path, 'w')
            up_f.writelines(up_content)
            up_f.close()

if args.merge:
    f_src = args.database+"users_db.json"
    f_dst = args.merge+"users_db.json"
    db_src = json.load(open(f_src, "r", encoding="utf-8"))
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
