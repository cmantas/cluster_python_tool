__author__ = 'cmantas'
from CassandraNode import CassandraNode as Node

seeds = []     # the seed node(s) of the casssandra cluster !!! ONLY ONE IS SUPPORTED !!!
nodes = []     # the rest of the nodes of the Cassandra cluster

seed_name = "cassandra_seednode"
node_name = "cassandra_node_"


def create_cluster(worker_count=0):
    """
    Creates a Cassandra Cluster with a single Seed Node and 'worker_count' other nodes
    :param worker_count: the number of the nodes to create-apart from the seednode
    """
    #create the seed node
    seeds.append(Node(seed_name, node_type="SEED", create=True))
    #create the rest of the nodes
    for i in range(worker_count):
        name = "cassandra_node_"+str(len(nodes)+1)
        nodes.append(Node(name, create=True))


def bootstrap_cluster():
    """ Runs the necessary boostrap commnands to each of the Seed Node and the other nodes  """
    #bootstrap the seed node
    seeds[0].bootstrap()
    #bootstrap the rest of the nodes
    for n in nodes:
        n.bootstrap(params={"seednode": seeds[0].vm.get_private_addr()})


#=============================== MAIN ==========================

create_cluster(worker_count=1)
bootstrap_cluster()

# run ycsb commands to the cluster

load_command = "ycsb load cassandra-cql  -P $WORKLOADS/workloada -p host=127.0.0.1 -p port=9042  " \
               "-s -threads 2 -p recordcount=1000"
read_command = "ycsb run cassandra-cql -P $WORKLOADS/workloada -p maxexecutiontime=100000000 -p host=127.0.0.1 \
                -p port=9042 -threads 4 -p operationcount=1000 -p recordcount=1000 -s"



nodes[0].vm.run_command(load_command)
nodes[0].vm.run_command(read_command+" -p clientno=%d" % 0 + " 2>/dev/null >ycsb_stats")
print "\n================= YCSB STATS ====================\n"
print nodes[0].vm.run_command("cat ycsb_stats")
print "CLUSTER: DONE"