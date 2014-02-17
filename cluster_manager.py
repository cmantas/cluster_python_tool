__author__ = 'cmantas'

from  CassandraNode import CassandraNode as Node


#=====================================  main  ============================================
load_command = "ycsb load cassandra-cql  -P $WORKLOADS/workloada -p host=127.0.0.1 -p port=9042  -s -threads 2 -p recordcount=1000"
read_command = "ycsb run cassandra-cql \
    -P $WORKLOADS/workloada  \
    -p maxexecutiontime=100000000 \
    -p host=127.0.0.1 -p port=9042 \
    -threads 4 \
    -p operationcount=1000000 \
    -p recordcount=100000 -s"

nodes = []

seed = Node("seednode", node_type="SEED", create=True)

node_name = "node_"+str(len(nodes)+1)
nodes.append(Node(node_name, node_type="NODE", create=True))

seed.bootstrap()
for n in nodes:
    n.bootstrap(params= {"seednode": seed.vm.get_private_addr()})


#run ycsb commands
nodes[0].vm.run_command(load_command)
nodes[0].vm.run_command(read_command+" -p clientno %d" % 0 + " 2>/dev/null >ycsb_stats")
print "================= YCSB STATS ===================="
print nodes[0].vm.run_command("cat ycsb_stats")
print "CLUSTER: DONE"

