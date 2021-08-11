"""Non-IPC test cases. Using the vpnmd class directly"""

import subprocess
from multiprocessing import Process
from unittest import TestCase

from anyd import ClientSession
from vpnmd import appd


class TestClass01(TestCase):
    """Direct methods calls"""

    tun2socks: Process
    ifindex = 1
    ifaddr = "10.0.0.2/24"
    socks_port = "1080"
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
        ifindex, ifaddr = appd.get_ifindex_and_ifaddr()
        self.assertEqual(ifindex, None)
        self.assertEqual(ifaddr, None)

    def test_case03(self):
        """Create a tun interface"""
        appd.add_iface(self.ifindex, self.ifaddr)
        proc = subprocess.run(
            ["ip", "address", "show", f"tun{self.ifindex}"],
            check=True,
            capture_output=True,
        )
        self.assertIn(self.ifaddr, proc.stdout.decode())

    def test_case04(self):
        """ifindex and ifaddr are not empty values"""
        ifindex, ifaddr = appd.get_ifindex_and_ifaddr()
        self.assertEqual(ifindex, self.ifindex)
        self.assertEqual(ifaddr, self.ifaddr)

    def test_case05(self):
        """Set interface up"""
        appd.set_iface_up()
        proc = subprocess.run(
            ["ip", "link", "show", f"tun{self.ifindex}"],
            check=True,
            capture_output=True,
        )
        self.assertIn("UP", proc.stdout.decode())

    def test_case06(self):
        """node_address is an empty value"""
        response = appd.get_node_address()
        self.assertEqual(response, None)

    def test_case07(self):
        """Add the new route for a node_address"""
        appd.add_node_route(self.node_address, "127.0.0.1", 1)
        proc = subprocess.run(["ip", "route"], check=True, capture_output=True)
        self.assertIn(self.node_address, proc.stdout.decode())

    def test_case08(self):
        """node_address is not an empty value"""
        response = appd.get_node_address()
        self.assertEqual(response, self.node_address)

    def test_case09(self):
        """Add default route through tun interface"""
        appd.add_default_route(1)
        proc = subprocess.run(["ip", "route"], check=True, capture_output=True)
        self.assertIn(f"default dev tun{self.ifindex}", proc.stdout.decode())

    def test_case10(self):
        """Add iptables rule"""
        appd.add_dns_rule(self.dns_port)
        self.assertTrue(appd.iptables_rule_exists(self.dns_port))

    def test_case11(self):
        """Delete iptables rule"""
        appd.delete_dns_rule()
        self.assertFalse(appd.iptables_rule_exists(self.dns_port))

    def test_case12(self):
        """Delete tun interface"""
        if self.tun2socks.is_alive():
            self.tun2socks.terminate()

        self.assertFalse(self.tun2socks.is_alive())

        appd.delete_iface()

        with self.assertRaises(subprocess.CalledProcessError):
            subprocess.run(
                ["ip", "link", "show", f"tun{self.ifindex}"],
                check=True,
            )
        proc = subprocess.run(["ip", "route"], check=True, capture_output=True)
        self.assertNotIn(f"default dev tun{self.ifindex}", proc.stdout.decode())

    def test_case13(self):
        """Delete route for the node"""
        appd.delete_node_route()
        proc = subprocess.run(["ip", "route"], check=True, capture_output=True)
        self.assertNotIn(self.node_address, proc.stdout.decode())

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls.tun2socks.terminate()


