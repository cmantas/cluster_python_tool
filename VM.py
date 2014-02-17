from lib import connector_okeanos as iaas

__author__ = 'cmantas'
from sys import stderr
from os.path import exists
from os import mkdir
from scp_utils import *
import ntpath

LOGS_DIR = "files/VM_logs"
ATTEMPT_INTERVAL = 2


class VM:
    class Address:
        """
        Helper class that represents an IP address
        """
        def __init__(self, version, ip, in_type):
            self.version = version
            self.ip = ip
            self.type = in_type

        def __str__(self):
            rv = "%s IPv%d: %s" % (self.type, self.version, self.ip)
            return rv

    def __init__(self, name, flavor_id, image_id, create=False, wait=False, log_path=LOGS_DIR):
        """
        VM class constructor
        """
        #set attributes
        self.created = False
        self.name = name
        self.flavor_id = flavor_id
        self.log_path = log_path
        self.image_id = image_id
        self.public_addresses = []
        self.log_path = log_path
        self.addresses = []
        self.id = -1
        if create:
            self.create(wait)
            self.load_addresses()

    def load_addresses(self):
        """
        loads the IP interfaces from the IaaS
        :return:
        """
        addr_list = iaas.get_addreses(self.id)
        for a in addr_list:
            addr = self.Address(a['version'], a['ip'], a['type'])
            self.addresses.append(addr)

    def from_dict(self, in_dict):
        """
        creates a VM from dictionary containing 'name' and 'id' reccords
        """
        self.name = in_dict['name']
        self.id = in_dict['id']

    def create(self, wait=True):
        """
        Creates this VM in the underlying IaaS provider
        """
        #start the timer
        timer = Timer()
        timer.start()
        print "VM: creating '"+self.name+"'"
        self.id = iaas.create_server(self.name, self.flavor_id, self.image_id, LOGS_DIR+"/%s.log" % self.name)
        new_status = iaas.get_vm_status(self.id)
        print('\tIaaS status for VM "%s" is now: %s' % (self.name, new_status or 'not changed yet')),
        if wait:
            self.wait_ready()
        delta = timer.stop()
        print "- took %dsec. (waited for ssh:%r)" % (delta, wait)
        self.created = True

    def shutdown(self):
        """
        Issues the 'shutdown' command to the IaaS provider
        """
        print 'VM: Shutting down "%s" (id: %d)' % (self.name, self.id)
        return iaas.shutdown_vm(self.id)

    def startup(self):
        """
        boots up an existing VM instance in okeanos
        :return: true if VM exist false if not
        """
        if not self.created: return False;
        print 'VM: starting up "%s" (id: %d)' % (self.name, self.id)
        return iaas.startup_vm(self.id)

    def destroy(self):
        """Issues the 'destory' command to the IaaS provider  """
        iaas.destroy_vm(self.id)

    def __str__(self):
            text = ''
            text += '========== VM '+self.name+" ===========\n"
            text += "ID: "+str(self.id)+'\n'
            text += 'host: %s\n' % self.get_host()
            text += "Addresses (%s):" % len(self.addresses)
            for a in self.addresses:
                text += " [" + str(a) + "],"
            text += "\nCloud Status: %s\n" % self.get_cloud_status()
            return text

    @staticmethod
    def vm_from_dict(in_dict):
        """
        creates a VM instance from a synnefo "server" dict
        :param in_dict: "server" or "server details" dictionary from synnefo
        :return: a VM instance for an existing vm
        """
        vm_id, name, flavor_id, image_id = in_dict['id'], in_dict['name'], in_dict['flavor_id'], in_dict['image_id']
        rv = VM(name, flavor_id, image_id)
        rv.created = True
        rv.id = vm_id
        rv.load_addresses()
        return rv

    @staticmethod
    def from_id(vm_id):
        """ creates a VM instance from the VM id """
        vm_dict = iaas.get_vm_details(vm_id)
        return VM.vm_from_dict(vm_dict)

    def get_host(self):
        """the host string for this VM """
        return iaas.get_vm_host(self.id)

    def get_cloud_status(self):
        return iaas.get_vm_status(self.id)

    def run_command(self, command, user='root', indent=0, prefix="\t$:  "):
        """
        runs a command to this VM if it actually exists
        :param command:
        :param user:
        :return:
        """
        if not self.created:
            stderr.write('this VM does not exist (yet),'
                         ' so you cannot run commands on it')
            return "ERROR"
        print "VM: [%s] running SSH command \"%s\"" % (self.name, command)
        return run_ssh_command(self.get_host(), user, command, indent, prefix)

    def put_files(self, files, user='root', remote_path='.', recursive=False):
        """
        Puts a file or a list of files to this VM
        """
        put_file_scp(self.get_host(), user, files, remote_path, recursive)

    def run_files(self, files):
        """
        puts a file in the VM and then runs it
        :param files:
        :return:
        """
        self.put_files(files)

        filename = ''
        remote_path = ''
        if not isinstance(files, (list, tuple)):
            head, tail = ntpath.split(files)
            filename = tail or ntpath.basename(head)
            remote_path = "~/scripts/" + filename
        else:
            for f in files:
                head, tail = ntpath.split(f)
                short_fname = (tail or ntpath.basename(head))
                filename += short_fname + ' '
                remote_path += "~/scripts/"+short_fname+"; "
        #generate the command that runs the desired scripts
        command = 'chmod +x %s; ' \
                  'mkdir -p scripts;' \
                  'mv %s ~/scripts/ 2>/dev/null;' \
                  '%s'\
                  % (filename, filename, remote_path)
        return self.run_command(command)

    def wait_ready(self):
        """
        Waits until it is able to run SSH commands on the VM or a timeout is reached
        """
        success = False
        attempts = 0
        print "VM: Waiting for SSH deamon of %s, on addr: %s :" % (self.name, self.get_public_addr()),
        #time to stop trying
        end_time = datetime.now()+timedelta(seconds=ssh_giveup_timeout)
        timer = Timer()
        timer.start()
        #print("VM: Trying ssh, attempt "),
        while not success:
            #if(attempts%5 == 0): print ("%d" % attempts),
            attempts += 1
            if test_ssh(self.get_public_addr(), 'root'):
                success = True
            else:
                if datetime.now() > end_time:
                    break
                sleep(ATTEMPT_INTERVAL)
        if success: print (" OK"),
        else: print(" FAIL"),
        print (" - waited for " + str(timer.stop())+" sec"),
        return success

    def connect(self, network_id):
        """ Issues the connect command to the IaaS (connects this VM to network_id_"""
        iaas.connect_vm_to_network(self.id, network_id)

    def get_public_addr(self):
        """ Returns a publicly accessible IP address !!! for now, only checks for IPv6+fixed !!!"""
        if len(self.addresses) == 0:
            self.load_addresses()
        for i in self.addresses:
            if i.type == "fixed" and i.version == 6:
                return i.ip
        return None

    def get_private_addr(self):
        #find fixed ip
        for i in self.addresses:
            if i.version == 4 and i.type == "fixed":
                return i.ip


def get_all_vms():
    """
    Creates VM instances for all the VMs of the user available in the IaaS
    """
    vms = []
    vm_ids = iaas.get_all_vm_ids()
    for vm_id in vm_ids:
        vm = VM.vm_from_dict(iaas.get_vm_details(vm_id))
        vms.append(vm)
    return vms


if not exists(LOGS_DIR):
    mkdir(LOGS_DIR)


class Timer():
    """
    Helper class that gives the ablility to measure time between events
    """
    def __init__(self):
        self.started = False
        self.start_time = 0

    def start(self):
        assert self.started is False, " Timer already started"
        self.started = True
        self.start_time = int(round(time() * 1000))

    def stop(self):
        end_time = int(round(time() * 1000))
        assert self.started is True, " Timer had not been started"
        start_time = self.start_time
        self.start_time = 0
        return float(end_time - start_time)/1000