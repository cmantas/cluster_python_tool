__author__ = 'cmantas'

import VM

from VM import *
from persistance_module import env_vars


class CassandraNode:

    image = env_vars["cassandra_base_image"]
    seed_flavor = env_vars["cassandra_seed_flavor"]
    node_flavor = env_vars["cassandra_node_flavor"]
    name = None
    vm = None
    node_type = None
    bootstraped = False

    def __init__(self, name, node_type, create=False, vm=None):
        self.name = name
        self.node_type = node_type
        if not vm is None:
            # init a node from a VM
            self.from_vm(VM)
        if create: self.create()

    def create(self):
        """
        creates a VM that is a Cassandra Node
        :return:
        """
        if self.node_type == "SEED":
            flavor = self.seed_flavor
        else:
            flavor = self.node_flavor
        #create the VM
        self.vm = VM(self.name, flavor, self.image, create=True)

    def from_vm(self, vm):
        if not vm.created:
            print  "this VM is not created, so you cann't create a node from it"
        self.name = vm.name
        self.vm = vm

    def bootstrap(self, params = None):
        """
        Bootstraps a node with the rest of the cluster
        :return:
        """
        self.vm.wait_ready()
        print "NODE: %s started" % self.name
        if self.node_type == "SEED":
            command = "c-tool be_seed && c-tool full_start"
        else:
            command = "c-tool configure %s && c-tool full_start && service ganglia-monitor restart" % params["seednode"]
        print self.vm.run_command(command)

    def decommission(self):
        print "decommissioning node: " + self.name
        keyspace = env_vars['keyspace']
        priv_ip = self.vm.get_private_address()
        print self.vm.run_command("nodetool repair -h %s %s" % (priv_ip, keyspace))
        print self.vm.run_command("nodetool decommission")
        self.vm.shutdown()

