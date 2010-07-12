# -*- coding: utf-8 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

import sys
from traceback import print_exc

import dbus

def main():

    bus = dbus.SystemBus()
    try:
        oya_policy_object = bus.get_object("org.addhen.OyaPolicyKitService",
                "/OyaPolicyKit")
        
        #start dnsmasq service
        oya_policy_object.start_dnsmasq_service("start dnsmasq service",
                dbus_interface = "org.addhen.OyaPolicyKitInterface")
        
    except dbus.DBusException, e:
        print str(e)

if __name__ == '__main__':
    main()