class TestClass02(TestCase):
    """IPC method calls"""

    vpnmd: Process
    tun2socks = TestClass01.tun2socks
    ifindex = TestClass01.ifindex
    ifaddr = TestClass01.ifaddr
    socks_port = TestClass01.socks_port
    node_address = TestClass01.node_address
    dns_port = TestClass01.dns_port

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.vpnmd = Process(target=appd.appd.start)
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
        cls.vpnmd.start()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls.vpnmd.terminate()
        cls.tun2socks.terminate()

    def test_case01(self):
        """vpnmd and tun2socks are running"""
        self.assertTrue(self.vpnmd.is_alive())
        self.assertTrue(self.tun2socks.is_alive())

    def test_case02(self):
        """ifindex and ifaddress are empty values"""
        with ClientSession(appd.address) as client:
            ifindex, ifaddr = client.commit("get_ifindex_and_ifaddr")
        self.assertEqual(ifindex, None)
        self.assertEqual(ifaddr, None)

    def test_case03(self):
        """Create a tun interface"""
        with ClientSession(appd.address) as client:
            client.commit("add_iface", self.ifindex, self.ifaddr)
        proc = subprocess.run(
            ["ip", "address", "show", f"tun{self.ifindex}"],
            check=True,
            capture_output=True,
        )
        self.assertIn(self.ifaddr, proc.stdout.decode())

    def test_case04(self):
        """ifindex and ifaddr are not empty values"""
        with ClientSession(appd.address) as client:
            ifindex, ifaddr = client.commit("get_ifindex_and_ifaddr")
        self.assertEqual(ifindex, self.ifindex)
        self.assertEqual(ifaddr, self.ifaddr)

    def test_case05(self):
        """Set interface up"""
        with ClientSession(appd.address) as client:
            client.commit("set_iface_up")
        proc = subprocess.run(
            ["ip", "link", "show", f"tun{self.ifindex}"],
            check=True,
            capture_output=True,
        )
        self.assertIn("UP", proc.stdout.decode())

    def test_case06(self):
        """node_address is an empty value"""
        with ClientSession(appd.address) as client:
            response = client.commit("get_node_address")
        self.assertEqual(response, "")

    def test_case07(self):
        """Add the new route for a node_address"""
        with ClientSession(appd.address) as client:
            client.commit("add_node_route", self.node_address, "172.17.0.1", 1)
        proc = subprocess.run(["ip", "route"], check=True, capture_output=True)
        self.assertIn(self.node_address, proc.stdout.decode())

    def test_case08(self):
        """node_address is not an empty value"""
        with ClientSession(appd.address) as client:
            response = client.commit("get_node_address")
        self.assertEqual(response, self.node_address)

    def test_case09(self):
        """Add default route through tun interface"""
        with ClientSession(appd.address) as client:
            client.commit("add_default_route", 1)
        proc = subprocess.run(["ip", "route"], check=True, capture_output=True)
        self.assertIn(f"default dev tun{self.ifindex}", proc.stdout.decode())

    def test_case10(self):
        """Add iptables rule"""
        with ClientSession(appd.address) as client:
            client.commit("add_dns_rule", self.dns_port)
        proc = subprocess.run(
            ["iptables", "-t", "nat", "-L", "OUTPUT"], check=True, capture_output=True
        )
        self.assertIn(f"{self.dns_port}", proc.stdout.decode())

    def test_case11(self):
        """Delete iptables rule"""
        with ClientSession(appd.address) as client:
            client.commit("delete_dns_rule")
        proc = subprocess.run(
            ["iptables", "-t", "nat", "-L", "OUTPUT"], check=True, capture_output=True
        )
        self.assertNotIn(f"{self.dns_port}", proc.stdout.decode())

    def test_case12(self):
        """Delete tun interface"""
        if self.tun2socks.is_alive():
            self.tun2socks.terminate()

        self.assertFalse(self.tun2socks.is_alive())

        with ClientSession(appd.address) as client:
            client.commit("delete_iface")

        with self.assertRaises(subprocess.CalledProcessError):
            subprocess.run(
                ["ip", "link", "show", f"tun{self.ifindex}"],
                check=True,
            )
        proc = subprocess.run(["ip", "route"], check=True, capture_output=True)
        self.assertNotIn(f"default dev tun{self.ifindex}", proc.stdout.decode())

    def test_case13(self):
        """Delete route for the node"""
        with ClientSession(appd.address) as client:
            client.commit("delete_node_route")
        proc = subprocess.run(["ip", "route"], check=True, capture_output=True)
        self.assertNotIn(self.node_address, proc.stdout.decode())
