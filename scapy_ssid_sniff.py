#!/usr/bin/python

from scapy.all import *
from pyric import pyw
import argparse
import time
import sys

###################### Utily functions #################################################################################

def hex2int(str):
    return int(str.encode('hex'), 16)


def time_ms():
    return time.time() * 1000


def dot11EltInfoFromId(pkt, id):
    dot11elt = pkt.getlayer(Dot11Elt)
    while dot11elt and dot11elt.ID != id:
            dot11elt = dot11elt.payload.getlayer(Dot11Elt)
    if dot11elt:
            return dot11elt.info

##################### Global "carry-everything super class " ###########################################################
class Cfg:
    chan_ap = {}                                #Dictionnary of SSIDs per channel & seen during a "output_timer interval"
    card = None                                 #PyRIC Object of the wireless card
    if_channel = 1                              #Current channel of the wireless card, incremented every channel_timer interval
    track_channel = 0                           #Current channel of a tracked SSID
    output_timer = 5000                         #Time to aggreagate beacons in chan_ap dictionarry
    channel_timer = 250                         #Time to want before switching to the next channel
    elapsed_time_channel = time_ms()            #Time of the last ouput of aggregated data
    elapsed_time_ouput = time_ms()              #Time of the last channel change
    ssid = ''
    verbose = None

    def __init__(self, _card, _ssid, sampling_timer, channel_hop_timer, verbose):
        self.card = _card
        self.ssid = _ssid
        self.output_timer = sampling_timer
        self.channel_timer = channel_hop_timer
        self.verbose = verbose



##################### Scapy Handler ####################################################################################
def packetHandler(pkt) :
    try:
        global cfg

        #Collect data
        if pkt.haslayer(Dot11) and ( pkt.type == 0 and pkt.subtype == 8) :  #Check if beacon & get data
                channel = hex2int(dot11EltInfoFromId(pkt, 3))
                ssid = pkt.info

                if not channel in cfg.chan_ap:
                    cfg.chan_ap[channel] = [ssid]
                else:
                    if ssid not in cfg.chan_ap[channel]:
                        cfg.chan_ap[channel].append(ssid)

                if ssid == cfg.ssid:
                        cfg.track_channel = channel


        #Time to switch channel ?
        if (time_ms() - cfg.elapsed_time_channel) > cfg.channel_timer:
            if cfg.if_channel == 13:
                cfg.if_channel = 1
            else:
                cfg.if_channel += 1

            try:
                if cfg.verbose:
                    sys.stderr.write("Change to channel " + str(cfg.if_channel) + " for " + cfg.card.dev)

                pyw.chset(pyw.getcard(cfg.card.dev), cfg.if_channel, None)
            except:
                if cfg.verbose:
                    sys.stderr.write("Change to channel "+str(cfg.if_channel)+" failed for " + cfg.card.dev)

            cfg.elapsed_time_channel = time_ms()


        #Time to consumme data ? Aggregate data every cfg.ouput_timer ms
        if (time_ms() - cfg.elapsed_time_ouput) > cfg.output_timer:
            if cfg.ssid:
                output = [time.strftime("%H:%M:%S"), cfg.track_channel]
            else:
                output = [time.strftime("%H:%M:%S")]
            for i in range(1,14):
                    if cfg.chan_ap.has_key(i):
                            output.append(str(len(cfg.chan_ap[i])))
                    else:
                            output.append(0)

            print ",".join(str(x) for x in output)

            cfg.chan_ap.clear()
            cfg.elapsed_time_ouput = time_ms()
    except:
        raise



################################### Read parameters ####################################################################
argp = argparse.ArgumentParser(description="Wireless beacon sniffer & SSID tracking")
argp.add_argument('-d','--dev',help="Wireless Monitor Device")
argp.add_argument('-s','--ssid',help="SSID", default="")
argp.add_argument('-v','--verbose',help="Verbose mode")
argp.add_argument('-c','--cs_timer',help="Channel switch timer in ms", default=250)
argp.add_argument('-o','--output_timer',help="Output timer for aggregated data", default=5000)
args = argp.parse_args()

if not args.dev:
    argp.print_help()
    exit()


########################## WiFi initalization and sanity checks ########################################################


wifaces = pyw.winterfaces()
if args.dev not in wifaces:
    print "Device {0} is not wireless, use one of {1}".format(args.dev, wifaces)
    exit()


dev = pyw.devinfo(args.dev)

if args.verbose:
    print args
    print dev


if dev['mode'] != "monitor":
    print "Interface {0} is not in monitor mode".format(args.dev)
    exit()

cfg = Cfg(dev['card'], args.ssid, args.output_timer, args.cs_timer, args.verbose)

header = ["timestamp"]
if args.ssid:
    header.append("ch_" + args.ssid)
for i in xrange(1, 14):
    header.append("ch_"+ str(i))

print ",".join(header)


########################### Start beacon capture #######################################################################
sniff(iface=cfg.card.dev, prn = packetHandler)
