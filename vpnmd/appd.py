"""vpnmd is a helper daemon for vpnm that runs in the root
and receives IPC requests to perform privileged actions"""
from __future__ import annotations

import subprocess

from anyd import Appd, logging

address = ("localhost", 4000)
appd = Appd(address)
SESSION: dict = {}


def iptables_rule_exists(port):
    try:
        proc = subprocess.run(
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
            capture_output=True,
        )
    except subprocess.CalledProcessError as ex:
        if ex.stderr:
            logging.error(ex.stderr.decode().strip())
        return False
    else:
        if proc.stdout:
            logging.info(proc.stdout.decode().strip())
        return True


@appd.api
def delete_dns_rule():
    try:
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
                SESSION["dns_port"],
            ],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as ex:
        logging.error(ex.stderr.decode().strip())
    else:
        if proc.stdout:
            logging.info(proc.stdout.decode().strip())


@appd.api
def add_dns_rule(port: str):
    if not iptables_rule_exists(port):
        try:
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
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as ex:
            logging.error(ex.stderr.decode().strip())
        else:
            if proc.stdout:
                logging.info(proc.stdout.decode().strip())
        finally:
            SESSION["dns_port"] = port


@appd.api
def get_ifindex_and_ifaddr():
    return (SESSION.get("ifindex"), SESSION.get("ifaddr"))


@appd.api
def delete_iface():
    try:
        proc = subprocess.run(
            ["ip", "tuntap", "del", "dev", f"tun{SESSION['ifindex']}", "mode", "tun"],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as ex:
        logging.error(ex.stderr.decode().strip())
    else:
        if proc.stdout:
            logging.info(proc.stdout.decode().strip())


@appd.api
def add_iface(ifindex: int, ifaddr: str):
    try:
        proc = subprocess.run(
            ["ip", "tuntap", "add", "dev", f"tun{ifindex}", "mode", "tun"],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as ex:
        logging.error(ex.stderr.decode().strip())
    else:
        if proc.stdout:
            logging.info(proc.stdout.decode().strip())
    try:
        proc = subprocess.run(
            ["ip", "address", "add", f"{ifaddr}", "dev", f"tun{ifindex}"],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as ex:
        logging.error(ex.stderr.decode().strip())
    else:
        if proc.stdout:
            logging.info(proc.stdout.decode().strip())
    finally:
        SESSION["ifindex"] = ifindex
        SESSION["ifaddr"] = ifaddr


@appd.api
def set_iface_up():
    """tun2socks must be running"""
    try:
        proc = subprocess.run(
            ["ip", "link", "set", "dev", f"tun{SESSION['ifindex']}", "up"],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as ex:
        logging.error(ex.stderr.decode().strip())
    else:
        if proc.stdout:
            logging.info(proc.stdout.decode().strip())


@appd.api
def add_default_route(metric: int):
    """Device must be UP"""
    try:
        proc = subprocess.run(
            [
                "ip",
                "route",
                "add",
                "default",
                "dev",
                f"tun{SESSION['ifindex']}",
                "metric",
                f"{metric}",
            ],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as ex:
        logging.error(ex.stderr.decode().strip())
    else:
        if proc.stdout:
            logging.info(proc.stdout.decode().strip())


@appd.api
def delete_node_route():
    try:
        proc = subprocess.run(
            [
                "ip",
                "route",
                "delete",
                f"{SESSION['node_address']}",
                "via",
                f"{SESSION['original_gateway']}",
            ],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as ex:
        logging.error(ex.stderr.decode().strip())
    else:
        if proc.stdout:
            logging.info(proc.stdout.decode().strip())


@appd.api
def add_node_route(node_address: str, original_gateway: str, metric: int):
    """Add the route for the v2ray node through the original gateway

    Args:
        node_address (str): An IP address of the v2ray node
        original_gateway (str): The original gateway of the host
        metric (int): The route metric should be lower than the one \
            of the original default route
    """
    try:
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
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as ex:
        logging.error(ex.stderr.decode().strip())
    else:
        if proc.stdout:
            logging.info(proc.stdout.decode().strip())
    finally:
        SESSION["node_address"] = node_address
        SESSION["original_gateway"] = original_gateway


@appd.api
def get_node_address():
    return SESSION.get("node_address")


if __name__ == "__main__":
    appd.start()
