
from inventory import Host, Inventory


class SSOTestInventory(Inventory):
    def __init__(self):
        super().__init__()
        self.add_host(Host("ssotstemeaapp1.dmz.dsv.com", groups=['emea', 'app']))
        self.add_host(Host("ssotstemeaapp2.dmz.dsv.com", groups=['emea', 'app']))
        self.add_host(Host("ssotstemeadgt1.dmz.dsv.com", groups=['emea', 'dgt']))
        self.add_host(Host("ssotstemeadgt2.dmz.dsv.com", groups=['emea', 'dgt']))
        self.add_host(Host("ssotstemeadb1.dmz.dsv.com", groups=['emea', 'db']))
        self.add_host(Host("ssotstemeadb2.dmz.dsv.com", groups=['emea', 'db']))
        self.add_host(Host("ssotstemeadb3.dmz.dsv.com", groups=['emea', 'db']))

        self.add_host(Host("ssotstafriapp1.dmz.dsv.com", groups=['afri', 'app']))
        self.add_host(Host("ssotstafriapp2.dmz.dsv.com", groups=['afri', 'app']))
        self.add_host(Host("ssotstafridgt1.dmz.dsv.com", groups=['afri', 'dgt']))
        self.add_host(Host("ssotstafridgt2.dmz.dsv.com", groups=['afri', 'dgt']))
        self.add_host(Host("ssotstafridb1.dmz.dsv.com", groups=['afri', 'db']))
        self.add_host(Host("ssotstafridb2.dmz.dsv.com", groups=['afri', 'db']))
        self.add_host(Host("ssotstafridb3.dmz.dsv.com", groups=['afri', 'db']))
# dgt - database gateway?
