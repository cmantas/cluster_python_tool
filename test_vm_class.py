from VM import *
from lib.persistance_module import env_vars

server_name = "test_node"
flavor_id = 1;
image_id = env_vars['cassandra_base_image']



testVM = VM("test1", flavor_id, image_id, create=False)
testVM.create(wait= False)
timer = Timer(); timer.start()
testVM.wait_ready()
delta= timer.stop()
print "ssh active in : "+str(testVM.name)+"in %d seconds" % delta


testVM2 = VM("test2", flavor_id, image_id, create=False)
testVM2.create(wait=False)
timer = Timer(); timer.start()
testVM2.wait_ready()
delta= timer.stop()
print "ssh active in: "+str(testVM2.name)+"in %d seconds" % delta