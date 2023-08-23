import argparse
import ipaddress
import json
import os
import qrcode
import random
import subprocess
import sys
import string
import termcolor
import traceback


CONFIG = {
    "log": {
        "loglevel": "info"
    },
    "routing": {
        "rules": [],
        "domainStrategy": "AsIs"
    },
    "inbounds": [
        {
            "port": 443,
            "protocol": "vless",
            "tag": "vless_tls",
            "settings": {
                "clients": [
                    {
                        "id": "<uuid>",
                        "email": "<email>",
                        "flow": "xtls-rprx-vision"
                    }
                ],
                "decryption": "none"
            },
            "streamSettings": {
                "network": "tcp",
                "security": "reality",
                "realitySettings": {
                    "show": False,
                    "dest": "www.microsoft.com:443",
                    "xver": 0,
                    "serverNames": [
                        "www.microsoft.com"
                    ],
                    "privateKey": "<pbk>",
                    "minClientVer": "",
                    "maxClientVer": "",
                    "maxTimeDiff": 0,
                    "shortIds": [
                        "<sid>>"
                    ]
                }
            },
            "sniffing": {
                "enabled": True,
                "destOverride": [
                    "http",
                    "tls"
                ]
            }
        }
    ],
    "outbounds": [
        {
            "protocol": "freedom",
            "tag": "direct"
        },
        {
            "protocol": "blackhole",
            "tag": "block"
        }
    ]
}

LINK_UNCHANGE = "encryption=none&flow=xtls-rprx-vision&sni=www.microsoft.com&fp=chrome&security=reality"
LINK_TEMPLATE = "vless://{uuid}@{ip}:443/?type=tcp&{unchange}&pbk={pbk}&sid={sid}#{nickname}"


def get_uuid_and_keys():
    try:
        p1 = subprocess.Popen(["/usr/local/bin/xray", "uuid"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out1, err1 = p1.communicate()
        uuid = out1.decode("ascii").strip()

        p2 = subprocess.Popen(["/usr/local/bin/xray", "x25519"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out2, err2 = p2.communicate()
        lines = out2.decode("ascii"). split("\n")
        public_key = lines[1]
        private_key = lines[0]

        pos1 = public_key.find(":")
        public_key = public_key[pos1+2:]
        pos2 = private_key.find(":")
        private_key = private_key[pos2+2:]

        termcolor.cprint("UUID         = {}".format(uuid), "yellow")
        termcolor.cprint("Public key   = {}".format(public_key), "yellow")
        termcolor.cprint("Private key  = {}".format(private_key), "yellow")

        return uuid, public_key, private_key
    except Exception as ex:
        termcolor.cprint("Error: {}".format(ex), "red")
        traceback.print_exc()
        sys.exit(0)


def generate_sid():
    items = [random.choice("0123456789abcdef") for _ in range(8)]
    sid = "".join(items)
    termcolor.cprint("SID          = {}".format(sid), "yellow")
    return sid


def generate_nickname(ip):
    items = "-".join(ip.split("."))
    nickname = "server-{}".format(items)
    termcolor.cprint("Nickname     = {}".format(nickname), "yellow")
    return nickname


def create_conf(path, uuid, sid, public_key, nickname):
    try:
        conf = CONFIG.copy()
        conf["inbounds"][0]["settings"]["clients"][0]["id"] = uuid
        conf["inbounds"][0]["settings"]["clients"][0]["email"] = "admin@{}.com".format(nickname)
        conf["inbounds"][0]["streamSettings"]["realitySettings"]["privateKey"] = public_key
        conf["inbounds"][0]["streamSettings"]["realitySettings"]["shortIds"][0] = sid
        with open(path, "w") as fp:
            json.dump(conf, fp, indent=2)
        termcolor.cprint("Config saved to {}".format(path), "green")
    except Exception as ex:
        termcolor.cprint("Error: {}".format(ex), "red")
        traceback.print_exc()
        sys.exit(0)


def create_link(path, uuid, ip, public_key, sid, nickname):
    try:
        link_content = LINK_TEMPLATE.format(
            uuid=uuid,
            ip=ip,
            unchange=LINK_UNCHANGE,
            pbk=public_key,
            sid=sid,
            nickname=nickname
        )
        with open(path, "w") as fp:
            fp.write(link_content)
        termcolor.cprint("Link saved to {}".format(path), "green")
        return link_content
    except Exception as ex:
        termcolor.cprint("Error: {}".format(ex), "red")
        traceback.print_exc()
        sys.exit(0)


def create_qr(path, link_content):
    try:
        img = qrcode.make(link_content)
        img.save(path)
        termcolor.cprint("QR-code saved to {}".format(path), "green")
    except Exception as ex:
        termcolor.cprint("Error: {}".format(ex), "red")
        traceback.print_exc()
        sys.exit(0)


def cli():
    parser = argparse.ArgumentParser(description="Script creates config, link and QR-code for...")
    parser.add_argument("ip", type=str, help="IP v4 or the server we're working at")
    parser.add_argument("dest", type=str, help="Destination folder")
    args = parser.parse_args()

    ip = args.ip
    dest = os.path.abspath(args.dest)

    uuid, public_key, private_key = get_uuid_and_keys()
    if (uuid is None) or (public_key is None) or (private_key is None):
        termcolor.cprint("Invalid UUID, Public Key or Private Key!", "red")
        sys.exit(0)

    sid = generate_sid()
    nickname = generate_nickname(ip)

    create_conf(
        os.path.join(dest, "config.json"),
        uuid,
        sid,
        public_key,
        nickname
    )

    link_content = create_link(
        os.path.join(dest, "link.txt"),
        uuid,
        ip,
        public_key,
        sid,
        nickname
    )

    create_qr(
        os.path.join(dest, "qrcode.png"),
        link_content
    )

    print()
    termcolor.cprint(link_content, "cyan")
    print()
    termcolor.cprint("Enjoy!", "cyan")

    sys.exit(42)  # All good!


if __name__ == "__main__":
    cli()
