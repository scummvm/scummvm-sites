"""
Vendorized BuildMaster.

Used to support giving the buildmaster a unique name.
"""

from buildbot.master import BuildMaster as OriginalBuildMaster


class BuildMaster(OriginalBuildMaster):
    """
    BuildMaster that accepts a unique name

    The BuildMaster name is generated from the hostname and the path on the server.
    This clashes because we run multiple masters from one directory.
    """

    def __init__(
        self,
        basedir,
        configFileName=None,
        umask=None,
        reactor=None,
        config_loader=None,
        master_name=None,
    ):
        super().__init__(basedir, configFileName, umask, reactor, config_loader)
        self.name = master_name
