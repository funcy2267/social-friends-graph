import os
import argparse
import re

from lib import shared

parser = argparse.ArgumentParser(description='Database management tool.')
parser.add_argument('--database', '-d', default='Friends', help='database name')
parser.add_argument('--generate', '-g', action='store_true', help='generate graph from database')
parser.add_argument('--cleanup', '-c', action='store_true', help='remove markdown files from database')
parser.add_argument('--usernames', '-u', action='store_true', help='use usernames instead of full names for generating graph')
parser.add_argument('--query', '-q', help='execute query on database (keys separated with spaces)')
parser.add_argument('--merge', '-m', help='source database to merge')
args = parser.parse_args()

db_folder = shared.user_data_folder+args.database+'/'
users_db = shared.db_load(args.database)

def get_graph_name(user):
    if not args.usernames:
        return re.sub(r'[<>:"/\\|?*]', '', users_db["full_names"][user])
    else:
        return user

def db_cleanup():
    files = os.listdir(db_folder)
    for file in files:
        if file.endswith('.md'):
            file_path = os.path.join(db_folder, file)
            os.remove(file_path)

if args.query:
    query_split = args.query.split(" ")
    sub = users_db
    for i in query_split:
        sub = sub[i]
    print(sub)

if args.cleanup:
    db_cleanup()
    print(f'Cleaned up database {args.database}.')

if args.generate:
    db_cleanup()
    users_db_graph = shared.db_format_graph(users_db)
    for user in users_db_graph["users"]:
        user_name = get_graph_name(user)
        f_content = f'Username: {user}\nFull name: {users_db_graph["full_names"][user]}\n'
        if user+'.png' in os.listdir(db_folder+'images/'):
            f_content += f'Profile picture:\n![[images/{user}.png]]\n'
        f_content += '\n'
        for x in users_db_graph["users"][user]:
            if x in ["friends", "following"]:
                for friend in users_db_graph["users"][user][x]:
                    friend_name = get_graph_name(friend)
                    f_content += f'[[{friend_name}]]\n'
        f = open(db_folder+user_name+".md", "w", encoding="utf-8")
        f.write(f_content)
        f.close()
    print("Generated graph:", args.database)

if args.merge:
    users_db_src = shared.db_load(args.merge)
    users_db = shared.deep_update(users_db, users_db_src)
    shared.db_dump(args.database, users_db)
    print(f'Merged database {args.merge} with {args.database}.')
