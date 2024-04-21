# About
Create relationship graph between friends using data from social media services.

### Supported services
- Facebook
- Instagram

### Features
- No **API keys** are needed.
- Data can be opened in **Obsidian** to show [graph view](https://help.obsidian.md/Plugins/Graph+view) of connections between friends.
- **Linux** and **Windows** OS are supported.
- Multiple scanning **threads** support.

# Requirements
- [Python 3](https://python.org)
- [Firefox](https://firefox.com)
- [Obsidian](https://obsidian.md)

# Setup
Install required Python modules:
```
pip3 install -r requirements.txt
```
Download [Firefox webdriver](https://github.com/mozilla/geckodriver/releases) and extract to project directory.

# Usage

### Log in
Log in to selected service and save session:
```
python3 login.py {service}
```

### Example usage
Get *username*'s friends and their friends from *Facebook* service:
```
python3 main.py "username" "facebook" --depth 2
```
Generate graph:
```
python3 database.py --generate
```

Now you can open database folder `user_data/your_database/` in Obsidian as a vault and see the graph of connections.\
You can run scanning **multiple times** for different users to make your database even larger.

Use `--help` to check more info about usage of available commands.

# Limits
Facebook may [temporarily restrict access](https://www.facebook.com/help/177066345680802) to viewing people's profiles if too many requests are made. To avoid this, you can use `--pause` to wait between scans, use `--max-scrolls` or partially scan with `--limit`.
