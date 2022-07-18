import os
import argparse

parser = argparse.ArgumentParser(description='Database cleanup tool.')
parser.add_argument('--folder', '-f', default='Friends/', help='folder with database to clean up (followed by slash)')
args = parser.parse_args()

files = os.listdir(args.folder)

for f in files:
    print("Processing:", f)
    f_path = args.folder+f
    try:
        up_content = set(open(f_path).readlines())
        up_f = open(f_path, 'w')
        up_f.writelines(up_content)
        up_f.close()
    except IsADirectoryError:
        pass
