import argparse
import datetime
import os
import pprint
import sqlite3
import sys
import time

import termcolor

import get_traffic


_DB_NAME = "traffic_info.db"
# Table structure: record id, uptime hours, traffic in gigabytes, clock time, timestamp as text


def create_db():
    query = "CREATE TABLE IF NOT EXISTS main (id INTEGER PRIMARY KEY, hrs REAL, gbs REAL, clock REAL, stamp TEXT)"
    try:
        conn = sqlite3.connect(_DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()
        termcolor.cprint("DB created, table created!", "green")
    except sqlite3.Error as ex:
        termcolor.cprint("SQL error: {}".format(str(ex)), "red")
        sys.exit(1)


def create_index():
    query = "CREATE INDEX idx_clock ON main(clock);"
    try:
        conn = sqlite3.connect(_DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()
        termcolor.cprint("Index added!", "green")
    except sqlite3.Error as ex:
        termcolor.cprint("SQL error: {}".format(str(ex)), "red")
        sys.exit(1)


def update_db(records):
    query_values = []
    for item in records:
        hrs = item["uptime_hours"]
        gbs = item["traffic_gb"]
        clock = item["clock"]
        timestamp = item["timestamp"]
        val = "({:f}, {:f}, {:f}, \"{}\")".format(hrs, gbs, clock, timestamp)
        query_values.append(val)
    query_tail = ", ".join(query_values)
    query = "INSERT INTO main (hrs, gbs, clock, stamp) VALUES {}".format(query_tail)

    try:
        conn = sqlite3.connect(_DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()
    except sqlite3.Error as ex:
        termcolor.cprint("SQL error: {}".format(str(ex)), "red")
        sys.exit(1)


def fetch_db(last_days=None):
    query = "SELECT * FROM main"
    if last_days is not None:
        threshold = time.time() - last_days * 24.0 * 60.0 * 60.0
        query += " WHERE clock > {:f}".format(threshold)
    query += " ORDER BY id"
    try:
        conn = sqlite3.connect(_DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    except sqlite3.Error as ex:
        termcolor.cprint("SQL error: {}".format(str(ex)), "red")
        sys.exit(1)


def show_db():
    data = fetch_db()
    for item in data:
        print(item)


def get_total_traffic_last_n_days(n):
    data = fetch_db(last_days=n)
    if len(data) <= 1:
        return 0.0

    data.insert(0, (-1, 0.0, 0.0, 0.0, ""))
    pos = 1

    chunks = [[]]
    while pos < len(data) - 1:
        prev_uptime = data[pos - 1][1]
        curr_uptime = data[pos][1]
        if curr_uptime < prev_uptime:
            chunks.append([])
        chunks[-1].append(data[pos][2])
        pos += 1

    total_traffic = 0.0
    for ch in chunks:
        tr = ch[-1] - ch[0]
        assert tr > 0.0
        total_traffic += tr

    return total_traffic


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("task", type=str, default="update", nargs='?')
    args = parser.parse_args()

    if not os.path.exists(_DB_NAME):
        create_db()
        create_index()
        update_db([get_traffic.get_record()])
    elif args.task == "update":
        update_db([get_traffic.get_record()])
    elif args.task == "show":
        show_db()
    elif args.task == "last-30":
        #start = time.time()
        gbs = get_total_traffic_last_n_days(30)
        #duration_ms = 1000.0 * (time.time() - start)
        print(gbs)
        #print("Query took: {:.2f} ms".format(duration_ms))
    else:
        termcolor.cprint("", "red")
        sys.exit(1)


if __name__ == "__main__":
    cli()
