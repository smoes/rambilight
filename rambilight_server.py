#!/usr/bin/env python
#coding: utf8
 
import lirc
import time
 
sockid=lirc.init("ambilight-server", blocking = False)
 
while True:
    codeIR = lirc.nextcode()
    if codeIR != []:
        print codeIR[0]
    time.sleep(0.05)
