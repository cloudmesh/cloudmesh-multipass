import json
import os

from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from cloudmesh.common.DateTime import DateTime
from cloudmesh.common.Printer import Printer
from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.util import banner

# some of the banners will be removed.
# they must be used for dryrun
# we also keep it for shell, abd create

# in case of create we need to look at cloudmesh-openstack as it also measures 
# the time it takes to start the image and includes it into the cm dict

# all but the shell need to return a cm dict even if the original multipass does
# not return one for example if we delete a vom we need to return the cmdict
# with a stuatus and introduce a status "DELETE"


"""

from the launch documentation to derive sample. This will be used to create the
manual page for cms multipass. The sample in the provider will be used for the
cms register command which is defined in cloudmesh-cloud so you can add
multipass to your yaml fie.


Options:
  -h, --help           Display this help
  -v, --verbose        Increase logging verbosity, repeat up to three times for
                       more detail
  -c, --cpus <cpus>    Number of CPUs to allocate.
                       Minimum: 1, default: 1.
  -d, --disk <disk>    Disk space to allocate. Positive integers, in bytes, or
                       with K, M, G suffix.
                       Minimum: 512M, default: 5G.
  -m, --mem <mem>      Amount of memory to allocate. Positive integers, in
                       bytes, or with K, M, G suffix.
                       Minimum: 128M, default: 1G.
  -n, --name <name>    Name for the instance. If it is 'primary' (the
                       configured primary instance name), the user's home
                       directory is mounted inside the newly launched instance,
                       in 'Home'.
  --cloud-init <file>  Path to a user-data cloud-init configuration, or '-' for
                       stdin

Arguments:
  image                Optional image to launch. If omitted, then the default
                       Ubuntu LTS will be used.
                       <remote> can be either ‘release’ or ‘daily‘. If <remote>
                       is omitted, ‘release’ will be used.
                       <image> can be a partial image hash or an Ubuntu release
                       version, codename or alias.
                       <url> is a custom image URL that is in http://, https://,
                       or file:// format.
                       
Gregor: interesting is the file:// and http(s):// we shoudl try if we can 
  do 19.10 on 
  osx and windows
"""


