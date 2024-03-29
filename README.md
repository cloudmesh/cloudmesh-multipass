# The cloudmesh bumpversion command

![GitHub Repo](https://img.shields.io/badge/github-repo-green.svg)](https://github.com/cloudmesh/cloudmesh-bumpversion)
[![image](https://img.shields.io/pypi/pyversions/cloudmesh-bumpversion.svg)](https://pypi.org/project/cloudmesh-bumpversion)
[![image](https://img.shields.io/pypi/v/cloudmesh-bumpversion.svg)](https://pypi.org/project/cloudmesh-bumpversion/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

[![General badge](https://img.shields.io/badge/Status-Production-<COLOR>.svg)](https://shields.io/)
[![GitHub issues](https://img.shields.io/github/issues/cloudmesh/cloudmesh-bumpversion.svg)](https://github.com/cloudmesh/cloudmesh-bumpversion/issues)
[![Contributors](https://img.shields.io/github/contributors/cloudmesh/cloudmesh-bumpversion.svg)](https://github.com/cloudmesh/cloudmesh-bumpversion/graphs/contributors)
[![General badge](https://img.shields.io/badge/Other-repos-<COLOR>.svg)](https://github.com/cloudmesh/cloudmesh)


[![Linux](https://img.shields.io/badge/OS-Linux-orange.svg)](https://www.linux.org/)
[![macOS](https://img.shields.io/badge/OS-macOS-lightgrey.svg)](https://www.apple.com/macos)
[![Windows](https://img.shields.io/badge/OS-Windows-blue.svg)](https://www.microsoft.com/windows)

see cloudmesh.cmd5

* https://github.com/cloudmesh/cloudmesh.cmd5


## Installation

```bash
pip install cloudmesh-multipass
cms help multipass
```
## Last verified install test

cms multipass deploy
* Ubuntu 22.04, Dec 2023Command multipass



## Manual Page

<!-- START-MANUAL -->
```
Command multipass
=================

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
```
<!-- STOP-MANUAL -->