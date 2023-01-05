import os, sys

from twisted.application import service
from director.vendor.buildmaster import BuildMaster
#from buildbot.master import BuildMaster

master_name = os.environ["MASTER_NAME"]

basedir = '.'
#rotateLength = 10000000
#maxRotatedFiles = 10
configfile = 'master.py'

# Default umask for server
umask = None

# if this is a relocatable tac file, get the directory containing the TAC
if basedir == '.':
    basedir = os.path.abspath(os.path.dirname(__file__))

# note: this line is matched against to check that this is a buildmaster
# directory; do not edit it.
application = service.Application('buildmaster')
from twisted.python.log import ILogObserver, FileLogObserver
application.setComponent(ILogObserver, FileLogObserver(sys.stdout).emit)

#m = BuildMaster(basedir, configfile, umask)
m = BuildMaster(basedir, configfile, umask, master_name=master_name)

m.setServiceParent(application)
