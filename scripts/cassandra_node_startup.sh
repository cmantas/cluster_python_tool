#accepts as paremeter the IP of the seed node

if [[ -z "$1" ]]; then
echo "configure_cassandra must be called with one parameter: 
	the IP address of the seed node"
exit -1
fi
seed_address=$1

#start ganglia services
service ganglia-monitor start
service gmetad start
service apache2 start


#stop cassandra and remove any data
service cassandra stop
rm -r /var/lib/cassandra
rm /var/log/cassandra/system.log


#look for an IPv4 interface in range 10.0 and use that for the cassandra communication
let if_count=($(ifconfig | grep eth | wc -l ))-1
$my_priv_addr
for i in $(seq 0 $if_count)
	do	#look for IPv4 address
		line=$(ifconfig eth$i | grep "inet addr:")
		line=$(echo $line | awk '{print $2}')
		address=$(echo $line | sed 's/addr://g')
		if [[ "$address" == 10.0.* ]] ;
		then 
			my_priv_addr=$address
			break
		fi 

	done
echo "configuring cassandra.yaml for my address:$my_priv_addr, seed address: $seed_address"

#change the listen address of this node
sed "s/listen_address: .*/listen_address: $my_priv_addr/g"  /etc/cassandra/cassandra.yaml> tmp && mv tmp /etc/cassandra/cassandra.yaml
#change the rpc_address of this node to 0.0.0.0
sed "s/rpc_address: .*/rpc_address: 0.0.0.0/g"  /etc/cassandra/cassandra.yaml> tmp && mv tmp /etc/cassandra/cassandra.yaml
#change the seeds to the input parameter
sed "s/seeds: .*/seeds: \"$seed_address\"/g"  /etc/cassandra/cassandra.yaml> tmp && mv tmp /etc/cassandra/cassandra.yaml

