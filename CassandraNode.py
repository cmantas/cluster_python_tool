__author__ = 'cmantas'

from VM import *
from lib.persistance_module import env_vars


class CassandraNode:
    """
    Class that represents a node in a cassandra cluster. Can be of type 'SEED' or 'REGULAR' (default)
    """
    #static vars
    image = env_vars["cassandra_base_image"]
    seed_flavor = env_vars["cassandra_seed_flavor"]
    node_flavor = env_vars["cassandra_node_flavor"]

    def __init__(self, name, node_type="REGULAR", create=False, vm=None):
        """
        Creates a CassandraNode object.
        :param name:
        :param node_type: if "SEED" then will be treated as seednode
        :param create: if True then the actual VM will be created
        :param vm: if not None then this CassandraNode will be created from an existing vm
        """
        bootstraped = False
        self.name = name
        self.type = node_type
        self.vm = None
        if not vm is None:
            # init a node from a VM
            self.from_vm(VM)
        if create:
            self.create()

    def create(self):
        """
        creates the VM that this Cassandra Node will run on
        :return:
        """
        if self.type == "SEED":
            flavor = self.seed_flavor
        else:
            flavor = self.node_flavor
        #create the VM
        self.vm = VM(self.name, flavor, self.image, create=True)

    def from_vm(self, vm):
        """
        Creates a CassandraNode from an existing VM
        :param vm:
        :return:
        """
        if not vm.created:
            print  "this VM is not created, so you cann't create a node from it"
        self.name = vm.name
        self.vm = vm

    def bootstrap(self, params = None):
        """
        Bootstraps a node with the rest of the Casandra cluster
        :return:
        """
        print "NODE: waiting for %s to be ready" % self.name
        self.vm.wait_ready()
        print "NODE: '%s' booted, running bootstrap scripts" % self.name
        if self.type == "SEED":
            command = "c-tool be_seed && c-tool full_start"
        else:
            command = "c-tool configure %s && c-tool full_start" % params["seednode"]
        print self.vm.run_command(command)
        print "NODE: %s is now bootstrapped" % self.name

    def decommission(self):
        """
        Cecommissions a node from the Cassandra Cluster
        :return:
        """
        print "decommissioning node: " + self.name
        keyspace = env_vars['keyspace']
        priv_ip = self.vm.get_private_address()
        print self.vm.run_command("nodetool repair -h %s %s" % (priv_ip, keyspace))
        print self.vm.run_command("nodetool decommission")
        self.vm.shutdown()

