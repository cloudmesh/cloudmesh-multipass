from __future__ import print_function

from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import banner
from cloudmesh.common.variables import Variables
from cloudmesh.multipass.Provider import Provider
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.shell.command import map_parameters


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
                multipass destroy NAMES [--dryrun]
                multipass create NAMES [--image=IMAGE] [--size=SIZE] [--dryrun]
                multipass reboot NAMES [--dryrun]

          Interface to multipass

          Options:
               --output=OUTPUT  the output format [default: table]

          Arguments:
              NAMES   the names of the virtual machine

          Description:

              cms multipass start vm1,vm2

                 start multiple vms

              The NAMES can be a parameterized hostname

        """
        name = arguments.NAME

        map_parameters(arguments,
                       "dryrun",
                       "refresh",
                       "cloud",
                       "image",
                       "size",
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

                print(provider.Print(images,
                                     kind='image',
                                     output=arguments.output))

            return ""

        elif arguments.run:

            if arguments.dryrun:
                banner("dryrun run")

            for name in names:
                if arguments.dryrun:
                    Console.ok(f"run {name} {arguments.COMMAND}")
                else:

                    provider = Provider()
                    provider.run(name, arguments.COMMAND)

            return ""

        elif arguments.create:

            result = ""

            if arguments.dryrun:
                banner("create")

            for name in names:
                if arguments.dryrun:
                    Console.ok(f"dryrun create {name}")
                else:
                    provider = Provider()
                    result = provider.create(name)
                    VERBOSE(result)

            return result

        elif arguments.start:

            result = ""

            if arguments.dryrun:
                banner("start")

            for name in names:
                if arguments.dryrun:
                    Console.ok(f"dryrun start {name}")
                else:
                    provider = Provider()
                    result = provider.start(name)
                    VERBOSE(result)

            return result

        elif arguments.stop:

            result = ""

            if arguments.dryrun:
                banner("stop")

            for name in names:
                if arguments.dryrun:
                    Console.ok(f"dryrun stop {name}")
                else:
                    provider = Provider(name=name)
                    result = provider.stop(name)
                    VERBOSE(result)

            return result

        elif arguments.delete:

            result = ""

            if arguments.dryrun:
                banner("delete")

            for name in names:
                if arguments.dryrun:
                    Console.ok(f"dryrun delete {name}")
                else:
                    provider = Provider()
                    # Default purge is false. Is this ok?
                    result = provider.delete(name)
                    VERBOSE(result)

            return result

        elif arguments.destroy:

            result = ""

            if arguments.dryrun:
                banner("destroy")

            for name in names:
                if arguments.dryrun:
                    Console.ok(f"dryrun destroy {name}")
                else:
                    provider = Provider()
                    result = provider.destroy(name)
                    VERBOSE(result)

            return result

        elif arguments.reboot:

            result = ""

            if arguments.dryrun:
                banner("reboot")

            for name in names:
                if arguments.dryrun:
                    Console.ok(f"dryrun reboot {name}")
                else:
                    provider = Provider()
                    result = provider.reboot(name)
                    VERBOSE(result)

            return result

        elif arguments.shell:

            if len(names) > 1:
                Console.error("shell must only have one host")
                return ""

            name = names[0]

            if arguments.dryrun:
                banner("dryrun shell {name}")
            else:
                provider = Provider()
                provider.shell()

            return ""

        else:
            Console.error("Not yet implemented")
        return ""
