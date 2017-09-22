from VNFM import *
from WorkflowFunctions import *

vnfd
def check_instant(vnfd_local_path):
    InstantiateVnfWorkflow(VnfId,JobId,NfvoParams)
    vnf_map = get_vnf_database(VnfId)
    check_vm(vnf_map)
    check_flavor(vnf_map)
    check_image(vnf_map)
    check_ip(vnf_map)
    check_volume(vnf_map)
    check_personality(vnf_map)
    #check_userdata(vnf_map)
