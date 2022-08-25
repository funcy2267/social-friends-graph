# About
Create relationship graph from Facebook friends.

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
Go to project directory.\
Install required Python modules:
```
pip3 install -r requirements.txt
```
Download [Firefox webdriver](https://github.com/mozilla/geckodriver/releases) and extract to project directory.\
Login to Facebook and save session:
```
python3 login.py
```

# Usage

### Example usage
Get *username*'s friends and their friends:
```
python3 main.py --user "username" --depth 2
```
Generate graph:
```
python3 database.py --generate
```

Now you can open output folder `Friends` in Obsidian as a vault and see the graph of connections.\
You can run scanning **multiple times** for different users to make your database even larger.

Use `--help` to check more info about usage.

### Database
To see available options for managing your database:
```
python3 database.py --help
```

# Limits
Facebook may [temporarily restrict access](https://www.facebook.com/help/177066345680802) to viewing people's profiles if too many requests are made. To avoid this, you can use `--pause` to wait between scans, use `--noscroll` or partially scan with `--limit`.
