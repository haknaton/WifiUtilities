#!/usr/bin/env python
# -*- coding: utf-8 -*-
from scapy.all import *
import time, sys

beacons = []
ssid = "FakeAP"
mac = "20:E5:2A:FA:CE:"
nb_ap = int(sys.argv[1])
channel = chr(int(sys.argv[2]))
interface = "wlp3s0mon"

for i in range(nb_ap):
	tmp_mac = "%s%s"%(mac, hex(i))
	tmp_ssid = "%s%d"%(ssid, i)
	beacons.append(RadioTap()/
        	Dot11(addr1="ff:ff:ff:ff:ff:ff", addr2=tmp_mac, addr3=tmp_mac)/
        	Dot11Beacon(cap="ESS")/
        	Dot11Elt(ID="SSID", len=len(tmp_ssid),info=tmp_ssid)/
        	Dot11Elt(ID="Rates",info='\x82\x84\x8b\x96\x24\x30\x48\x6C')/
        	Dot11Elt(ID="DSset",info=channel)/ #Channel
        	Dot11Elt(ID="TIM",info="\x00\x01\x00\x00"))

while True:
	for b in beacons:
		sendp(b, iface=interface)
		#time.sleep((100.0/len(beacons))/1000.0)
	time.sleep(0.1)
