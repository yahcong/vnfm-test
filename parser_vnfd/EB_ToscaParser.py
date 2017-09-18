#!/usr/bin/python2
from __future__ import division, print_function, unicode_literals
import json
import base64
import yaml

def GetVdusInstancesLimit(tosca_nodes_nfv_VDU_list):
    VdusInstancesLimit = {}
    for VDU in tosca_nodes_nfv_VDU_list:
        if(VDU['properties']['min_instances'] < VDU['properties']['max_instances']):
            VdusInstancesLimit[VDU['name']] = {}
            VdusInstancesLimit[VDU['name']]['min_instances'] = VDU['properties']['min_instances']
            VdusInstancesLimit[VDU['name']]['max_instances'] = VDU['properties']['max_instances']

        #VDU['properties'].pop('min_instances')
        #VDU['properties'].pop('max_instances')
    return VdusInstancesLimit
            

def process_policies(policies):
    PoliciesDict = {}
    for policy in policies:
        for key in policy:
            PoliciesDict[key] = policy[key]['properties']
    return PoliciesDict


def GetVnfManagerInfo(VnfManager,tosca_nodes_nfv_CP_list):
    VnfIpInfo = {}
    properties = VnfManager['properties']
    VnfIpInfo['VduName'] = properties['vdu_node']
    VnfIpInfo['VmIndex'] = properties['vm_order']
    CPName = properties['cp_node']
    for CP in tosca_nodes_nfv_CP_list:
        if(CP['name'] == CPName):
            VnfIpInfo['EthIndex'] = CP['properties']['order'] 
            break

    VnfInitParams = {}
    VnfInitParams['protocol'] = properties['protocol']
    VnfInitParams['verify'] = properties['verify']
    VnfInitParams['port'] = properties['port']
    VnfInitParams['username'] = properties['username']
    VnfInitParams['password'] = properties['password']

    VnfManagerInfo = {}
    VnfManagerInfo['VnfIpInfo'] = VnfIpInfo
    VnfManagerInfo['VnfInitParams'] = VnfInitParams 

    return VnfManagerInfo
            

def process_interfaces(interfaces):
    #print (json.dumps(interfaces,indent=4),'\n******************\n\n')
    InterfacesDict = {}

    if(interfaces.has_key('Standard')):
        Standard = interfaces['Standard']
        for key,value in Standard.items():
            type_value = str(type(value))
            if ('str' in type_value) or ('unicode' in type_value):
                InterfacesDict[key] = value
            else:
                if(value.has_key('inputs')):
                    inputs = value['inputs']
                    InputListList = []
                    for key_input,value_input in inputs.items():
                        InputList = []
                        InputList.append(key_input)
                        for key_value_input,value_value_input in value_input.items():
                            InputList.append(key_value_input)
                            InputList.append(value_value_input[0])
                            InputList.append(value_value_input[1])
                        InputListList.append(InputList)
                    InterfacesDict[key] = [value['implementation'],InputListList]
                else:
                    InterfacesDict[key] = value['implementation']

    if(interfaces.has_key('injection')):
        injection = interfaces['injection']
        if(injection.has_key('inputs')):
            inputs = injection['inputs']
            InputListList = []
            for key_input,value_input in inputs.items():
                InputList = []
                InputList.append(key_input)
                for key_value_input,value_value_input in value_input.items():
                    InputList.append(key_value_input)
                    InputList.append(value_value_input[0])
                    InputList.append(value_value_input[1])
                InputListList.append(InputList)
            InterfacesDict['injection'] = [injection['source'],InputListList,injection['destination']]
        else:
            InterfacesDict['injection'] = [injection['source'],injection['destination']]


    return InterfacesDict
                


