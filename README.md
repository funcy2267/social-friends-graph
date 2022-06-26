# About
Create relationship graph with Facebook friends that can be opened in Obsidian app.
# Requirements
- [Python 3](https://python.org)
- [Firefox](https://firefox.com)
- [Obsidian](https://obsidian.md)
# Setup
Go to project directory.\
Create `Friends/` folder.\
Install required Python modules:
```
pip3 install -r requirements.txt
```
Download [Firefox browser driver](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/#quick-reference) to project directory.\
Login to Facebook and save session:
```
py .\login.py
```
# Usage
## Example usage
Get *user.id*'s friends and their friends:
```
py .\main.py "user.id" --depth 2
```
Now you can open `Friends/` folder in Obsidian as a vault and see the graph view (Graph plugin must be enabled).
## Help
Check more info about usage with `--help` parameter.
## Stored data
Data is saved to `Friends/` folder + collected database dump (user ids with corresponding full names) to `db_dump.json`.