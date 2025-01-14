import os
import argparse
import shutil

from lib import shared

parser = argparse.ArgumentParser(description='Database management tool.')
parser.add_argument('database', help='database name')
parser.add_argument('--generate', '-g', action='store_true', help='generate graph from database')
parser.add_argument('--cleanup', '-c', action='store_true', help='remove markdown files from database')
parser.add_argument('--usernames', '-u', action='store_true', help='use usernames instead of full names for generating graph')
parser.add_argument('--query', '-q', help='execute query on database (keys separated with spaces)')
parser.add_argument('--merge', '-m', help='source database to merge')
args = parser.parse_args()

def get_graph_name(user):
    if not args.usernames:
        return shared.format_file_name(users_db["display_names"][user])
    else:
        return shared.format_file_name(user)

def db_cleanup():
    files = os.listdir(db_folder)
    for file in files:
        if file.endswith('.md'):
            file_path = os.path.join(db_folder, file)
            os.remove(file_path)

db_folder = shared.databases_folder+args.database+'/'
users_db = shared.Database.load(args.database)

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
    users_db_graph = shared.Database.format_graph(users_db)
    for user in users_db_graph["users"]:
        user_name = get_graph_name(user)
        f_content = f'Username: {user}\nFull name: {users_db_graph["display_names"][user]}\n'
        if shared.format_file_name(user)+'.png' in os.listdir(db_folder+shared.db_images_folder):
            f_content += f'Profile picture:\n![[{shared.db_images_folder+shared.format_file_name(user)}.png]]\n'
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
    db_folder_merge = shared.databases_folder+args.merge+'/'
    if open(db_folder_merge+'service.txt', 'r').read() != open(db_folder+'service.txt', 'r').read():
        if input("Caution! You are trying to merge databases with different services. It might cause mismatch and inconsistency in database. Are you sure you want to continue? [y/n]: ") == 'y':
            shutil.copy(db_folder_merge+'service.txt', db_folder+'service.txt')
        else:
            exit()
    users_db_src = shared.Database.load(args.merge)
    users_db = shared.deep_update(users_db, users_db_src)
    shared.Database.dump(args.database, users_db)
    for file in os.listdir(db_folder_merge+shared.db_images_folder):
        if file.endswith('.png'):
            shutil.copy(db_folder_merge+shared.db_images_folder+file, db_folder+shared.db_images_folder)
    print(f'Merged database {args.merge} to {args.database}.')