def process_tosca_nodes_nfv_VDU_list(tosca_nodes_nfv_VDU_list):
    for i in range(0,len(tosca_nodes_nfv_VDU_list)):
        tosca_nodes_nfv_VDU_list[i]['networks'] = []
    
        artifacts = tosca_nodes_nfv_VDU_list[i]['artifacts']
        #artifacts_keys = artifacts.keys()
        #artifacts_key = artifacts_keys[0]
        #tosca_nodes_nfv_VDU_list[i]['image'] = tosca_nodes_nfv_VDU_list[i]['artifacts'][artifacts_key]['file'] 
        tosca_nodes_nfv_VDU_list[i]['image'] = artifacts['VM_image']['file']
        
        capabilities = tosca_nodes_nfv_VDU_list[i]['capabilities']
        #capabilities_keys = capabilities.keys()
        #capabilities_key = capabilities_keys[0]
        #tosca_nodes_nfv_VDU_list[i]['flavor'] = tosca_nodes_nfv_VDU_list[i]['capabilities'][capabilities_key]['properties']
        tosca_nodes_nfv_VDU_list[i]['flavor'] = {} 
        tosca_nodes_nfv_VDU_list[i]['flavor']['num_cpus'] = capabilities['host']['properties']['num_cpus']
        tosca_nodes_nfv_VDU_list[i]['flavor']['disk_size'] = capabilities['host']['properties']['disk_size']
        tosca_nodes_nfv_VDU_list[i]['flavor']['mem_size'] = capabilities['host']['properties']['mem_size'] 
        tosca_nodes_nfv_VDU_list[i]['volume'] = {}
        tosca_nodes_nfv_VDU_list[i]['volume']['size'] = capabilities['host']['properties']['volume_size'] 
     
    
        if(tosca_nodes_nfv_VDU_list[i].has_key('interfaces')):
            interfaces = tosca_nodes_nfv_VDU_list[i]['interfaces']
            InterfacesDict = process_interfaces(interfaces)
            #print (json.dumps(InterfacesDict,indent=4),'\n---------------------------\n\n')
            if(InterfacesDict.has_key('create')):
                value = InterfacesDict['create']
                type_value = str(type(value))
                if ('str' in type_value) or ('unicode' in type_value):
                    file_name = value
                    tosca_nodes_nfv_VDU_list[i]['user_data'] = file_name 
                else:
                    file_name = value[0]
                    InputListList = value[1]
                    for index_InputList in range(0,len(InputListList)):
                        #print (json.dumps(InputListList[index_InputList],indent=4),'\n---------------------------\n\n')
                        if(InputListList[index_InputList][2] == 'SELF'):
                            InputListList[index_InputList][2] = tosca_nodes_nfv_VDU_list[i]['name']
                    tosca_nodes_nfv_VDU_list[i]['user_data'] = [file_name,InputListList] 

            if(InterfacesDict.has_key('injection')):
                value = InterfacesDict['injection']
                file_name = value[0]
                if(len(value) == 3):
                    InputListList = value[1]
                    for index_InputList in range(0,len(InputListList)):
                        #print (json.dumps(InputListList[index_InputList],indent=4),'\n---------------------------\n\n')
                        if(InputListList[index_InputList][2] == 'SELF'):
                            InputListList[index_InputList][2] = tosca_nodes_nfv_VDU_list[i]['name']
                    tosca_nodes_nfv_VDU_list[i]['personality'] = [file_name,InputListList,value[-1]] 
                else:
                    tosca_nodes_nfv_VDU_list[i]['personality'] = [file_name,value[-1]] 

            tosca_nodes_nfv_VDU_list[i].pop('interfaces')
        
        tosca_nodes_nfv_VDU_list[i]['artifacts'].pop('VM_image')
        tosca_nodes_nfv_VDU_list[i].pop('capabilities')
        tosca_nodes_nfv_VDU_list[i].pop('type')
    
 
def process_tosca_nodes_nfv_CP_list(tosca_nodes_nfv_VDU_list,tosca_nodes_nfv_CP_list,tosca_nodes_nfv_VL_list):
    CurOrder = 0
    while(tosca_nodes_nfv_CP_list):
        tosca_nodes_nfv_CP_list_delete = []
        for tosca_nodes_nfv_CP in tosca_nodes_nfv_CP_list:
            #print (json.dumps(tosca_nodes_nfv_CP,indent=4))
            if(tosca_nodes_nfv_CP.has_key('properties')):
                order = tosca_nodes_nfv_CP['properties']['order']
            else:
                order = 0
            if(order == CurOrder):
                tosca_nodes_nfv_CP_list_delete.append(tosca_nodes_nfv_CP)
                requirement_list = tosca_nodes_nfv_CP['requirements']
                for requirement in requirement_list:
                    requirement_keys = requirement.keys()
                    requirement_key = requirement_keys[0]
                    if(requirement_key == 'virtualBinding'):
                        VDUName = requirement[requirement_key]['node']
                    elif(requirement_key == 'virtualLink'):
                        NetNodeName = requirement[requirement_key]['node']
                
                for i in range(0,len(tosca_nodes_nfv_VDU_list)):
                    if(tosca_nodes_nfv_VDU_list[i]['name'] == VDUName):
                        for VL in tosca_nodes_nfv_VL_list:
                            if(VL['name'] == NetNodeName):
                                NetName = VL['properties']['network_name']
                                tosca_nodes_nfv_VDU_list[i]['networks'].append(NetName)
        for tosca_nodes_nfv_CP_delete in tosca_nodes_nfv_CP_list_delete:
            tosca_nodes_nfv_CP_list.remove(tosca_nodes_nfv_CP_delete)    
    
        CurOrder += 1          
            
     
    
def InListList(VDUName,tosca_nodes_nfv_VDU_list_order_list):
    for i in range(len(tosca_nodes_nfv_VDU_list_order_list)):
        for j in range(len(tosca_nodes_nfv_VDU_list_order_list[i])):
    	    if(VDUName == tosca_nodes_nfv_VDU_list_order_list[i][j]['name']):
    	       return i
    return -1
    
