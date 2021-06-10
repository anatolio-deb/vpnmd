"""Non-IPC test cases. Using the Server class directly"""

import subprocess
from multiprocessing import Process
from unittest import TestCase

from vpnmd.appd import Server, iptables_rule_exists


class TestClass01(TestCase):
    """Direct methods calls"""

    address = ("localhost", 6000)
    server = Server(address)
    tun2socks: Process
    ifindex = 1
    ifaddr = "10.0.0.2/24"
    socks_port = 1080
    node_address = "1.1.1.1"
    dns_port = "1053"

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.tun2socks = Process(
            target=subprocess.run,
            kwargs={
                "check": True,
                "args": [
                    "tun2socks-linux-amd64",
                    "-device",
                    f"tun://tun{cls.ifindex}",
                    "-proxy",
                    f"socks5://127.0.0.1:{cls.socks_port}",
                ],
            },
        )
        cls.tun2socks.start()

    def test_case01(self):
        """tun2socks is running"""
        self.assertTrue(self.tun2socks.is_alive())

    def test_case02(self):
        """ifindex and ifaddress are empty values"""
        ifindex, ifaddr = self.server.get_ifindex_and_ifaddr()
        self.assertEqual(ifindex, 0)
        self.assertEqual(ifaddr, "")

    def test_case03(self):
        """Create a tun interface"""
        self.server.add_iface(self.ifindex, self.ifaddr)
        proc = subprocess.run(
            ["ip", "address", "show", f"tun{self.ifindex}"],
            check=True,
            capture_output=True,
        )
        self.assertIn(self.ifaddr, proc.stdout.decode())

    def test_case04(self):
        """ifindex and ifaddr are not empty values"""
        ifindex, ifaddr = self.server.get_ifindex_and_ifaddr()
        self.assertEqual(ifindex, self.ifindex)
        self.assertEqual(ifaddr, self.ifaddr)

    def test_case05(self):
        """Set interface up"""
        self.server.set_iface_up()
        proc = subprocess.run(
            ["ip", "link", "show", f"tun{self.ifindex}"],
            check=True,
            capture_output=True,
        )
        self.assertIn("UP", proc.stdout.decode())

    def test_case06(self):
        """node_address is an empty value"""
        response = self.server.get_node_address()
        self.assertEqual(response, "")

    def test_case07(self):
        """Add the new route for a node_address"""
        self.server.add_node_route(self.node_address, "172.17.0.1", 1)
        proc = subprocess.run(["ip", "route"], check=True, capture_output=True)
        self.assertIn(self.node_address, proc.stdout.decode())

    def test_case08(self):
        """node_address is not an empty value"""
        response = self.server.get_node_address()
        self.assertEqual(response, self.node_address)

    def test_case09(self):
        """Add default route through tun interface"""
        self.server.add_default_route(1)
        proc = subprocess.run(["ip", "route"], check=True, capture_output=True)
        self.assertIn(f"default dev tun{self.ifindex}", proc.stdout.decode())

    def test_case10(self):
        """Add iptables rule"""
        self.server.add_dns_rule(self.dns_port)
        self.assertTrue(iptables_rule_exists(self.dns_port))

    def test_case11(self):
        """Delete iptables rule"""
        self.server.delete_dns_rule()
        self.assertFalse(iptables_rule_exists(self.dns_port))

    # def test_case12(self):
    #     """Delete tun interface"""
    #     while self.tun2socks.is_alive():
    #         self.tun2socks.terminate()

    #     self.server.delete_iface()

    #     with self.assertRaises(subprocess.CalledProcessError):
    #         subprocess.run(
    #             ["ip", "link", "show", f"tun{self.ifindex}"],
    #             check=True,
    #         )
    #     proc = subprocess.run(["ip", "route"], check=True, capture_output=True)
    #     self.assertNotIn(f"default dev tun{self.ifindex}", proc.stdout.decode())

    def test_case12(self):
        """Delete route for the node"""
        self.server.delete_node_route()
        proc = subprocess.run(["ip", "route"], check=True, capture_output=True)
        self.assertNotIn(self.node_address, proc.stdout.decode())

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls.tun2socks.terminate()
