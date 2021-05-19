from __future__ import annotations

import subprocess

from sockets_framework import BaseServer


class Server(BaseServer):
    def delete_tuntap(self):
        subprocess.run("ip tuntap delete dev tun0 mode tun".split(), check=False)

    def delete_node_route(self, node_address: str, original_gateway: str):
        subprocess.run(
            "ip route delete {} via {}".format(node_address, original_gateway).split(),
            check=False,
        )

    def add_default_route(self):
        subprocess.run(
            "ip route add default via 10.0.0.1 metric 1".split(), check=False
        )

    def add_tuntap(self):
        subprocess.run("ip tuntap add dev tun0 mode tun".split(), check=False)

    def add_ifaddr(
        self,
    ):
        subprocess.run("ip address add 10.0.0.2/24 dev tun0".split(), check=False)

    def set_if_up(self):
        subprocess.run("ip link set dev tun0 up".split(), check=False)

    def add_node_route(self, node_address: str, original_gateway: str):
        subprocess.run(
            "ip route add {} via {}".format(node_address, original_gateway).split(),
            check=False,
        )


if __name__ == "__main__":
    server = Server(("localhost", 4000))
    server.start()