def GetVDUOrder(query_tosca_nodes_nfv_VDU,tosca_nodes_nfv_VDU_list_order_list):
    MaxDependsOnNodeOrder = -1 
    requirement_list = query_tosca_nodes_nfv_VDU['requirements']
    for requirement in requirement_list:
        requirement_values = requirement.values()
        DependsOnNodeName = requirement_values[0]['node']
        CurrentDependsOnNodeOrder = InListList(DependsOnNodeName,tosca_nodes_nfv_VDU_list_order_list)
        if (CurrentDependsOnNodeOrder == -1):
            return -1
        else:
            if(CurrentDependsOnNodeOrder > MaxDependsOnNodeOrder):
                MaxDependsOnNodeOrder = CurrentDependsOnNodeOrder
    return MaxDependsOnNodeOrder + 1


def order_tosca_nodes_nfv_VDU_list(tosca_nodes_nfv_VDU_list):
    tosca_nodes_nfv_VDU_list_order_list = []
    round0 = True
    while(len(tosca_nodes_nfv_VDU_list)):
        tosca_nodes_nfv_VDU_list_delete = []
        if(round0):
            tosca_nodes_nfv_VDU_list_order0 = []
            for i in range(0,len(tosca_nodes_nfv_VDU_list)):
                if not(tosca_nodes_nfv_VDU_list[i].has_key('requirements')):
                    tosca_nodes_nfv_VDU_list_delete.append(tosca_nodes_nfv_VDU_list[i])
                    tosca_nodes_nfv_VDU_list_order0.append(tosca_nodes_nfv_VDU_list[i])
            tosca_nodes_nfv_VDU_list_order_list.append(tosca_nodes_nfv_VDU_list_order0) 
            round0 = False
        else:
            tosca_nodes_nfv_VDU_list_orderN = []
            for i in range(0,len(tosca_nodes_nfv_VDU_list)):
                CurrentVDUOrder = GetVDUOrder(tosca_nodes_nfv_VDU_list[i],tosca_nodes_nfv_VDU_list_order_list)
                if(CurrentVDUOrder == len(tosca_nodes_nfv_VDU_list_order_list)):
                    tosca_nodes_nfv_VDU_list[i].pop('requirements')
                    tosca_nodes_nfv_VDU_list_delete.append(tosca_nodes_nfv_VDU_list[i])
                    tosca_nodes_nfv_VDU_list_orderN.append(tosca_nodes_nfv_VDU_list[i])
            tosca_nodes_nfv_VDU_list_order_list.append(tosca_nodes_nfv_VDU_list_orderN)
    
        for tosca_nodes_nfv_VDU_delete in tosca_nodes_nfv_VDU_list_delete:
            tosca_nodes_nfv_VDU_list.remove(tosca_nodes_nfv_VDU_delete)
    
    return tosca_nodes_nfv_VDU_list_order_list 
        

        
def YamlFile2Dict(EB_Tosca_yaml_FilePath):
    fp = open(EB_Tosca_yaml_FilePath,'r')
    str_EB_vnfd = fp.read()
    fp.close()
    dict_EB_vnfd = yaml.load(str_EB_vnfd)
    return dict_EB_vnfd


def EB_ToscaParser(dict_EB_vnfd_vms): 
    vnf_name = dict_EB_vnfd_vms['name']

    node_templates = dict_EB_vnfd_vms['topology_template']['node_templates']

    tosca_nodes_nfv_VDU_list = []
    tosca_nodes_nfv_CP_list = []
    tosca_nodes_nfv_VL_list = []
    for node_template in node_templates.items():
        node_name = node_template[0]
        node_params_dict = node_template[1]
        node_type = node_params_dict['type']
        node_params_dict['name'] = node_name
        if(node_type == 'tosca.nodes.nfv.VDU'):
            tosca_nodes_nfv_VDU_list.append(node_params_dict)
        elif(node_type == 'tosca.nodes.nfv.CP'):
            tosca_nodes_nfv_CP_list.append(node_params_dict)
        elif(node_type == 'tosca.nodes.nfv.VL'):
            tosca_nodes_nfv_VL_list.append(node_params_dict)

    VdusInstancesLimit = GetVdusInstancesLimit(tosca_nodes_nfv_VDU_list)

    VnfManager = dict_EB_vnfd_vms['topology_template']['VnfManager']
    VnfManagerInfo = GetVnfManagerInfo(VnfManager,tosca_nodes_nfv_CP_list)
    
    process_tosca_nodes_nfv_VDU_list(tosca_nodes_nfv_VDU_list)

    process_tosca_nodes_nfv_CP_list(tosca_nodes_nfv_VDU_list,tosca_nodes_nfv_CP_list,tosca_nodes_nfv_VL_list)
    tosca_nodes_nfv_VDU_list_order_list = order_tosca_nodes_nfv_VDU_list(tosca_nodes_nfv_VDU_list)
    
    return (vnf_name,tosca_nodes_nfv_VDU_list_order_list,VnfManagerInfo,VdusInstancesLimit)
        
