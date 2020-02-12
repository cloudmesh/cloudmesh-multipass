from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import map_parameters
from cloudmesh.shell.command import PluginCommand
from cloudmesh.multipass.Provider import Provider
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from pprint import pprint
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.variables import Variables
from cloudmesh.common.util import banner


class MultipassCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_multipass(self, args, arguments):
        """
        ::

          Usage:
                multipass list [--output=OUTPUT] [--dryrun]
                multipass images [--output=OUTPUT] [--dryrun]
                multipass start NAMES [--output=OUTPUT] [--dryrun]
                multipass stop NAMES [--output=OUTPUT] [--dryrun]
                multipass delete NAMES [--output=OUTPUT][--dryrun]
                multipass shell NAMES [--dryrun]
                multipass run COMMAND NAMES [--output=OUTPUT] [--dryrun]

          Interface to multipass

          Options:
               --output=OUTPUT  the output format [default: table]

          Arguments:
              NAMES   the names of the virtual machine

          Description:

              cms multipass start host[01-03]

                 start multiple vms

              The NAMES can be a parameterized hostname

        """
        name = arguments.NAME

        map_parameters(arguments,
                       "dryrun",
                       "refresh",
                       "cloud",
                       "output")

        variables = Variables()

        arguments.output = Parameter.find("output",
                                          arguments,
                                          variables,
                                          "table")

        names = Parameter.expand(arguments.NAMES)

        VERBOSE(arguments)

        if arguments.list:

            if arguments.dryrun:
                banner("dryrun list")
            else:
                provider = Provider()
                provider.list()

            return ""

        elif arguments.images:

            if arguments.dryrun:
                banner("dryrun images")
            else:

                provider = Provider()
                images = provider.images()

                print(provider.Print(images, kind='image', output=arguments.output))

            return ""

        elif arguments.run:

            if arguments.dryrun:
                banner("dryrun run")

            for name in names:
                if arguments.dryrun:
                    Console.ok(f"run {name} {arguments.COMMAND}")
                else:

                    provider = Provider(name=name)
                    provider.run(name,arguments.COMMAND)

            return ""

        elif arguments.start:

            if arguments.dryrun:
                banner("start")

            for name in names:
                if arguments.dryrun:
                    Console.ok(f"dryrun start {name}")
                else:
                    provider = Provider(name=name)
                    provider.start()

            return ""

        elif arguments.stop:

            if arguments.dryrun:
                banner("stop")

            for name in names:
                if arguments.dryrun:
                    Console.ok(f"dryrun stop {name}")
                else:
                    provider = Provider(name=name)
                    provider.stop()

            return ""

        elif arguments.delete:

            if arguments.dryrun:
                banner("delete")

            for name in names:
                if arguments.dryrun:
                    Console.ok(f"dryrun delete {name}")
                else:
                    provider = Provider(name=name)
                    provider.delete()

            return ""


        elif arguments.shell:

            if len(names) > 1:
                Console.error("shell must only have one host")
                return ""

            name = names[0]

            if arguments.dryrun:
                banner("dryrun shell {name}")
            else:
                provider = Provider(name=name)
                provider.shell()

            return ""


        else:
            Console.error("Not yet implemented")
        return ""

