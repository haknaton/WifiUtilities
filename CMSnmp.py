from easysnmp import *
import ctypes


def snmp_to_py(value):
    # print value.snmp_type
    if value.snmp_type == "INTEGER":
        return int(value.value)

    return value.value


def py_to_snmp_type(value):
    if isinstance(value, int):
        return "INTEGER"
    if isinstance(value, str) or isinstance(value, unicode):
        return "OCTETSTR"

    return None


class CMSnmp:
    def __init__(self, ip, community, mac="000000000000"):
        self.ip = ip
        self.mac = mac
        self.community = community
        self.session = Session(hostname=self.ip, community=self.community, version=2, timeout=1, retries=2)

    def __get__(self, oid):
        return self.session.get(oid)

    def get(self, oid):
        return snmp_to_py(self.__get__(oid))

    def __set__(self, oid, value, snmp_type):
        self.session.set(oid, value, snmp_type)

    def set(self, oid, value):
        stype = py_to_snmp_type(value)
        if (not stype):
            print "Type unknow"
            stype = self.__get__(oid).snmp_type

        self.__set__(oid, value, stype)

    def __walk__(self, oid):
        return self.session.walk(oid)

    def walk(self, oid):
        return map(snmp_to_py, self.__walk__(oid))


if (__name__ == "__main__"):
    cm = CMSnmp("10.166.20.101", "brutelepswd")

    ### TEST GET 
    print "Test GET"
    string = cm.get("1.3.6.1.2.1.1.5.0")
    print "\tTest String:\t%s" % string
    integer = cm.get("1.3.6.1.2.1.69.1.1.5.0")
    print "\tTest Integer:\t%d" % integer

    ### TEST SET
    print "Test SET"
    before = integer
    cm.set("1.3.6.1.2.1.69.1.1.5.0", 3)
    integer = cm.get("1.3.6.1.2.1.69.1.1.5.0")
    if (before != integer):
        cm.set("1.3.6.1.2.1.69.1.1.5.0", before)
    print "\tTest Integer:\t%d" % integer

    before = string
    cm.set("1.3.6.1.2.1.1.5.0", "TEST_LIB")
    string = cm.get("1.3.6.1.2.1.1.5.0")
    if (before != integer):
        cm.set("1.3.6.1.2.1.1.5.0", before)
    print "\tTest String:\t%s" % string

    ### TEST WALK
    print "Test WALK"
    print "\tTest String:"
    for i in cm.walk("1.3.6.1.2.1.2.2.1.2"):
        print "\t\t%s" % i
    print "\tTest Integer:"
    for i in cm.walk("1.3.6.1.2.1.10.127.1.1.1.1.6"):
        print "\t\t%d" % i
