import datetime
import os
import random
import sys
import time

import traffic_counter

if os.path.exists("../traffic_info.db"):
    print("Already exists!")
    sys.exit(1)

traffic_counter.create_db()

TOTAL = 365 * 24 * 60

uptime = 0.0
traffic = 0.0

gt_traffic = 0.0
num_reboots = 0

clock = time.time() - 365.0 * 24.0 * 60.0 * 60.0
date = datetime.datetime.now()
date -= datetime.timedelta(days=365)
records = []
for idx in range(TOTAL):
    coin = random.random()
    if coin < 0.0001:
        print("REBOOT!!!")
        uptime = 0.0
        traffic = 0.0
        num_reboots += 1

    uptime += 1.0 / 60
    new_traffic = random.uniform(0.0, 0.01)
    traffic += new_traffic
    gt_traffic += new_traffic
    clock += 60.0
    timestamp = date.strftime('%Y-%m-%d %H:%M:%S')
    date += datetime.timedelta(minutes=1)

    record = dict()
    record["uptime_hours"] = uptime
    record["traffic_gb"] = traffic
    record["clock"] = clock
    record["timestamp"] = timestamp

    records.append(record)
    print(idx + 1, "of",  TOTAL)

traffic_counter.update_db(records)

print()
print("Ground truth traffic = {:.2f} Gb".format(gt_traffic))
print("Num reboots = {:d}".format(num_reboots))