class Provider(ComputeNodeABC):
    kind = "multipass"

    sample = """
    cloudmesh:
      cloud:
        {name}:
          cm:
            active: true
            heading: {name}
            host: TBD
            label: {name}
            kind: multipass
            version: TBD
            service: compute
          credentials:
            username: TBD
            key_path: ~/.ssh/id_rsa.pub
          default:
            size: m1.medium
            image: 18.04
            cpu: 1
            disk: 5G
            mem: 1GB
            @ cloudinit: file:// ... or http:// 
    """

    output = {
        "vm": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "cm.cloud",
                      "ipv4",
                      "name",
                      "release",
                      "state"],
            "header": ["Name",
                       "Cloud",
                       "Address",
                       "Name",
                       "Release",
                       "State"],
        },
        "image": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "os",
                      "release",
                      "remote",
                      "version",
                      "aliases"],
            "header": ["Name",
                       "OS",
                       "Release",
                       "Remote",
                       "Version",
                       "Alias"]
        },
        "info": {
            "sort_keys": ["cm.name"],
            "order": ["name",
                      "state",
                      "images_release",
                      "memory",
                      "mounts",
                      "ipv4",
                      "release",
                      "image_hash"],
            "header": ["Name",
                       "State",
                       "Image Release",
                       "Memory",
                       "Mounts",
                       "Ipv4",
                       "Release",
                       "Image Hash"]
        },
    }

    # please add a status here if there is one that you observe. WHat are all
    # the States form multipass?

    STATUS = ['UNKOWN']

    def __init__(self, name="multipass",
                 configuration="~/.cloudmesh/cloudmesh.yaml"):
        """
        Initializes the multipass provider. The default parameters are read
        from the configuration file that is defined in yaml format.

        :param name: The name of the provider as defined in the yaml file
        :param configuration: The location of the yaml configuration file
        """
        #
        # The following will be added later once we have identified how to
        # configure multipass from cloudmesh.yaml. This requires understanding
        # the get and set methods and setting defaults for sizes
        #
        # conf = Config(configuration)["cloudmesh"]
        # super().__init__(name, conf)
        #
        self.cloudtype = "multipass"
        self.cloud = name

    # noinspection PyPep8Naming
    # TODO: docstring
    def Print(self, data, output=None, kind=None):

        if output == "table":
            if kind == "secrule":
                # this is just a temporary fix, both in sec.py and
                # here the secgruops and secrules should be separated
                result = []
                for group in data:
                    # for rule in group['security_group_rules']:
                    #     rule['name'] = group['name']
                    result.append(group)
                data = result

            order = self.output[kind]['order']  # not pretty
            header = self.output[kind]['header']  # not pretty
            # humanize = self.output[kind]['humanize']  # not pretty

            print(Printer.flatwrite(data,
                                    sort_keys=["name"],
                                    order=order,
                                    header=header,
                                    output=output,
                                    # humanize=humanize
                                    )
                  )
        else:
            print(Printer.write(data, output=output))

    def update_dict(self, elements, kind=None):
        """
        converts the dict into a list

        :param elements: the list of original dicts. If elements is a single
                         dict a list with a single element is returned.
        :param kind: for some kinds special attributes are added. This includes
                     key, vm, image, flavor.
        :return: The list with the modified dicts
        """

        if elements is None:
            return None

        d = []
        for key, entry in elements.items():

            entry['name'] = key

            if "cm" not in entry:
                entry['cm'] = {}

            # if kind == 'ip':
            #    entry['name'] = entry['floating_ip_address']

            entry["cm"].update({
                "kind": kind,
                "driver": self.cloudtype,
                "cloud": self.cloud,
                "name": key
            })

            if kind == 'vm':

                entry["cm"]["updated"] = str(DateTime.now())

                # if 'public_v4' in entry:
                #    entry['ip_public'] = entry['public_v4']

                # if "created_at" in entry:
                #    entry["cm"]["created"] = str(entry["created_at"])
                # del entry["created_at"]
                #    if 'status' in entry:
                #        entry["cm"]["status"] = str(entry["status"])
                # else:
                #    entry["cm"]["created"] = entry["modified"]

            elif kind == 'image':

                entry["cm"]["created"] = entry["updated"] = str(
                    DateTime.now())

            d.append(entry)
        return d

    # New method to return vm status
    # TODO: docstring
    def _get_vm_status(self, name=None) -> dict:

        dict_result = {}
        result = Shell.run(f"multipass info {name} --format=json")

        if f'instance "{name}" does not exist' in result:
            dict_result = {
                'name': name,
                'status': "instance does not exist"
            }
        else:
            result = json.loads(result)
            dict_result = {
                'name': name,
                'status': result["info"][name]['state']
            }

        return dict_result

    def _images(self):
        """
        internal method that returns a native multipass dict of the images.

        :return: dict of images in multipass format
        """
        result = Shell.run("multipass find --format=json")
        #
        # TODO: relpace with json.loads
        #
        result = eval(result)['images']
        return result

    def images(self, **kwargs):
        """
        Lists the images on the cloud

        :return: dict
        """
        result = self._images()
        return self.update_dict(result, kind="image")

    def image(self, name=None):
        """
        Gets the image with a given name

        :param name: The name of the image
        :return: the dict of the image
        """
        result = self._images()
        result = [result[name]]
        return self.update_dict(result, kind="image")

    def _vm(self):
        """
        internal method that returns the dict of all vms

        :return: dict of vms in multipass format
        """
        result = Shell.run("multipass list --format=json")
        #
        # TODO: relpace with json.loads
        #
        result = eval(result)['list']
        result_new_dict = {}
        for i in range(len(result)):
            result_new_dict[result[i]["name"]] = result[i]

        return result_new_dict

    def vm(self, **kwargs):
        """
        Lists the vms on the cloud

        :return: dict
        """
        result = self._vm()
        return self.update_dict(result, kind="vm")

    # IMPLEMENT
    # WRONG, shoudl this not use SHell.live so we can redirect and test ...
    def start(self, name=None):
        """
        start a node

        :param name: the unique node name
        :return:  The dict representing the node
        """

        banner(f"start {name}")
        os.system(f"multipass start {name}")
        print('\n')

        # Get the vm status.
        dict_result = self._get_vm_status(name)

        return dict_result

    # IMPLEMENT
    def delete(self, name="cloudmesh", purge=False):
        """
        Deletes the names instance

        :param name: The name
        :param purge: if set to tru also purges the instance
        :return: the dict of the deleted vm
        """

        if purge:
            # terminate and purge
            os.system(f"multipass delete {name} --purge")
        else:
            # terminate only
            os.system(f"multipass delete {name}")

        # Get the vm status.
        dict_result = self._get_vm_status(name)

        return dict_result

    # IMPLEMENT
    def list(self, **kwargs):
        """
        list all vm Instances

        :return: an array of dicts representing the nodes
        """

        # Already implemented by vm method
        return self.vm()

    # IMPLEMENT
    def shell(self, name="cloudmesh"):
        """
        log into the shell of instance

        :return: an empty string
        """
        banner("shell")

        os.system(f"multipass shell {name}")
        print("\n")
        return ""

    # IMPLEMENT
    def run(self, name="cloudmesh", command=None, executor="buffer"):
        """
        executes a command in a named multipass instance

        :param name: the name of the instance
        :param command: the command
        :param executor: one of live, buffer, os
        :return: only returned when using live or buffer

        live   = prints the output immediatly but also buffers it and returns it
                 at the end

        buffer = buffers the result and only returns it after the command has
                 executed.

        os =     just uses os.system and returns a "" at the end. This is good
                 for debugging

        """
        banner(f"run {name} {command}")
        # improve next line
        result = ""
        if executor == "buffer":
            result = Shell.live(f"multipass exec {name} -- {command}")
        elif executor == "buffer":
            result = Shell.run(f"multipass exec {name} -- {command}")
        elif executor == "os":
            os.system(f"multipass exec {name} -- {command}")
            print('\n')
        else:
            Console.error(
                "run: executor must be cloudmesh or os, found: {executor}")
        return result

    # IMPLEMENT, new method
    # TODO: docstring
    def get(self, key=None):
        """
        returns the variable with the given key name from multipass

        :param key: the key name
        :return:
        """
        result = ""
        if (key is not None):
            result = Shell.run(f"multipass get {key}")
        return result

    # IMPLEMENT, new method
    def set(self, key=None, value=None):
        """
        sets the multipass variable with the kename to value

        :param key: the name of the key
        :param value: the value to be set
        :return:
        """
        result = ""
        if (key is not None):
            result = Shell.run(f"multipass set {key} {value}")
        return result

    # IMPLEMENT
    def stop(self, name=None):
        """
        stops the node with the given name

        :param name:
        :return: The dict representing the node including updated status
        """

        # WRONG
        curr_status = self._get_vm_status(name)
        if (curr_status['status'] != "Stopped"):
            os.system(f"multipass stop {name}")

        # Get the vm status.
        dict_result = self._get_vm_status(name)

        return dict_result

    # IMPLEMENT
    def info(self, name=None):
        """
        gets the information of a node with a given name

        :param name:
        :return: The dict representing the node including updated status
        """

        result = self._info()
        result = [result[name]]
        return self.update_dict(result, kind="info")

    # IMPLEMENT
    def suspend(self, name=None):
        """
        suspends the node with the given name

        :param name: the name of the node
        :return: The dict representing the node
        """
        banner(f"suspend {name}")
        os.system(f"multipass suspend {name}")

        # Get the vm status.
        dict_result = self._get_vm_status(name)
        # raise NotImplementedError

        return dict_result

    # IMPLEMENT
    def resume(self, name=None):
        """
        resume the named node

        :param name: the name of the node
        :return: the dict of the node
        """
        banner(f"resume {name}")
        os.system(f"multipass start {name}")

        # Get the vm status.
        dict_result = self._get_vm_status(name)
        return dict_result
        # raise NotImplementedError
        # raise NotImplementedError

    # IMPLEMENT
    def destroy(self, name=None):
        """
        Destroys the node
        :param name: the name of the node
        :return: the dict of the node
        """
        banner(f"destroy {name}")

        return self.delete(name, purge=True)

    # IMPLEMENT
    # TODO: se the sample for defaults they are not idenitified
    #  from kwargs and passed along
    def create(self,
               name=None,
               image=None,
               size=None,
               timeout=360,
               group=None,
               **kwargs):
        """
        creates a named node

        :param group: a list of groups the vm belongs to
        :param name: the name of the node
        :param image: the image used
        :param size: the size of the image
        :param timeout: a timeout in seconds that is invoked in case the image
                        does not boot.
               The default is set to 3 minutes.
        :param kwargs: additional arguments passed along at time of boot
        :return:
        """
        """
        create one node
        """

        banner(f"create {name} {image}")
        #
        # TODO: shouls we not use shell.live?
        #
        os.system(f"multipass launch --name {name} {image}")

        # Get the vm status.
        dict_result = self._get_vm_status(name)

        return dict_result

    # DO NOT IMPLEMENT
    def set_server_metadata(self, name, **metadata):
        """
        sets the metadata for the server

        :param name: name of the fm
        :param metadata: the metadata
        :return:
        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def get_server_metadata(self, name):
        """
        gets the metadata for the server

        :param name: name of the fm
        :return:
        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def delete_server_metadata(self, name):
        """
        gets the metadata for the server

        :param name: name of the fm
        :return:
        """
        raise NotImplementedError

    # IMPLEMENT
    # TODO: pytest
    def rename(self, name=None, destination=None):
        """
        rename a node

        :param destination:
        :param name: the current name
        :return: the dict with the new name
        """
        Console.error("Renaming an instance is not yet supported by multipass")
        return ""

    # DO NOT IMPLEMENT
    def keys(self):
        """
        Lists the keys on the cloud

        :return: dict
        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def key_upload(self, key=None):
        """
        uploads the key specified in the yaml configuration to the cloud
        :param key:
        :return:
        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def key_delete(self, name=None):
        """
        deletes the key with the given name
        :param name: The name of the key
        :return:
        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def flavors(self, **kwargs):
        """
        Lists the flavors on the cloud

        :return: dict of flavors
        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def flavor(self, name=None):
        """
        Gets the flavor with a given name
        :param name: The name of the flavor
        :return: The dict of the flavor
        """
        raise NotImplementedError

    # IMPLEMENT
    def reboot(self, name=None):
        """
        Reboot a list of nodes with the given names

        :param name: A list of node names
        :return:  A list of dict representing the nodes
        """

        banner(f"reboot {name}")

        dict_result = self.stop(name)

        #
        # TODO: we ned to list the states we have in STATUS
        #
        if dict_result["status"] in "Stopped Suspended":
            # If the status is stopped or suspended then attempt to start.
            dict_result = self.start(name)
        else:
            # Something wrong..
            dict_result["status"] = "Error when stopping instance"

        return dict_result

    # DO NOT IMPLEMENT
    def attach_public_ip(self, name=None, ip=None):
        """
        adds a public ip to the named vm

        :param name: Name of the vm
        :param ip: The ip address
        :return:
        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def detach_public_ip(self, name=None, ip=None):
        """
        adds a public ip to the named vm

        :param name: Name of the vm
        :param ip: The ip address
        :return:
        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def delete_public_ip(self, ip=None):
        """
        Deletes the ip address

        :param ip: the ip address, if None than all will be deleted
        :return:
        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def list_public_ips(self, available=False):
        """
        Lists the public ip addresses.

        :param available: if True only those that are not allocated will be
            returned.

        :return:
        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def create_public_ip(self):
        """
        Creates a new public IP address to use

        :return: The ip address information
        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def find_available_public_ip(self):
        """
        Returns a single public available ip address.

        :return: The ip
        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def get_public_ip(self, name=None):
        """
        returns the public ip

        :param name: name of the server
        :return:
        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def list_secgroups(self, name=None):
        """
        List the named security group

        :param name: The name of the group, if None all will be returned
        :return:
        """

    # DO NOT IMPLEMENT
    def list_secgroup_rules(self, name='default'):
        """
        List the named security group

        :param name: The name of the group, if None all will be returned
        :return:
        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def upload_secgroup(self, name=None):
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def add_secgroup(self, name=None, description=None):
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def add_secgroup_rule(self,
                          name=None,  # group name
                          port=None,
                          protocol=None,
                          ip_range=None):
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def remove_secgroup(self, name=None):
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def add_rules_to_secgroup(self, name=None, rules=None):
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def remove_rules_from_secgroup(self, name=None, rules=None):
        raise NotImplementedError

    # IMPLEMENT, work with Gregor
    # see cloudmesh-openstack already implemented there
    def wait(self,
             vm=None,
             interval=None,
             timeout=None):
        """
        wais till the given VM can be logged into

        :param vm: name of the vm
        :param interval: interval for checking
        :param timeout: timeout
        :return:
        """
        # repeatedly tries run aof a knwpn command such as uname -a and
        # sees if it returns without error.
        # if it reaches timeout it fails
        # We may want to create a special static class for this as this is
        # the same likely for all clouds.
        # maybe just place in the ABC class or so as implemenattion so we
        # inherit
        # samee with ssh
        raise NotImplementedError
        return False

    # DO NOT IMPLEMENT
    def console(self, vm=None):
        """
        gets the output from the console

        :param vm: name of the VM
        :return:
        """
        raise NotImplementedError
        return ""

    # DO NOT IMPLEMENT
    def log(self, vm=None):
        raise NotImplementedError
        return ""

    def info(self, **kwargs):
        """
        Lists the info on the cloud

        :return: dict
        """
        result = self._info()
        return self.update_dict(result, kind="info")

    def _info(self):
        """
        an internal method that returns the info of all instances as a dict in
        multipass

        :return: dict of all instances in multipass
        """
        result = Shell.run("multipass info --all --format=json")
        #
        # TODO: relpace with json.loads
        #
        result = eval(result)['info']
        return result


if __name__ == "__main__":
    # excellent-titmouse is multipass instance name
    p = Provider()  # name="cloudmesh"
    p.vm()
    p.start()
    p.list()
    p.run("uname -r")
    p.images()
    p.delete()
    p.list()
