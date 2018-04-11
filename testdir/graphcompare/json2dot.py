#!/usr/bin/python


# -*- coding: utf-8 -*-
# python

# example of reading JSON from a file

import json
import re
import sys

filename = "examples/cascade_mapped.json"

# my_data = json.loads(open(filename).read())
my_data = json.loads(sys.stdin.read())

# print my_data
# print "------------------------------------------------------------------------------"

instances = my_data["namespaces"]["global"]["modules"]["DesignTop"]["instances"]
connections = my_data["namespaces"]["global"]["modules"]["DesignTop"]["connections"]


def print_header():
    print "digraph Diagram {"
    print "  node [shape=box]; # Comment"

def print_trailer():
    print "}"

print_header()

DBG=0
if DBG:
    print "INSTANCES"
    for k in instances:
        # print "%s - %s" % (k, instances[k])
        # try:    print "%-12s %s" % (k, instances[k]['configargs'])
        try:    print "%-12s %s" % (k, instances[k]['modargs'])
        except: print "%-12s %s" % (k, "N/A")

def uniquify(nodename):
    '''Turn e.g. "PE_U70.data.out, PE_U8.data.in.1" into "PE_U70, PE_U8"'''

    # Preserve bitPE-in info e.g.
    # "bitmux_157_lut_bitPE.bit.in.1" => "bitmux_157_lut_bitPE.in1"
    parse = re.search('([^.]*)\.bit\.in\.([0-9])', nodename)
    if parse:
        return '%s.in%s' % (parse.group(1), parse.group(2))


    # Huh really more of a UN-uniquify isn't it
    parse = re.search('([^.]*)[.]', nodename)
    if parse: nodename = parse.group(1)

    # Now turn e.g.
    #    "add_335_343_344_PE" -> "add_335_343_344"

    # Sample PE node:
    #   "add_335_343_344_PE":{
    #     "genref":"cgralib.PE",
    #     "genargs":{"numbitports":["Int",3], "numdataports":["Int",2], "op_kind":["String","alu"], "width":["Int",16]},
    #     "modargs":{"alu_op":["String","add"], "data0_mode":["String","BYPASS"], "data0_value":[["BitVector",16],0], "data1_mode":["String","BYPASS"], "data1_value":[["BitVector",16],0]}
    #   },

    #    "add_335_343_344_PE" -> "add_335_343_344"
    parse = re.search("(.*)_PE", nodename)
    if parse:
        orig = nodename
        # print "FOO", ; print nodename
        # print "FOO", ; print instances[nodename]
        nodename = "%s_PE" % parse.group(1)

        # Wait...this did nothing.  Right?
        assert orig == nodename

        return nodename
    
#     # Sample const node:
#     #           "const7__338":{
#     #             "genref":"coreir.const",
#     #             "genargs":{"width":["Int",16]},
#     #             "modargs":{"value":[["BitVector",16],7]}
#     #           },
# 
#     parse = re.search("^const", nodename)
#     if parse:
#         # print "FOO", ; print nodename
#         # print "FOO", ; print instances[nodename]
# 
#         # nodename = "const%s" % (instances[nodename]['modargs']['value'][1])
#         # NOPE!  Need unique const nodes e.g. trouble if 'const7_334'
#         # and 'const7_448' both collapse to 'const7' :(
# 
#         return nodename


    # Memory nodes
    #     "lb_p4_clamped_stencil_update_stream$mem_1$cgramem" => "mem_1"

    parse = re.search("^lb.*[$](mem_\d+)[$]cgramem", nodename)
    if parse:
        nodename = parse.group(1)
        return nodename

    # "lb_p4_clamped_stencil_update_stream_wen_lut_bitPE" => "wen_lut"
    parse = re.search("wen_lut", nodename)
    if parse:
        nodename = 'wen_lut'
        return nodename


    # Inputs and outputs BEFORE:
    #   io16in_U0 -> PE_U48_mul
    #   io16_U1 -> PE_U4_add
    #   io16in_U0 -> lb_repeat_edge_2_stencil_update_stream$reg_0_1
    #   io16in_U0 -> lb_repeat_edge_2_stencil_update_stream$mem_1
    # AFTER:
    #   INPUT -> PE_U48_mul
    #   PE_U4_add -> OUTPUT (!!???) (fixed elsewhere i guess)
    #   INPUT -> lb_repeat_edge_2_stencil_update_stream$reg_0_1
    #   INPUT -> lb_repeat_edge_2_stencil_update_stream$mem_1
    parse = re.search("^io16_", nodename)
    if parse: return "OUTPUT"

    parse = re.search("^io16in_", nodename)
    if parse: return "INPUT"


    return nodename

