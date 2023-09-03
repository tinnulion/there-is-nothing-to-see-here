import datetime
import psutil


def get_timestamp():
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')
    return ts


def get_uptime():
    with open("/proc/uptime", "r") as f:
        uptime_seconds = float(f.readline().split()[0])
    return uptime_seconds


def get_total_traffic():
    nc = psutil.net_io_counters()
    traffic = nc.bytes_recv + nc.bytes_sent
    return traffic


def cli():
    uptime = get_uptime()
    uptime_hours = uptime / 3600.0
    traffic = get_total_traffic()
    traffic_gb = float(traffic) / 2**30
    print("{")
    print("  \"uptime_hours\": {:.2f},".format(uptime_hours))
    print("  \"traffic_gb\": {:.3f},".format(traffic_gb))
    print("  \"timestamp\": {}".format(get_timestamp()))
    print("}")


if __name__ == "__main__":
    cli()
