# Creates & updates GTFS-static SQLite db...
# Doesn't fetch the feed, it just creates db and stores data.

# Call functions : build_db_from_gtfs_zip(zip_path, db_path)

# .zip needs to be called GTFSExport ...
# Should be named correclty if fetched from the fetch_gtfs_static.py 

import sqlite3
import zipfile
import csv

# -- .ZIP "MANAGER" --
def open_csv_from_zip(zf: zipfile.ZipFile, name: str):
    with zf.open(name) as f:
        # File seemed to close itself witout the following line...
        # This reopens the file to "decode" the data...
        # Not 100% sure if the 'with' statment is still needed, but keeping it to be safe.
        f = zf.open(name)

        # decode as UTF-8 with BOM safety
        text = (line.decode("utf-8-sig") for line in f)
        return csv.DictReader(text)

# -- DATABASE CREATION -- 
def init_db(db_path: str) -> None:
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    cur.executescript("""
    PRAGMA journal_mode=WAL;
    PRAGMA synchronous=NORMAL;
    
    CREATE TABLE IF NOT EXISTS stops (
        stop_id TEXT PRIMARY KEY,
        stop_code TEXT,
        stop_name TEXT,
        stop_lat REAL,
        stop_lon REAL,
        level_id TEXT,
        location_type TEXT,
        parent_station TEXT
    );

    CREATE TABLE IF NOT EXISTS routes (
        route_id TEXT PRIMARY KEY,
        route_short_name TEXT,
        route_long_name TEXT,
        route_type INTEGER
    );

    CREATE TABLE IF NOT EXISTS trips (
        trip_id TEXT PRIMARY KEY,
        route_id TEXT,
        service_id TEXT,
        trip_headsign TEXT,
        direction_id INTEGER,
        wheelchair_accessible INTEGER,
        bikes_allowed INTEGER,
        FOREIGN KEY(route_id) REFERENCES routes(route_id)
    );

    CREATE TABLE IF NOT EXISTS stop_times (
        trip_id TEXT,
        arrival_time TEXT,
        departure_time TEXT,
        stop_id TEXT,
        stop_sequence INTEGER,
        drop_off_type INTEGER,
        pickup_type INTEGER
    );

    CREATE TABLE IF NOT EXISTS calendar (
        service_id TEXT PRIMARY KEY,
        monday INTEGER, tuesday INTEGER, wednesday INTEGER, thursday INTEGER, friday INTEGER, saturday INTEGER, sunday INTEGER,
        start_date TEXT, end_date TEXT
    );

    CREATE TABLE IF NOT EXISTS calendar_dates (
        service_id TEXT,
        date TEXT,
        exception_type INTEGER
    );

    CREATE INDEX IF NOT EXISTS idx_stop_times_stop ON stop_times(stop_id, departure_time);
    CREATE INDEX IF NOT EXISTS idx_stop_times_trip ON stop_times(trip_id, stop_sequence);
    CREATE INDEX IF NOT EXISTS idx_trips_route ON trips(route_id);
    CREATE INDEX IF NOT EXISTS idx_trips_service ON trips(service_id);
    CREATE INDEX IF NOT EXISTS idx_calendar_dates_date ON calendar_dates(date);
    """)
    con.commit()
    con.close()

