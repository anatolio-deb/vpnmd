from unittest import TestCase

from vpnmd import appd

PORT = "1054"


class TestClass01(TestCase):
    def test_case01(self):
        """Iptables rule not exists"""
        self.assertFalse(appd.iptables_rule_exists(PORT))


class TestClass02(TestCase):
    """Iptables rules"""

    server: appd.Server
    address = ("localhost", 3000)

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.server = appd.Server(cls.address)

    def setUp(self) -> None:
        super().setUp()
        self.server.add_dns_rule(PORT)

    def test_case01(self):
        """Iptables rule exist"""
        self.assertTrue(appd.iptables_rule_exists(PORT))
