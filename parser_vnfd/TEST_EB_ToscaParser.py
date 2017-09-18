#!/usr/bin/python
# -*- coding:utf-8 -*- 
from __future__ import division, print_function, unicode_literals
from EB_ToscaParser import YamlFile2Dict, EB_ToscaParser
import sys
import json

EB_Tosca_yaml_FilePath = sys.argv[1]
dict_EB_vnfd = YamlFile2Dict(EB_Tosca_yaml_FilePath)
#print (json.dumps(dict_EB_vnfd,indent=4),'\n---------------------------\n\n')
VnfDescription = EB_ToscaParser(dict_EB_vnfd)
#print (json.dumps(VnfDescription,indent=4),'\n---------------------------\n\n')

#added by congyahuan@ebupt.com
#print('vnfd_name:\n',VnfDescription[0])
#print('VnfManagerInfo:\n',VnfDescription[2])
#print('VdusInstancesLimit:\n',VnfDescription[3])

dict_a=VnfDescription[1]

#print(type(dict_a[0])==type([]))
#print(type(dict_a[0][1])==type({}))

vdu_name_list = []

def vnfd_vdu_name_list():
    #vdu_name_list = []
    for i in dict_a[0]:
        vdu_name_list.append(i["name"])
    #return vdu_name_list

print(vnfd_vdu_name_list())

print(dict_a[0][0]['properties']['max_instances'])
