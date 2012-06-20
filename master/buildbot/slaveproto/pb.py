# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Buildbot Team Members

from zope.interface import implements

from twisted.spread import pb
from twisted.python import log
from twisted.internet import error, reactor, task, defer
from twisted.application import service, strports

import buildbot.pbmanager
from buildbot.process import metrics, botmaster
from buildbot.buildslave import AbstractBuildSlave
from buildbot.interfaces import IMasterProtocol

class PBSlaveProto(pb.Avatar):
    implements(IMasterProtocol)

    def __init__(self, name, password, missing_timeout=3600,
                 keepalive_interval=3600):

        self.slavename = name
        self.password = password

        self.registration = None
        self.registered_port = None

        self.slave = None # a RemoteReference to the Bot, when connected
        self.buildslave= None # a local reference to BuildSlave

        self.missing_timeout = missing_timeout
        self.missing_timer = None

        self.keepalive_interval = keepalive_interval

        self.slave = AbstractBuildSlave()

    def setBuilderList(self, builders):
        """
        set BuilderList for a BuildSlave
        """
        pass

    def startBuild(self, builder, args):
        """
        start Build on a SlaveBuilder
        """
        pass

    def getSlaveStatus(self):
        """
        send SlaveStatus to Master
        """
        pass

    def getSlaveInfo(self):
        """
        send SlaveInfo to Master on request
        """
        pass

    def startCommand(self, builder, args):
        """
        start a command on a SlaveBuilder
        """
        pass

    def interruptCommmand(self, builder, args):
        """
        interrupt a command on a SlaveBuilder
        """
        pass

    def shutdown(self):
        """
        shutdown a slave
        """
        pass

    def getPerspective(self, mind, slavename):
        assert slavename == self.slavename
        metrics.MetricCountEvent.log("attached_slaves", 1)

        # record when this connection attempt occurred
        if self.slave_status:
            self.slave_status.recordConnectTime()


        if self.isConnected():
            # duplicate slave - send it to arbitration
            arb = botmaster.DuplicateSlaveArbitrator(self)
            return arb.getPerspective(mind, slavename)
        else:
            log.msg("slave '%s' attaching from %s" % (slavename, mind.broker.transport.getPeer()))
            return self

    def attached():
        pass

    def perspective_keepalive(self):
        self.buildslave.messageReceivedFromSlave()

    def perspective_shutdown(self):
        log.msg("slave %s wants to shut down" % self.slavename)
        self.buildslave.slave_status.setGraceful(True)

    def register(self, new, new_config, master):
        # replace old variables of AbstractBuildSlave to those of slaveproto.pb
        if (not self.registration or
            self.password != new.password or
            new_config.slavePortnum != self.registered_port):
            if self.registration:
                self.registration.unregister()
            self.password = new.password
            self.registered_port = new_config.slavePortnum
            self.registration = master.pbmanager.register(
                    self.registered_port, self.slavename,
                    self.password, self.getPerspective) # Perspective should be PBSlaveProto rather than AbstractBuildSlave
            return self.registration
