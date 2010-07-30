# -*- coding: utf-8 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

import gobject
import time
import os

import dbus
import dbus.service
import dbus.mainloop.glib


class OyaPolicyKitException(dbus.DBusException):
    _dbus_error_name = 'org.addhen.OyaPolicyKitException'

class PermissionDeniedByPolicy(dbus.DBusException):
    _dbus_error_name = 'com.ubuntu.DeviceDriver.PermissionDeniedByPolicy'

class OyaPolicyKit(dbus.service.Object):
    
    def __init__(self, conn=None, object_path=None, bus_name=None):
        dbus.service.Object.__init__(self,conn,object_path,bus_name)

        self.dbus_info = None
        self.policy_kit = None
        self.enforce_policy_kit = True

    @dbus.service.method("org.addhen.OyaPolicyInterface",
            in_signature='s', out_signature='as', sender_keyword='sender',
            connection_keyword='conn')
    def start_dnsmasq_service(self, start_service_cmd, sender=None,conn=None):
        self.check_policy_kit_privilege(sender, conn, 'org.addhen.OyaPolicyKitService.there')
        #start dnsmasq service
        # TODO write proper code to start the service
        print "Starting ... %s" % (start_service_cmd )    
            
    @dbus.service.method("org.addhen.OyaPolicyInterface",
        in_signature='', out_signature='',
        sender_keyword='sender', connection_keyword='conn') 
    def RaiseException(self, sender=None, conn=None):
        raise OyaPolicyKitException('Oya PolicyKit ExceptionExcept')

    def check_policy_kit_privilege(self, sender, conn, privilege):
        """ sender - is the sender's private d-bus name
        conn - is the dbus.Connection object
        privilege is the PolicyKit privilege string."""

        if sender is None and conn is None:
            print "No privilege"
            return
        if not self.enforce_policy_kit:
            return

        #get peer PID
        if self.dbus_info is None:
            self.dbus_info = dbus.Interface(conn.get_object('org.freedesktop.DBus',
                '/org/freedesktop/DBus/Bus', False),'org.freedesktop.DBus')
        pid = self.dbus_info.GetConnectionUnixProcessID(sender)

        #query PolicyKit
        if self.policy_kit is None:
            self.policy_kit = dbus.Interface(dbus.SystemBus().get_object(
                'org.freedesktop.PolicyKit1',
                '/org/freedesktop/PolicyKit1/Authority',False),
                'org.freedesktop.PolicyKit1.Authority')
        try:
            (is_auth, _, details) = self.policy_kit.CheckAuthorization(
                    ('unix-process',{'pid':dbus.UInt32(pid,variant_level=1),
                        'start-time':dbus.UInt64(0,variant_level=1)}),
                    privilege,{'':''},dbus.UInt32(1),'',timeout=600)
        except dbus.DBusException, e:
            if e._dbus_error_name == 'org.freedesktop.DBus.Error.ServiceUnknown':
                self.policy_kit = None
                return self.check_policy_kit_privilege(sender, conn,privilege)
            else:
                raise

        if not is_auth:
            print "You are not authorized to access admin privileges"
            raise PermissionDeniedByPolicy(privilege)

if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()
    name = dbus.service.BusName("org.addhen.OyaPolicyKitSerivce",bus)
    object = OyaPolicyKit(bus,'/OyaPolicyKit')

    mainloop = gobject.MainLoop()
    mainloop.run()