def to_or_from(nodename):

    # Apparently connections are unordered!!?
    # I guess ".in", ".out" is supposed to be some kind of clue... :(

    # Some node names include:
    #   PE_U6.data.out
    #   PE_U66.data.in.1
    #   lb_conv1_2_stencil_update_stream$mem_1.rdata
    #   lb_conv1_2_stencil_update_stream$mem_1.wdata
    #   lb_conv1_2_stencil_update_stream$reg_0_1.out

    #     # Special cases for i/o nodes: up is down and down is up
    #     if re.search("io16in.*\.out$", nodename): return "from"
    #     if re.search("io16.*\.in$",    nodename): return "to"

    parse = re.search("\.out$", nodename)
    if parse:
        # connections go FROM output TO input
        # print "FOO I think conn goes FROM %s" % nodename
        return "from"

    parse = re.search("\.in\.\d+$", nodename)
    if parse:
        # connections go FROM output TO input
        return "to"

    # Not sure this case ever happens
    parse = re.search("\.in$", nodename)
    if parse:
        # connections go FROM output TO input
        return "to"

    if re.search("\.wdata$", nodename): return "to"
    if re.search("\.rdata$", nodename): return "from"
    if re.search("\.wen$", nodename): return "to"

    # print "FOO I don't know what '%s' is" % nodename
    # return "unknown"
    sys.stderr.write("\nERROR I don't know what '%s' is\n\n" % nodename)
    assert False

# FIXME hacky hack wacky wack
# Ignore connections to cg_en, ren, wcgw?
def ignoble_node(n):
    if re.search('cg_en$', n):
        if DBG: print('# WARNING Ignoring connection to cg_en signal "%s" wcgw?\n' % n);
        return True
    elif re.search('ren$', n):
        if DBG: print('# WARNING Ignoring connection to ren signal "%s" wcgw?\n' % n);
        return True
    else:
        return False

if DBG:
    print "CONNECTIONS"
    print connections

if DBG: print "CONNECTIONS"
for k in connections:
    # print k
    if DBG: print "# %s , %s" % (k[0], k[1])

    # FIXME hacky hack wacky wack - ignore connections to cg_en, ren, wcgw?
    if ignoble_node(k[1]): continue

    u0 = uniquify(k[0])
    u1 = uniquify(k[1])

    # "lb_p4_clamped_stencil_update_stream$mem_1$cgramem":{
    #   "genref":"cgralib.Mem",
    #   "genargs":{"depth":["Int",1024], "width":["Int",16]},
    #   "modargs":{"almost_full_cnt":["Int",0], "fifo_depth":["Int",64], ...
    # Insert a fifo_depth comment
    # (for some reason, node name has a '.wdata' on the end)

    parse = re.search('(.*).wdata', k[1])
    if parse:
        k1 = parse.group(1)
        if DBG: print "# FOO found wdata node", k1
        fifo_depth = int(instances[k1]['modargs']['depth'][1])
        if DBG: print "# FOO found fifo depth", fifo_depth
        assert fifo_depth > 1 and fifo_depth <= 1024
        fdcomment = ' # fifo_depth %d' % fifo_depth
    else:
        fdcomment = ''

    # Insert a lut_load_value comment
    # Node will have name like "bitnot_156_lut_bitPE.bit.out"
    # mapper json:
    #   "bitand_153_151_154_lut_bitPE":{
    #     "modargs":{
    # "bit0_mode":["String","BYPASS"], "bit0_value":["Bool",false], 
    # "bit1_mode":["String","BYPASS"], "bit1_value":["Bool",false], 
    # "bit2_mode":["String","BYPASS"], "bit2_value":["Bool",false], 
    # "lut_value":[["BitVector",8],"8'h88"]}
    #   },

    parse = re.search('(.*_lut_bitPE).bit.out', k[0])
    if parse:
        # k1 = re.search('(.*).wdata', k[1]).group(1)
        k1 = parse.group(1)
        if DBG: print "# FOO found lut", k1
        lut_value  =     instances[k1]['modargs']['lut_value'][1]
        if DBG: print "# FOO found LUT value", lut_value
        assert lut_value[0:3] == "8'h"
        fdcomment = ' # lut_value 0x%s' % lut_value[3:]
    else:
        fdcomment = ''
        

    # Turn "PE_U70.data.out, PE_U8.data.in.1" into "PE_U70, PE_U8"
    from_node = u0
    to_node   = u1

    tf0 = to_or_from(k[0]); 
    tf1 = to_or_from(k[1]); 
    
    if (tf0 == "to") or (tf1 == "from"):
        from_node = u1
        to_node   = u0

