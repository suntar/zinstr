#!/usr/bin/python3

#from __future__ import print_function
# -*- coding: utf-8 -*-

import sys,os
import getopt
import time
import zhinst.utils

def conn(device_id):
    global daq, device, dev_type
    old_stdout = sys.stdout
    sys.stdout = open(os.devnull, "w")
    try:
      apilevel_example = 6
      err_msg = "#Error: instrument has no demodulator"
      (daq, device, _) = zhinst.utils.create_api_session(device_id, apilevel_example,
                                                       required_devtype='.*LI|.*IA|.*IS',
                                                       required_err_msg=err_msg)
      d = zhinst.ziPython.ziDiscovery()
      d.find(device_id)
      dev_type = d.get(device_id)['devicetype']
      daq.setInt('/%s/demods/0/enable' % device, 1)
      daq.setDouble('/%s/demods/0/rate' % device, 1.0e3)
      daq.sync()
    finally:
      sys.stdout.close()
      sys.stdout = old_stdout
      print("ZI " + dev_type + " " + device_id + " device is opened. Type help to see command list.")
      print("#OK")

def get():
    data = daq.getSample('/%s/demods/0/sample' % device)
    print("{:.5e} {:.5e}".format(data['x'][0],data['y'][0]))
    return data


dev_id=''
argv=sys.argv[1:]
usagetxt="usage: ./zinstr.py -d <device>\n\
    -d,--device <device>  --  device name"
try:
    opts, args = getopt.getopt(argv,"d:",["gpib-num=","ip-address=","device=","test"])
except getopt.GetoptError:
    print(usagetxt,"; error")
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
      print(usagetxt)
      sys.exit()
    elif opt in ("-d", "--device"):
      dev_id = arg

if dev_id == '':
  print(usagetxt)
  quit()



print("#SPP001")
conn(dev_id)

cmdlist = '\
help -- show command list\n\
get -- get x,y\n\
*idn? -- write id string: "zurich instrument, <id>"\n\
get_time -- print current time (unix seconds with ms precision)\
'

while True:
    try:
      cmd=input("").rstrip()
      cmd_u=cmd.upper()
      if cmd_u == "help".upper():
        print(cmdlist)
        print("#OK")
      elif cmd_u == '*IDN?':
        print("zurich instrument, {}, {}".format(dev_id,dev_type))
        print("#OK")
      elif cmd_u == "get".upper():
        get()
        print("#OK")
      elif cmd_u == "get_time".upper():
        print("{:.6f}".format(time.time()))
        print("#OK")
      elif cmd_u == "":
        get()
        print("#OK")
      else:
        print("#Error: Unknown command:", cmd)
    except EOFError:
      break

