import os
from cloudmesh.common.console import Console
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import yn_choice
import sys


class Deploy:

    def __init__(self, dryrun=False):
        self.dryrun = dryrun
        self.operating_system = sys.platform.lower()

    def install(self):
        if self.operating_system == "windows":
            self._install_on_windows()
        elif self.operating_system == "darwin":
            self._install_on_osx()
        elif self.operating_system == "ubuntu":
            self._install_on_ubuntu()
        else:
            # theer could be different
            # methods on different linux versions.
            raise NotImplementedError

    def _install_on_windows(self):
        if not self.dryrun:
            Console.error("dryrun is not yet implemented")
            return ""

        # see https://multipass.run/docs/installing-on-windows
        raise NotImplementedError

    def _install_on_osx(self):
        """
        installs version 1.0.0 on macOS

        see https://multipass.run/docs/installing-on-macos
        """
        # test if you are in sudo, if not
        result = Shell.run("sudo -v")
        if "Sorry, user grey may not run sudo" in result:
            Console.error("this program must be run as sudo")
            if not self.dryrun:
                return ""
        # download
        url = "https://github.com/canonical/multipass/releases/download/v1.0.0/multipass-1.0.0+mac-Darwin.pkg"
        pkg = "multipass-1.0.0+mac-Darwin.pkg"
        # install
        try:
            if self.dryrun:
                Console.ok("Dryrun:")
                Console.ok("")
                Console.ok(f"curl {url} --output {pkg}")
                Console.ok(f"open {pkg}")
            else:
                Shell.run(f"curl {url} --output {pkg}")
                os.system(f"open {pkg}")
        except:
            Console.error("problem downloading multipass")
        # remove
        if not self.dryrun and \
            yn_choice("do you want to delete the downloaded file?"):
            Shell.rm(f"{pkg}")

    def _install_on_ubuntu(self):
        """
        installs the stable release with snap on ubuntu

        see https://multipass.run/docs/installing-on-linux
        """
        if not self.dryrun:
            Console.error("dryrun is not yet implemented")
            return ""
        command = "snap refresh multipass --channel stable"
        os.system(command)
        raise NotImplementedError