#     # For some reason output is emitted backwards-assed...!!?
#     if (innode == "OUTPUT"):
#         innode = outnode
#         outnode = "OUTPUT"

    # print "  %s" % instances[innode]['modargs']

    # print '    "%s" -> "%s";' % (from_node, to_node)
    print '    "%s" -> "%s";%s' % (from_node, to_node, fdcomment)

    if DBG: print ""

print_trailer()

# mydict = 
# for k0 in mydict:
#     print k0
# #     parse = re.search("u'(.*)'", k0)
# #     if parse: k0 = parse.group(1)
#     print mydict[k0]
# #     print "------------------------------------------------------------------------------"
# #     for k1 in my_data[k0]:
# #         print k1



# json file looks like this:
# 
# {"top":"global.DesignTop",
# "namespaces":{
#   "global":{
#     "modules":{
#       "DesignTop":{
#         "type":["Record",{
#           "in":["Array",1,["Array",16,"BitIn"]],
#           "out":["Array",16,"Bit"]
#         }],
#         "instances":{
#           "add_335_339_340_PE":{
#             "genref":"cgralib.PE",
#             "genargs":{"numbitports":["Int",3], "numdataports":["Int",2], "op_kind":["String","alu"], "width":["Int",16]},
#             "modargs":{"alu_op":["String","add"], "data0_mode":["String","BYPASS"], "data0_value":[["BitVector",16],0], "data1_mode":["String","BYPASS"], "data1_value":[["BitVector",16],0]}
#           },
#           "add_335_343_344_PE":{
#             "genref":"cgralib.PE",
#             "genargs":{"numbitports":["Int",3], "numdataports":["Int",2], "op_kind":["String","alu"], "width":["Int",16]},
#             "modargs":{"alu_op":["String","add"], "data0_mode":["String","BYPASS"], "data0_value":[["BitVector",16],0], "data1_mode":["String","BYPASS"], "data1_value":[["BitVector",16],0]}
#           },
#           "const0__334":{
#             "genref":"coreir.const",
#             "genargs":{"width":["Int",16]},
#             "modargs":{"value":[["BitVector",16],0]}
#           },
# ...
#           "io16_out":{
#             "genref":"cgralib.IO",
#             "genargs":{"width":["Int",16]},
#             "modargs":{"mode":["String","o"]}
#           },
#           "io16in_in_0":{
#             "genref":"cgralib.IO",
#             "genargs":{"width":["Int",16]},
#             "modargs":{"mode":["String","i"]}
#           },
#           "lb_p4_clamped_stencil_update_stream$mem_1$cgramem":{
#             "genref":"cgralib.Mem",
#             "genargs":{"depth":["Int",1024], "width":["Int",16]},
#             "modargs":{"almost_full_cnt":["Int",0], "fifo_depth":["Int",10], "mode":["String","linebuffer"]}
#           },
#           "lb_p4_clamped_stencil_update_stream_wen_lut_bitPE":{
#             "genref":"cgralib.PE",
#             "genargs":{"numbitports":["Int",3], "numdataports":["Int",2], "op_kind":["String","bit"], "width":["Int",16]},
#             "modargs":{"bit0_mode":["String","BYPASS"], "bit0_value":["Bool",false], "bit1_mode":["String","BYPASS"], "bit1_value":["Bool",false], "bit2_mode":["String","BYPASS"], "bit2_value":["Bool",false], "lut_value":[["BitVector",8],1]}
#           },
# ...
#         "connections":[
#           ["const0__334.out","add_335_339_340_PE.data.in.0"],
#           ["const7__338.out","mul_337_338_339_PE.data.in.1"],
#           ["const7__338$1.out","mul_342_338_343_PE.data.in.1"],
#           ["io16_out.in","add_335_343_344_PE.data.out"],
#           ["io16in_in_0.out","lb_p4_clamped_stencil_update_stream$mem_1$cgramem.wdata"],
#           ["io16in_in_0.out","mul_342_338_343_PE.data.in.0"],
#           ["lb_p4_clamped_stencil_update_stream$mem_1$cgramem.rdata","mul_337_338_339_PE.data.in.0"],
#           ["lb_p4_clamped_stencil_update_stream$mem_1$cgramem.wen","lb_p4_clamped_stencil_update_stream_wen_lut_bitPE.bit.out"],
#           ["add_335_339_340_PE.data.out","add_335_343_344_PE.data.in.0"],
#           ["mul_337_338_339_PE.data.out","add_335_339_340_PE.data.in.1"],
#           ["mul_342_338_343_PE.data.out","add_335_343_344_PE.data.in.1"]