# -- DATA & DATABASE -- 
def build_db_from_gtfs_zip(gtfs_zip_path: str, db_path: str) -> None:

    # Build/replace GTFS static tables from .zip.

    init_db(db_path)
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # Clear existing data
    cur.executescript("""
    DELETE FROM stop_times;
    DELETE FROM trips;
    DELETE FROM routes;
    DELETE FROM stops;
    DELETE FROM calendar;
    DELETE FROM calendar_dates;
    """)
    con.commit()

    with zipfile.ZipFile(gtfs_zip_path, "r") as zf:
        # stops.txt
        if "stops.txt" in zf.namelist():
            rows = open_csv_from_zip(zf, "stops.txt")
            cur.executemany(
                "INSERT OR REPLACE INTO stops(stop_id, stop_code, stop_name, stop_lat, stop_lon, level_id, location_type, parent_station) VALUES(?,?,?,?,?,?,?,?)",
                ((r["stop_id"], r.get("stop_code",""), r.get("stop_name",""), r.get("stop_lat") or None, r.get("stop_lon") or None, r.get("level_id", ""), r.get("location_type", ""), r.get("parent_station", "") ) for r in rows)
            )
            con.commit()

        # routes.txt
        if "routes.txt" in zf.namelist():
            rows = open_csv_from_zip(zf, "routes.txt")
            cur.executemany(
                "INSERT OR REPLACE INTO routes(route_id, route_short_name, route_long_name, route_type) VALUES(?,?,?,?)",
                ((r["route_id"], r.get("route_short_name",""), r.get("route_long_name",""), int(r.get("route_type") or 0)) for r in rows)
            )
            con.commit()

        # trips.txt
        if "trips.txt" in zf.namelist():
            rows = open_csv_from_zip(zf, "trips.txt")
            cur.executemany(
                "INSERT OR REPLACE INTO trips(trip_id, route_id, service_id, trip_headsign, direction_id, wheelchair_accessible, bikes_allowed) VALUES(?,?,?,?,?,?,?)",
                ((r["trip_id"], r["route_id"], r.get("service_id",""), r.get("trip_headsign",""), int(r.get("direction_id") or 0), int(r.get("wheelchair_accessible") or 0), int(r.get("bikes_allowed") or 0)) for r in rows)
            )
            con.commit()        

        # stop_times.txt
        # This file is huge, expect it to take time
        if "stop_times.txt" in zf.namelist():
            rows = open_csv_from_zip(zf, "stop_times.txt")
            batch = []
            for r in rows:
                batch.append((
                    r["trip_id"],
                    r.get("arrival_time",""),
                    r.get("departure_time",""),
                    r["stop_id"],
                    int(r.get("stop_sequence") or 0),
                    int(r.get("drop_off_type") or 0),
                    int(r.get("pickup_type") or 0),
                ))
                if len(batch) >= 50000:
                    cur.executemany("INSERT INTO stop_times(trip_id, arrival_time, departure_time, stop_id, stop_sequence, drop_off_type, pickup_type) VALUES(?,?,?,?,?,?,?)", batch)
                    con.commit()
                    batch.clear()
            if batch:
                cur.executemany("INSERT INTO stop_times(trip_id, arrival_time, departure_time, stop_id, stop_sequence, drop_off_type, pickup_type) VALUES(?,?,?,?,?,?,?)", batch)
                con.commit()

        # calendar.txt
        # Not sure if this data is needed
        if "calendar.txt" in zf.namelist():
            rows = open_csv_from_zip(zf, "calendar.txt")
            cur.executemany(
                """INSERT OR REPLACE INTO calendar(service_id, monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date)
                   VALUES(?,?,?,?,?,?,?,?,?,?)""",
                ((r["service_id"],
                  int(r.get("monday") or 0), int(r.get("tuesday") or 0), int(r.get("wednesday") or 0),
                  int(r.get("thursday") or 0), int(r.get("friday") or 0), int(r.get("saturday") or 0),
                  int(r.get("sunday") or 0),
                  r.get("start_date",""), r.get("end_date","")) for r in rows)
            )
            con.commit()   

        # calendar_dates.txt
        # Not sure if this data is needed
        if "calendar_dates.txt" in zf.namelist():
            rows = open_csv_from_zip(zf, "calendar_dates.txt")
            cur.executemany(
                "INSERT INTO calendar_dates(service_id, date, exception_type) VALUES(?,?,?)",
                ((r["service_id"], r.get("date",""), int(r.get("exception_type") or 0)) for r in rows)
            )
            con.commit()
    con.close()

def connect_db(db_path: str) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con