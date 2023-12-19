import os
from cloudmesh.common.console import Console
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import yn_choice
import sys
from cloudmesh.common.security import can_use_sudo

class Deploy:

    def __init__(self, dryrun=False):
        self.dryrun = dryrun
        self.operating_system = sys.platform.lower()
        self.directory = ".tmp"
        os.makedirs(self.directory, exist_ok=True)

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

        raise NotImplementedError
        
        import ctypes

        def is_admin():
            try:
                return ctypes.windll.shell32.IsUserAnAdmin()
            except:
                return False

        if not is_admin():
            Console.error("multipass needs admin, but you are not allowed to use it.")
            return ""

        if not self.dryrun:
            Console.error("dryrun is not yet implemented")
            return ""

        # see https://multipass.run/docs/installing-on-windows


    def _install_on_osx(self):
        """
        installs multipass current version on macOS

        see https://multipass.run/docs/installing-on-macos
        """
        # test if you are in sudo, if not
        result = Shell.run("sudo -v")
        if "Sorry, user grey may not run sudo" in result:
            Console.error("this program must be run as sudo")
            if not self.dryrun:
                return ""
        # download

        if not can_use_sudo():
            Console.error("multipass needs sudo, but you are not allowed to use it.")
            return ""

        url = "https://multipass.run/download/macos"
        pkg = "multipass-1.0.0+mac-Darwin.pkg"
        # install
        try:
            get_command = f"cd {self.directory} ; wget wget --content-disposition {url}"
            open_commad = f"cd {self.directory} ; open {pkg}"
            if self.dryrun:
                Console.ok("Dryrun:")
                Console.ok("")
                Console.ok(get_command)
                Console.ok(open_commad)
            else:
                Shell.run(get_command)
                os.system(open_commad)
        except:
            Console.error("problem downloading multipass")
        # remove
        if not self.dryrun and \
            yn_choice("do you want to delete the downloaded file?"):
            Shell.rm(self.directory)

    def _install_on_ubuntu(self):
        """
        installs the stable release with snap on ubuntu

        see https://multipass.run/docs/installing-on-linux
        """
        if not can_use_sudo():
            Console.error("multipass needs sudo, but you are not allowed to use it.")
            return ""

        command = "sudo snap install multipass"
        if not self.dryrun:
            Console.ok("Dryrun:")
            Console.ok("")
            Console.ok(command)
            return ""
        os.system(command)
        raise NotImplementedError
