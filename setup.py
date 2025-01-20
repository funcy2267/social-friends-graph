import os

from lib import shared

required_folders = [shared.user_data_folder, shared.databases_folder, shared.sessions_folder]
for folder in required_folders:
    if not os.path.isdir(folder):
        os.mkdir(folder)
