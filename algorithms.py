import argparse

from lib import shared

parser = argparse.ArgumentParser(description='Algorithms to perform on database.')
parser.add_argument('--database', '-d', help='database name')
parser.add_argument('--find-path', '-F', help='find path from user A to B through other users | from_user to_user')
parser.add_argument('--depth', '-D', type=int, default=1, help='max depth')
parser.add_argument('--bidirectional', '-b', action= 'store_true', help='uses only bidirectional connection')
parser.add_argument('--reverse', '-r', action='store_true', help='swap provided users')
args = parser.parse_args()

def bfs2(v, aim, graph, depth=0, visited=[]):
    global solution
    visited_new=visited+[v]
    for x in graph["users"][v]:
        if x in ['following', 'friends']:
            for i in graph["users"][v][x]:
                if not args.bidirectional or (args.bidirectional and i in graph["users"][v]['followers']):
                    if i == aim:
                        if (depth+1) in solution:
                            solution[depth+1].append(visited_new+[aim])
                        else:
                            solution[depth+1]=[visited_new+[aim]]
                    elif i not in visited_new:
                        bfs2(i, aim, graph, depth+1, visited_new)

users_db = shared.Database.load(args.database)
if args.find_path:
    args_find_path_split = args.find_path.split(" ")
    if not args.reverse:
        args_find_path_from = args_find_path_split[0]
        args_find_path_to = args_find_path_split[1]
    else:
        args_find_path_from = args_find_path_split[1]
        args_find_path_to = args_find_path_split[0]
    users_db_graph = shared.Database.format_graph(users_db)
    solution={}
    bfs2(args_find_path_from, args_find_path_to, users_db_graph)
    solution=dict(sorted(solution.items()))
    depthcounter=0
    for depth in solution:
        depthcounter+=1
        if args.depth == 0 or args.depth >= depthcounter:
            print(f'\nDepth {depth}:')
            for path in solution[depth]:
                print(" -> ".join(map(str, path)))
