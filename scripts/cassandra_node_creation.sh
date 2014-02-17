#reset the password
echo "root:1234" | chpasswd

#export workload directory var for use in this session
export WORKLOADS=/etc/YCSB/workloads

#export PATH var to add bin folder for use in this session
export PATH=$PATH:/etc/YCSB/bin/:
#add a ycsb script in the bin directory
mkdir ~/bin && echo "/etc/YCSB/bin/ycsb \"\$@\""> ~/bin/ycsb && chmod +x ~/bin/ycsb

#put exported vars in bashrc
echo"export WORKLOADS=/etc/YCSB/workloads
export PATH=$PATH:~/bin/:" > ~/.bashrc

