from __future__ import annotations

import subprocess

from sockets_framework import BaseServer
from sockets_framework.core import logging


class Server(BaseServer):
    node_address: str = ""
    original_gateway: str = ""
    ifindex: int = 0
    ifaddr: str = ""
    dns_port: str = ""

    def delete_dns_rule(self):
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
                    self.dns_port,
                ],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as ex:
            logging.error(ex.stderr.decode().strip())
        else:
            if proc.stdout:
                logging.info(proc.stdout.decode().strip())

    def add_dns_rule(self, port: str):
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
            self.dns_port = port

    def get_ifindex_and_ifaddr(self):
        return (self.ifindex, self.ifaddr)

    def delete_iface(self):
        try:
            proc = subprocess.run(
                ["ip", "tuntap", "delete", "dev", f"tun{self.ifindex}", "mode", "tun"],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as ex:
            logging.error(ex.stderr.decode().strip())
        else:
            if proc.stdout:
                logging.info(proc.stdout.decode().strip())

    def add_iface(self, ifindex: int, ifaddr: str):
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
            self.ifindex = ifindex
            self.ifaddr = ifaddr

    def set_iface_up(self):
        """tun2socks must be running"""
        try:
            proc = subprocess.run(
                ["ip", "link", "set", "dev", f"tun{self.ifindex}", "up"],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as ex:
            logging.error(ex.stderr.decode().strip())
        else:
            if proc.stdout:
                logging.info(proc.stdout.decode().strip())

    def add_default_route(self, metric: int):
        """Device must be UP"""
        try:
            proc = subprocess.run(
                [
                    "ip",
                    "route",
                    "add",
                    "default",
                    "dev",
                    f"tun{self.ifindex}",
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

    def delete_node_route(self):
        try:
            proc = subprocess.run(
                [
                    "ip",
                    "route",
                    "delete",
                    f"{self.node_address}",
                    "via",
                    f"{self.original_gateway}",
                ],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as ex:
            logging.error(ex.stderr.decode().strip())
        else:
            if proc.stdout:
                logging.info(proc.stdout.decode().strip())

    def add_node_route(self, node_address: str, original_gateway: str, metric: int):
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
            self.node_address = node_address
            self.original_gateway = original_gateway


if __name__ == "__main__":
    server = Server(("localhost", 4000))
    server.start()
