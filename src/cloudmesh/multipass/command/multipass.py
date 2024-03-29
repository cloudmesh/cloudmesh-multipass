from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import banner
from cloudmesh.common.variables import Variables
from cloudmesh.multipass.Provider import Provider as multipassProvider
from cloudmesh.multipass.Deploy import Deploy as multipassDeploy
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.shell.command import map_parameters
from cloudmesh.common.Printer import Printer


class MultipassCommand(PluginCommand):
    # noinspection PyUnusedLocal
    @command
    def do_multipass(self, args, arguments):
        """
        ::

          Usage:
                multipass deploy [--dryrun]
                multipass images [--output=OUTPUT] [--refresh] [--purge] [--dryrun]
                multipass list [--output=OUTPUT] [--dryrun]
                multipass create NAMES [--image=IMAGE]
                                       [--size=SIZE]
                                       [--memory=MEMORY]
                                       [--cpus=CPUS]
                                       [--disk=DISK]
                                       [--dryrun]
                                       [--cloudinit=FILE_OR_URL]
                                       [--network=NETWORK]
                                       [--bridged]
                                       [--mount=SOURCE]
                                       [--timeout=TIMEOUT]
                multipass delete NAMES [--output=OUTPUT][--dryrun]
                multipass destroy NAMES [--output=OUTPUT][--dryrun]
                multipass shell NAMES [--dryrun]
                multipass run COMMAND NAMES [--output=OUTPUT] [--dryrun]
                multipass info NAMES [--output=OUTPUT] [--dryrun]
                multipass suspend NAMES [--output=OUTPUT] [--dryrun]
                multipass resume NAMES [--output=OUTPUT] [--dryrun]
                multipass start NAMES [--output=OUTPUT] [--dryrun]
                multipass stop NAMES [--output=OUTPUT] [--dryrun]
                multipass reboot NAMES [--output=OUTPUT] [--dryrun]
                multipass mount SOURCE DESTINATION [--dryrun]
                multipass umount SOURCE [--dryrun]
                multipass transfer SOURCE DESTINATION [--dryrun]
                multipass set key=VALUE [--dryrun]
                multipass get [key] [--dryrun]
                multipass deploy [--dryrun]
                multipass rename NAMES [--dryrun]
                multipass test
                multipass vm defaults [--output=OUTPUT]
                multipass version

          Interface to multipass

          Options:
               --output=OUTPUT    the output format [default: table]. Other
                                  values are yaml, csv and json.

               --image=IMAGE      the image name to be used to create a VM.

               --cpus=CPUS        Number of CPUs to allocate.
                                  Minimum: 1, default: 1.

               --size=SIZE        Disk space to allocate. Positive integers,
                                  in bytes, or with K, M, G suffix.
                                  Minimum: 512M, default: 5G.

               --mem=MEMORY       Amount of memory to allocate. Positive
                                  integers, in bytes, or with K, M, G suffix.
                                  Minimum: 128M, default: 1G.

               --cloudinit=FILE  Path to a user-data cloudinit configuration

          Arguments:
              NAMES   the names of the virtual machine

          Description:

              The NAMES can be a parameterized hostname such as

                red[0-1,5] = red0,red1,red5

          Commands:

            First you can see the supported multipass images with

                cms multipass images

            Create and launch a new vm using

                cms multipass create NAMES

                Optionally you can provide image name, size, memory,
                number of cpus to create an instance.

            Start one or multiple multipass vms with

                cms multipass start NAMES

            Stop one or multiple vms with

                cms multipass stop NAMES

            Gets all multipass internal key values with

              cms multipass get

            Gets a specific internal key.

              cms multipass get KEY

              Known keys

                  client.gui.autostart
                  client.primary-name
                  local.driver

                  are there more?

            Reboot (stop and then start) vms with

                cms multipass reboot NAMES

            Delete one of multiple vms without purging with

                cms multipass delete NAMES

            Destory multipass vms (delete and purge) with

                cms multipass destroy NAMES

                Caution: Once destroyed everything in vm will be deleted
                         and cannot be recovered.

            WHEN YOU IMPLEMENT A FUNCTION INCLUDE MINIMAL
              DOCUMENTATION HERE
        """
        name = arguments.NAME

        map_parameters(
            arguments,
            "dryrun",
            "purge",
            "refresh",
            "cloud",
            "image",
            "size",
            "memory",
            "disk",
            "cpus",
            "cloudinit", "network", "bridged", "timeout",
            "output"
        )

        image = arguments.image
        variables = Variables()

        arguments.output = Parameter.find("output", arguments, variables, "table")

        names = Parameter.expand(arguments.NAMES)

        VERBOSE(arguments)

        if arguments["test"]:
            print ("test")
            provider = multipassProvider()
            provider.test()

        elif arguments.vm and arguments.defaults:

            print ("defaults")
            arguments.output = arguments.output or "table"
            provider = multipassProvider()
            provider.defaults(output=arguments.output)

        elif arguments.version:
            if arguments.dryrun:
                banner("dryrun list")
            else:
                provider = multipassProvider()
                version = provider.version()
                del version["name"]

                print(Printer.attribute(version, header=["Program", "Version"]))

            return ""

        elif arguments.list:
            if arguments.dryrun:
                banner("dryrun list")
            else:
                provider = multipassProvider()
                vm_list = provider.list()

                print(provider.Print(vm_list, kind="image", output=arguments.output))

            return ""

        elif arguments.images:

            provider = multipassProvider()

            if arguments.dryrun:
                banner("dryrun images")
            elif arguments.purge:
                image_list = provider.images(purge=arguments.purge)
            else:
                image_list = provider.images(
                    refresh=arguments.refresh, purge=arguments.purge
                )

                print(provider.Print(image_list, kind="image", output=arguments.output))

            return ""

        elif arguments.run:
            if arguments.dryrun:
                banner("dryrun run")

            for name in names:
                if arguments.dryrun:
                    Console.ok(f"run {name} {arguments.COMMAND}")
                else:
                    provider = multipassProvider()
                    provider.run(name, arguments.COMMAND)

            return ""

        elif arguments.create:
            result = ""

            if arguments.dryrun:
                banner("create")


            P = ["image", "size", "memory", "cpus", "disk", "cloudinit", "dryrun", "network", "bridged", "mount", "timeout"]
            found = {k: arguments[k] for k in P if arguments[k] is not None and arguments[k] != False}                
            names = Parameter.expand(names)
            
            for name in names:
                if arguments.dryrun:
                    Console.ok(f"dryrun create {name} {found}")
                else:
                    provider = multipassProvider()
            
                    result = provider.create(name, **found)
                    VERBOSE(result)

            # return result
            return ""

        elif arguments.start:
            result = ""

            if arguments.dryrun:
                banner("start")

            for name in names:
                if arguments.dryrun:
                    Console.ok(f"dryrun start {name}")
                else:
                    provider = multipassProvider()
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
                    provider = multipassProvider(name=name)
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
                    provider = multipassProvider()
                    # Default purge is false. Is this ok?
                    result = provider.delete(name)
                    VERBOSE(result)

            return result

        elif arguments.info:
            result = ""

            if arguments.dryrun:
                banner(f"info {name}")

            for name in names:
                if arguments.dryrun:
                    Console.ok(f"dryrun info {name}")
                else:
                    provider = multipassProvider()
                    # Default purge is false. Is this ok?
                    result = provider.info(name)
                    VERBOSE(result)

            return result

        elif arguments.rename:
            result = ""

            if arguments.dryrun:
                banner(f"Current Name: {names[0]}" f"New Name: {names[1]}")

            if names.len() > 2:
                Console.error(
                    "You have entered too many names." "Only enter TWO names at a time."
                )
            else:
                old_name = names[0]
                new_name = names[1]

                provider = multipassProvider()
                result = provider.rename(old_name, new_name)
                VERBOSE(result)

            return result

        elif arguments.suspend:
            result = ""

            if arguments.dryrun:
                banner("suspend")

            for name in names:
                if arguments.dryrun:
                    Console.ok(f"dryrun suspend {name}")
                else:
                    provider = multipassProvider()
                    result = provider.suspend(name)
                    VERBOSE(result)

            return result

        elif arguments.resume:
            result = ""

            if arguments.dryrun:
                banner("resume")

            for name in names:
                if arguments.dryrun:
                    Console.ok(f"dryrun resume {name}")
                else:
                    provider = multipassProvider()
                    result = provider.resume(name)
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
                    provider = multipassProvider()
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
                    provider = multipassProvider()
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
                provider = multipassProvider()
                provider.shell()

            return ""

        elif arguments.info:
            if arguments.dryrun:
                banner("dryrun info")
            else:
                provider = multipassProvider()
                info = provider.info()
                print(provider.Print(info, kind="info", output=arguments.output))

            return ""

        elif arguments.mount:
            if arguments.dryrun:
                banner(f"dryrun mount {arguments.SOURCE} {arguments.DESTINATION}")
            else:
                provider = multipassProvider()
                provider.mount(arguments.SOURCE, arguments.DESTINATION)

                # list the mounts and display as table

            return ""

        elif arguments.deploy:
            provider = multipassDeploy(dryrun=arguments.dryrun)
            provider.install()

        else:
            Console.error("Not yet implemented")
        return ""
