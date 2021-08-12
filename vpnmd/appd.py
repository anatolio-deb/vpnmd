"""vpnmd is a helper daemon for vpnm that runs in the root
and receives IPC requests to perform privileged actions"""
from __future__ import annotations

import argparse
import subprocess

from anyd import Appd, logging

from vpnmd import __version__

address = ("localhost", 6554)
appd = Appd(address)


def _iptables_rule_exists(port: str):
    try:
        subprocess.run(
            [
                "iptables",
                "-t",
                "nat",
                "-C",
                "OUTPUT",
                "-p",
                "udp",
                "--dport",
                "53",
                "-j",
                "REDIRECT",
                "--to-ports",
                port,
            ],
            check=True,
            capture_output=False,
        )
    except subprocess.CalledProcessError:
        return False
    else:
        return True


@appd.api
def iptables_rule_exists(port: str) -> bool:
    return _iptables_rule_exists(port)


@appd.api
def delete_dns_rule(port: str) -> subprocess.CompletedProcess:
    proc = subprocess.run(
        [
            "iptables",
            "-t",
            "nat",
            "-D",
            "OUTPUT",
            "-p",
            "udp",
            "--dport",
            "53",
            "-j",
            "REDIRECT",
            "--to-ports",
            port,
        ],
        check=False,
        capture_output=True,
    )
    return proc


@appd.api
def add_dns_rule(port: str) -> subprocess.CompletedProcess | None:
    proc = None

    if not _iptables_rule_exists(port):
        proc = subprocess.run(
            [
                "iptables",
                "-t",
                "nat",
                "-A",
                "OUTPUT",
                "-p",
                "udp",
                "--dport",
                "53",
                "-j",
                "REDIRECT",
                "--to-ports",
                port,
            ],
            check=False,
            capture_output=True,
        )
    return proc


# @appd.api
# def get_ifindex_and_ifaddr():
#     return (SESSION.get("ifindex"), SESSION.get("ifaddr"))


@appd.api
def delete_iface(ifindex: int) -> subprocess.CompletedProcess:
    proc = subprocess.run(
        ["ip", "tuntap", "del", "dev", f"tun{ifindex}", "mode", "tun"],
        check=False,
        capture_output=True,
    )
    return proc


@appd.api
def add_iface(ifindex: int, ifaddr: str) -> subprocess.CompletedProcess:
    try:
        proc = subprocess.run(
            ["ip", "tuntap", "add", "dev", f"tun{ifindex}", "mode", "tun"],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as ex:
        logging.exception(ex)
    else:
        proc = subprocess.run(
            ["ip", "address", "add", f"{ifaddr}", "dev", f"tun{ifindex}"],
            check=False,
            capture_output=True,
        )
    return proc


@appd.api
def set_iface_up(ifindex: int) -> subprocess.CompletedProcess:
    """tun2socks must be running"""
    proc = subprocess.run(
        ["ip", "link", "set", "dev", f"tun{ifindex}", "up"],
        check=False,
        capture_output=True,
    )
    return proc


@appd.api
def add_default_route(metric: int, ifindex: int) -> subprocess.CompletedProcess:
    """Device must be UP"""
    proc = subprocess.run(
        [
            "ip",
            "route",
            "add",
            "default",
            "dev",
            f"tun{ifindex}",
            "metric",
            f"{metric}",
        ],
        check=False,
        capture_output=True,
    )
    return proc


@appd.api
def delete_node_route(
    node_address: str, original_gateway: str
) -> subprocess.CompletedProcess:
    proc = subprocess.run(
        [
            "ip",
            "route",
            "delete",
            f"{node_address}",
            "via",
            f"{original_gateway}",
        ],
        check=False,
        capture_output=True,
    )
    return proc


@appd.api
def add_node_route(
    node_address: str, original_gateway: str, metric: int
) -> subprocess.CompletedProcess:
    """Add the route for the v2ray node through the original gateway

    Args:
        node_address (str): An IP address of the v2ray node
        original_gateway (str): The original gateway of the host
        metric (int): The route metric should be lower than the one \
            of the original default route
    """
    proc = subprocess.run(
        [
            "ip",
            "route",
            "add",
            f"{node_address}",
            "via",
            f"{original_gateway}",
            "metric",
            f"{metric}",
        ],
        check=False,
        capture_output=True,
    )
    return proc


# @appd.api
# def get_node_address():
#     return SESSION.get("node_address")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="store_true", default=False)
    args = parser.parse_args()
    if args.version:
        print(f"vpnmd, v{__version__}")
    else:
        appd.start()
