#!/usr/bin/env python2

import CMSnmp
import socket
import argparse
import sys

class WifiStatus:
    skip = 0
    on = 1
    off = 2


###############################################################################################################""
parser = argparse.ArgumentParser(description='Set CM wifi parameters')

parser.add_argument("--verbose", help="increase output verbosity",action="store_true")
parser.add_argument('--c5', type=int, help='5Ghz channel', default=-1, choices = [36,40,44,48,52,56,60,64,100,104,108,112,116,120,124,128,132,136,140,144,149,153,157,161,165])
parser.add_argument('--c24', type=int,help='2.4Ghz channel', default=-1, choices=xrange(0, 14))
parser.add_argument('--wifi', type=str, help='Wifi on/off', default="", choices=["on", "off"])
parser.add_argument('--cm', type=str, help='IP of a CM or TXT file containing one IP per line', default="", required=True)


args = parser.parse_args()

if args.verbose:
    print args

if args.wifi == "" and args.c5 ==-1 and args.c24 == -1:
    print "Nothing to do ...."
    parser.print_help()
    exit()

try:
    IPs = [line.rstrip('\n') for line in open(args.cm)]

except IOError:
    try:
        socket.inet_aton(args.cm)
        IPs = [args.cm]
    except socket.error:
        print "ERROR: cm arguement is not a txt file nor a valid IP address"
        parser.print_help()
        exit()

if args.wifi == "":
    wifiStatus = WifiStatus.skip
if args.wifi =="on":
    wifiStatus = WifiStatus.on
if args.wifi == "off":
    wifiStatus = WifiStatus.off

chan_24 = args.c24
chan_5 = args.c5


####################################################################################################

for ip in IPs:
    try:
        socket.inet_aton(ip)

        cm = CMSnmp.CMSnmp(ip, "brutelepswd")
        sysDesc = cm.get("1.3.6.1.2.1.1.1.0")

        if args.verbose:
            print ip, " ", sysDesc
        else:
            print ip

        #############################################################################################
        if "TC7210" in sysDesc:

            if chan_24 >= 0:
                cm.__set__("1.3.6.1.4.1.4413.2.2.2.1.18.1.1.2.1.2.32", chan_24, "Gauge32")

            if chan_5 >= 0:
                cm.__set__("1.3.6.1.4.1.4413.2.2.2.1.18.1.1.2.1.2.112", chan_5, "Gauge32")

            if wifiStatus != WifiStatus.skip:
                cm.set("1.3.6.1.4.1.4413.2.2.2.1.18.1.1.2.1.12.32", wifiStatus) #2.4Ghz
                cm.set("1.3.6.1.4.1.4413.2.2.2.1.18.1.1.2.1.12.112", wifiStatus) #5Ghz

            cm.set("1.3.6.1.4.1.4413.2.2.2.1.18.1.1.1.0", 1) #Apply changes


        ##############################################################################################
        if "CG3700B" in sysDesc:

            if chan_24 == 0 or (chan_24 >= 5 and chan_24 <= 13):
                cm.__set__("1.3.6.1.4.1.4413.2.2.2.1.18.1.1.2.1.2.32", chan_24, "Gauge32")

            if chan_5 >= 0:
                cm.__set__("1.3.6.1.4.1.4413.2.2.2.1.18.1.1.2.1.2.112", chan_5, "Gauge32")

            if wifiStatus != WifiStatus.skip:
                cm.set("1.3.6.1.4.1.4413.2.2.2.1.18.1.1.2.1.12.32", wifiStatus) #2.4Ghz
                cm.set("1.3.6.1.4.1.4413.2.2.2.1.18.1.1.2.1.12.112", wifiStatus) #5Ghz

            cm.set("1.3.6.1.4.1.4413.2.2.2.1.18.1.1.1.0", 1) #Apply changes


        ##############################################################################################
        if "CG3100" in sysDesc:
            if chan_24 >= 0 and chan_24 <= 13:
                cm.__set__("1.3.6.1.4.1.4413.2.2.2.1.18.1.1.2.1.2.32", chan_24, "Gauge32")

            if wifiStatus != WifiStatus.skip:
                cm.set("1.3.6.1.4.1.4413.2.2.2.1.18.1.1.2.1.12.32", wifiStatus)  # 2.4Ghz

            cm.set("1.3.6.1.4.1.4413.2.2.2.1.18.1.1.1.0", 1)  # Apply changes

    except socket.error:
        if ip != "" and args.verbose:
            print "Invalid IP: " + ip
        pass
    except:
        print "Unexpected error:", sys.exc_info()