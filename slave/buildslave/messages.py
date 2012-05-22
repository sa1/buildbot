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

class Messages:
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination
        self.file = open("/home/sa1/buildbot.messages", 'a')
    def __del__(self):
        self.file.close()
    def sendMessage(self, message):
        """Sends a message from source to destination."""
        print "Sending Message"
        self.file.write("From "+ self.source +" to " + self.destination + " " + message + "\n")
        self.file.flush()