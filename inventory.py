
class Host:
    def __init__(self, address, name=None, groups=[]):
        # address - IP of DNS name
        self.address = address
        self.name = name or address
        self.groups = groups  # list of str


class Inventory:
    def __init__(self):
        self._hosts = []

    def hosts(self, group=""):
        if not group:
            # all hosts
            return self._hosts
        return [host for host in self._hosts if group in host.groups]

    def add_host(self, host: Host):
        assert host.address not in [hh.address for hh in self._hosts]
        self._hosts.append(host)


class SampleInventory(Inventory):
    def __init__(self):
        super().__init__()
        self.add_host(Host("127.0.0.1", "localhost1"))
        self.add_host(Host("127.0.0.2", "localhost2", "app"))
        self.add_host(Host("127.0.0.3", "localhost3", "db"))
