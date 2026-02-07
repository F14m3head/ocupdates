import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

data_dir = os.path.join(root_dir, "bot/data")

# Fetches stop_id and stop_name from stop_code from GTFS static db
def fetch_GTFS_stops(db_path: str, stop_code: str):
    import sqlite3

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    cur.execute("SELECT stop_id, stop_name FROM stops WHERE stop_code = ?", (stop_code,))
    rows = cur.fetchall()

    stop_dict = {row[0]: row[1] for row in rows}

    con.close()
    return stop_dict

print(fetch_GTFS_stops(os.path.join(data_dir, "gtfs_static.sqlite"), "0105"))
