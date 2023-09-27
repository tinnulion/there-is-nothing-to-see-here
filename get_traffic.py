import datetime
import psutil
import time


def get_uptime():
    with open("/proc/uptime", "r") as f:
        uptime_seconds = float(f.readline().split()[0])
    return uptime_seconds


def get_total_traffic():
    nc = psutil.net_io_counters()
    traffic = nc.bytes_recv + nc.bytes_sent
    return traffic


def get_clock():
    return time.time()


def get_timestamp():
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return ts


def get_record():
    uptime = get_uptime()
    uptime_hours = uptime / 3600.0
    traffic = get_total_traffic()
    traffic_gb = float(traffic) / 2**30

    record = dict()
    record["uptime_hours"] = uptime_hours
    record["traffic_gb"] = traffic_gb
    record["clock"] = get_clock()
    record["timestamp"] = get_timestamp()

    return record


def cli():
    record = get_record()
    print("{")
    print("  \"uptime_hours\": {:.2f},".format(record["uptime_hours"]))
    print("  \"traffic_gb\": {:.3f},".format(record["traffic_gb"]))
    print("  \"clock\": {:f},".format(record["clock"]))
    print("  \"timestamp\": {}".format(record["timestamp"]))
    print("}")


if __name__ == "__main__":
    cli()
