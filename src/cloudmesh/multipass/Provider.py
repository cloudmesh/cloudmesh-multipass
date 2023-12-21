import json
import os

from cloudmesh.abstract.ComputeNodeABC import ComputeNodeABC
from cloudmesh.common.DateTime import DateTime
from cloudmesh.common.Printer import Printer
from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.util import banner
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.util import path_expand
from yamldb.YamlDB import YamlDB
from tabulate import tabulate
import yaml

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

# multipass mount
# multipass transfer

"""
  delete    Delete instances
  exec      Run a command on an instance
  find      Display available images to create instances from
  get       Get a configuration setting
  help      Display help about a command
  info      Display information about instances
  launch    Create and start an Ubuntu instance
  list      List all available instances
  mount     Mount a local directory in the instance
  purge     Purge all deleted instances permanently
  recover   Recover deleted instances
  restart   Restart instances
  set       Set a configuration setting
  shell     Open a shell on a running instance
  start     Start instances
  stop      Stop running instances
  suspend   Suspend running instances
  transfer  Transfer files between the host and instances
  umount    Unmount a directory from an instance
  version   Show version details

"""


class Provider(ComputeNodeABC):
    def __init__(self, name="multipass"):
        """Initializes the multipass provider. The default parameters are read
        from the configuration file that is defined in yaml format.

        Args:
            name: The name of the provider as defined in the yaml file
            configuration: The location of the yaml configuration file
        """
        #
        # The following will be added later once we have identified how to
        # configure multipass from cloudmesh.yaml. This requires understanding
        # the get and set methods and setting defaults for sizes
        #
        # conf = Config(configuration)["cloudmesh"]
        # super().__init__(name)
        #
        self.kind = "multipass"

        self.cache = path_expand("~/.cloudmesh/multipass")
        self.image_cache = path_expand(f"{self.cache}/images.json")
        self.vm_cache = path_expand(f"{self.cache}/vm.json")

        self.cloudtype = "multipass"
        self.cloud = name
        self.config = None
        self.create_cache_directory()
        self.config = YamlDB(filename=path_expand("~/.cloudmesh/cloud.yaml"))

    def test(self):
        print(self.config)

    def better_tabulate(self, data, output="table", headers=None, order=None, **kwargs):
        if output == "table":
            tablefmt = "pretty"
        else:
            tablefmt = output

        if kwargs is None:
            kwargs = {}
        if "tablfmt" not in kwargs:
            kwargs["tablefmt"] = tablefmt

        if output == "json":
            return json.dumps(data, indent=4)
        elif output == "yaml":
            return yaml.dump(data, indent=4)
        else:
            if headers is None:
                headers = list(data[0].keys())
            if order is not None:
                table_data = [[item[key] for key in order] for item in data]
                table = tabulate(table_data, headers=headers, **kwargs)
            else:
                table = tabulate(data, headers=headers, **kwargs)
        return table

    def defaults(self, output="table"):
        data = self.config["cloudmesh.cloud.multipass.alias.vm"].copy()

        data = [{**item, "alias": key} for key, item in data.items()]

        if output in ["json", "yaml"]:
            print(self.better_tabulate(data, output=output))
        else:
            order = ["alias", "id", "cpus", "disk", "memory"]
            headers = ["Name", "OS", "CPUs", "Disk", "Memory"]

            table_data = [[item[key] for key in order] for item in data]

            table = self.better_tabulate(
                table_data,
                headers=headers,
                numalign="right",
                stralign="right",
                output=output,
            )
            print(table)

    def create_cache_directory(self):
        if not os.path.exists(self.cache):
            os.makedirs(self.cache)

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
            "order": ["cm.name", "cm.cloud", "ipv4", "name", "release", "state"],
            "header": ["Name", "Cloud", "Address", "Name", "Release", "State"],
        },
        "image": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name", "os", "release", "remote", "version", "aliases"],
            "header": ["Name", "OS", "Release", "Remote", "Version", "Alias"],
        },
        "info": {
            "sort_keys": ["cm.name"],
            "order": [
                "name",
                "state",
                "images_release",
                "memory",
                "mounts",
                "ipv4",
                "release",
                "image_hash",
            ],
            "header": [
                "Name",
                "State",
                "Image Release",
                "Memory",
                "Mounts",
                "Ipv4",
                "Release",
                "Image Hash",
            ],
        },
    }

    # please add a status here if there is one that you observe. WHat are all
    # the States form multipass?

    STATUS = ["UNKOWN"]

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

            order = self.output[kind]["order"]  # not pretty
            header = self.output[kind]["header"]  # not pretty
            # humanize = self.output[kind]['humanize']  # not pretty
            print(
                Printer.write(
                    data,
                    sort_keys=["name"],
                    order=order,
                    header=header,
                    output=output,
                    # humanize=humanize
                )
            )
        else:
            print("else")
            print(Printer.write(data, output=output))

    def remove_spinner(self, str):
        line = str
        line.repalace("\\08-", "")
        line.repalace("\\08|", "")
        line.repalace("\\08\\\\", "")
        line.repalace("\\08/", "")
        return line

    def update_dict(self, elements, kind=None):
        """converts the dict into a list

        Args:
            elements: the list of original dicts. If elements is a
                single dict a list with a single element is returned.
            kind: for some kinds special attributes are added. This
                includes key, vm, image, flavor.

        Returns:
            The list with the modified dicts
        """

        if elements is None:
            return None

        d = []
        for key, entry in elements.items():
            entry["name"] = key

            if "cm" not in entry:
                entry["cm"] = {}

            # if kind == 'ip':
            #    entry['name'] = entry['floating_ip_address']

            entry["cm"].update(
                {
                    "kind": kind,
                    "driver": self.cloudtype,
                    "cloud": self.cloud,
                    "name": key,
                }
            )

            if kind == "vm":
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

            elif kind == "image":
                entry["cm"]["created"] = entry["updated"] = str(DateTime.now())

            # elif kind == 'version':

            #    entry["cm"]["created"] = str(DateTime.now())

            d.append(entry)
        return d

        # IMPLEMENT, new method

    def version(self):
        """returns just the version

        Returns:
            version dict
        """

        d = {"name": self.kind, "multipass": None, "multipassd": None}
        result = Shell.run(f"multipass version")
        if result is not None:
            for line in result.splitlines():
                line = line.strip().replace("multipass  ", "multipass ")
                key, value = line.split(" ", 1)
                d[key] = value

        return d

    # New method to return vm status
    # TODO: docstring
    def _get_vm_status(self, name=None) -> dict:
        dict_result = {}
        result = Shell.run(f"multipass info {name} --format=json")

        if f'instance "{name}" does not exist' in result:
            dict_result = {"name": name, "status": "instance does not exist"}
        else:
            result = json.loads(result)
            dict_result = {"name": name, "status": result["info"][name]["state"]}

        return dict_result

    def images(self, refresh=False, purge=False):
        """Lists the images on the cloud

        Returns:
            dict
        """
        if purge:
            os.remove(self.image_cache)
            return None
        elif refresh or not os.path.exists(self.image_cache):
            # get online
            result = Shell.run("multipass find --format=json")
            data = json.loads(result)["images"]
            new_data = []
            for key in data:
                new_item = data[key]
                new_item["cm.name"] = new_item["release"].replace(" ", "-").lower()
                new_data.append(new_item)
            with open(self.image_cache, "w") as f:
                json.dump(new_data, f, indent=4)
        else:
            # get from cache
            with open(self.image_cache) as f:
                data = json.load(f)
            new_data = data

        return new_data

    def image(self, name=None):
        """Gets the image with a given name

        Args:
            name: The name of the image

        Returns:
            the dict of the image
        """
        result = self._images()
        result = [result[name]]
        return self.update_dict(result, kind="image")

    def _vm(self):
        """internal method that returns the dict of all vms

        Returns:
            dict of vms in multipass format
        """
        result = Shell.run("multipass list --format=json")
        #
        # TODO: relpace with json.loads
        #
        results = json.loads(result)
        dict_results = {"vms": results["list"]}

        return dict_results

    def vm(self, **kwargs):
        """Lists the vms on the cloud

        Returns:
            dict
        """
        result = self._vm()
        return self.update_dict(result, kind="vm")

    # IMPLEMENT
    def start(self, name=None):
        """start a node

        Args:
            name: the unique node name

        Returns:
            The dict representing the node
        """

        banner(f"start {name}")

        dict_result = {}
        result = Shell.live(f"multipass start {name}")

        if result["status"] > 0:
            dict_result = {"name": name, "status": "Error when starting instance"}
        else:
            # Get the vm status.
            dict_result = self._get_vm_status(name)

        return dict_result

    # IMPLEMENT
    def delete(self, name=None, purge=True):
        """Deletes the names instance

        Args:
            name: The name
            purge: if set to tru also purges the instance

        Returns:
            the dict of the deleted vm
        """

        banner(f"delete {name}")

        dict_result = {}
        if purge:
            # terminate and purge
            result = Shell.live(f"multipass delete {name} --purge")
            if result["status"] > 0:
                dict_result = {
                    "name": name,
                    "status": "Error when deleting/destroying instance",
                }
            else:
                dict_result = {
                    "name": name,
                    "status": "Instance destroyed (deleted and purged)",
                }

        else:
            # terminate only
            result = Shell.live(f"multipass delete {name}")
            if result["status"] > 0:
                dict_result = {
                    "name": name,
                    "status": "Error when deleting/destroying instance",
                }
            else:
                dict_result = {"name": name, "status": "Instance deleted"}

        return dict_result

    # IMPLEMENT
    def list(self, **kwargs):
        """list all vm Instances

        Returns:
            an array of dicts representing the nodes
        """

        # Already implemented by vm method
        return self.vm()

    # IMPLEMENT
    def shell(self, name="cloudmesh"):
        """log into the shell of instance

        Returns:
            an empty string
        """
        banner("shell")

        os.system(f"multipass shell {name}")
        print("\n")
        return ""

    # IMPLEMENT, POSSIBLE BUG wilth live
    def run(self, name="cloudmesh", command=None, executor="buffer"):
        """executes a command in a named multipass instance

        Args:
            name: the name of the instance
            command: the command
            executor: one of live, buffer, os

        Returns:
            only returned when using live or buffer

        live   = prints the output immediatly but also buffers it and returns
                 it at the end

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
            result = self.remove_spinner(result)
        elif executor == "buffer":
            result = Shell.run(f"multipass exec {name} -- {command}")
            result = self.remove_spinner(result)
        elif executor == "os":
            os.system(f"multipass exec {name} -- {command}")
            print("\n")
        else:
            Console.error("run: executor must be cloudmesh or os, found: {executor}")
        return result

    # IMPLEMENT, new method
    def get(self, key=None):
        """returns the variable with the given key name from multipass

        Args:
            key: the key name

        Returns:

        """
        result = ""
        if key is not None:
            result = Shell.run(f"multipass get {key}")
        return result

    # IMPLEMENT, new method
    def set(self, key=None, value=None):
        """sets the multipass variable with the kename to value

        Args:
            key: the name of the key
            value: the value to be set

        Returns:

        """
        result = ""
        if key is not None:
            result = Shell.run(f"multipass set {key} {value}")
        return result

    # IMPLEMENT
    def stop(self, name=None):
        """stops the node with the given name

        :param name of the instance to stop

        Returns:
            The dict representing the node including updated status
        """
        banner(f"stop {name}")

        dict_result = {}
        result = Shell.live(f"multipass stop {name}")

        if result["status"] > 0:
            dict_result = {"name": name, "status": "Error when stopping instance"}
        else:
            # Get the vm status.
            dict_result = self._get_vm_status(name)

        return dict_result

    # IMPLEMENT
    def info(self, name=None):
        """gets the information of a node with a given name

        Args:
            name

        Returns:
            The dict representing the node including updated status
        """

        result = self._info()
        result = [result[name]]
        return self.update_dict(result, kind="info")

    # IMPLEMENT
    def suspend(self, name=None):
        """suspends the node with the given name

        Args:
            name: the name of the node

        Returns:
            The dict representing the node
        """
        banner(f"suspend {name}")
        os.system(f"multipass suspend {name}")

        # Get the vm status.
        dict_result = self._get_vm_status(name)

        return dict_result

    # IMPLEMENT
    def resume(self, name=None):
        """resume the named node

        Args:
            name: the name of the node

        Returns:
            the dict of the node
        """
        banner(f"resume {name}")
        os.system(f"multipass start {name}")

        # Get the vm status.
        dict_result = self._get_vm_status(name)
        return dict_result

    # IMPLEMENT
    def destroy(self, name=None):
        """Destroys the node

        Args:
            name: the name of the node

        Returns:
            the dict of the node
        """
        banner(f"destroy {name}")

        return self.delete(name, purge=True)

    # IMPLEMENT
    # TODO: se the sample for defaults they are not idenitified
    #  from kwargs and passed along

    def create(
        self,
        name: str = None,
        image: str = None,
        size: str = None,
        timeout: int = 360,
        group: str = None,
        memory: str = None,
        cpus: str = None,
        disk: str = None,
        cloud_init: str = None,
        dryrun: bool = False,
        cloudinit: str = None,
        network: str = None,
        bridged: bool = False,
        mount: str = None,
        **kwargs,
    ):
        """
        Create a resource with the given parameters.

        Args:
            name (str): The name of the resource.
            image (str): The image to use for the resource.
            size (str): The size of the resource.
            timeout (int): The timeout duration in seconds (default is 360 seconds).
            group (List[str]): A list of groups associated with the resource.
            memory (str): The memory configuration for the resource.
            cpus (str): The number of CPUs for the resource.
            disk (str): The disk configuration for the resource.
            cloud_init (str): The path to the cloud initialization file.
            dryrun (bool): If True, perform a dry run without creating the resource.
            cloudinit (str): The path or URL to the cloud initialization file.
            network (str): The network configuration for the resource.
            bridged (bool): If True, use bridged networking.
            mount (str): The source path for mounting.
            **kwargs (Any): Additional keyword arguments for customization.

        Returns:
            dict: A dictionary containing information about the created resource.
        """

        # multipass create NAMES [--image=IMAGE]
        #                    [--size=SIZE]
        #                    [--memory=MEMORY]
        #                    [--cpus=CPUS]
        #                    [--disk=DISK]
        #                    [--cloud-init=FILE]
        #                    [--dryrun]
        #                    [--cloudinit=FILE_OR_URL]
        #                    [--network=NETWORK]
        #                    [--bridged]
        #                    [--mount=SOURCE]
        #                    [--timeout=TIMEOUT]
        #                    [--image=IMAGE]

        banner(f"create {name} using image {image}")

        templates = self.config["cloudmesh.cloud.multipass.alias.vm"]

        if name in templates:
            image = templates[name]["image"]

        defined_parameters = {
            "name": name or "primary",
            "image": image or "lts",
            "timeout": timeout,
            "group": group,
            "memory": memory,
            "cpus": cpus,
            "disk": disk,
            "cloud_init": cloud_init,
            "dryrun": dryrun,
            "cloudinit": cloudinit,
            "network": network,
            "bridged": bridged,
            "mount": mount,
        }

        parameters = []
        for key, value in defined_parameters.items():
            if value is not None:
                if type(value) is list and len(value) == 0:
                    pass
                else:
                    parameter_string = f"--{key}={value}"
                    parameters.append(parameter_string)

        s = " ".join(parameters)
        print(s)

        return ""

        arguments = dotdict(kwargs)
        memory = arguments.memory
        cpu = arguments.cpus
        disk = arguments.disk
        cloud_init = arguments.cloud_init

        command = f"multipass launch --name {name}"

        # Add options to create command
        if cpu is not None:
            command = command + f" --cpus {cpu}"

        if memory is not None:
            command = command + f" --memory {memory}"

        if size is not None:
            command = command + f" --disk {size}"

        if cloud_init is not None:
            command = command + f" --cloud-init {cloud_init}"

        if image is not None:
            command = f"{command} {image}"

        # result = Shell.live(command, )  # ?
        os.system(command)

        # Get the vm status.
        dict_result = self._get_vm_status(name)

        return dict_result

    # DO NOT IMPLEMENT
    def set_server_metadata(self, name, **metadata):
        """sets the metadata for the server

        Args:
            name: name of the fm
            **metadata: the metadata

        Returns:

        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def get_server_metadata(self, name):
        """gets the metadata for the server

        Args:
            name: name of the fm

        Returns:

        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def delete_server_metadata(self, name):
        """gets the metadata for the server

        Args:
            name: name of the fm

        Returns:

        """
        raise NotImplementedError

    # IMPLEMENT
    # TODO: pytest
    def rename(self, old_name=None, new_name=None):
        """rename a node

        Args:
            destination
            name: the current name

        Returns:
            the dict with the new name
        """
        result = Shell.run(f"multipass info {old_name} --format=json")
        result = json.load(result)
        result["info"][new_name] = result["info"].pop(old_name)
        dict_results = {"info": {result["info"][new_name]}}

        return dict_results

    # DO NOT IMPLEMENT
    def keys(self):
        """Lists the keys on the cloud

        Returns:
            dict
        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def key_upload(self, key=None):
        """uploads the key specified in the yaml configuration to the cloud

        Args:
            key

        Returns:

        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def key_delete(self, name=None):
        """deletes the key with the given name

        Args:
            name: The name of the key

        Returns:

        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def flavors(self, **kwargs):
        """Lists the flavors on the cloud

        Returns:
            dict of flavors
        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def flavor(self, name=None):
        """Gets the flavor with a given name

        Args:
            name: The name of the flavor

        Returns:
            The dict of the flavor
        """
        raise NotImplementedError

    # IMPLEMENT, POSSIBLE BUG wilth live
    def reboot(self, name=None):
        """Reboot a list of nodes with the given names

        Args:
            name: name of instance to reboot

        Returns:
            A list of dict representing the nodes
        """

        banner(f"reboot {name}")

        # Shell.live(f"multipass restart {name}")
        os.system(f"multipass restart {name}")

        dict_result = self._get_vm_status(name)

        return dict_result

    # DO NOT IMPLEMENT
    def attach_public_ip(self, name=None, ip=None):
        """adds a public ip to the named vm

        Args:
            name: Name of the vm
            ip: The ip address

        Returns:

        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def detach_public_ip(self, name=None, ip=None):
        """adds a public ip to the named vm

        Args:
            name: Name of the vm
            ip: The ip address

        Returns:

        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def delete_public_ip(self, ip=None):
        """Deletes the ip address

        Args:
            ip: the ip address, if None than all will be deleted

        Returns:

        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def list_public_ips(self, available=False):
        """Lists the public ip addresses.

        Args:
            available: if True only those that are not allocated will be
                returned.

        Returns:

        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def create_public_ip(self):
        """Creates a new public IP address to use

        Returns:
            The ip address information
        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def find_available_public_ip(self):
        """Returns a single public available ip address.

        Returns:
            The ip
        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def get_public_ip(self, name=None):
        """returns the public ip

        Args:
            name: name of the server

        Returns:

        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def list_secgroups(self, name=None):
        """List the named security group

        Args:
            name: The name of the group, if None all will be returned

        Returns:

        """

    # DO NOT IMPLEMENT
    def list_secgroup_rules(self, name="default"):
        """List the named security group

        Args:
            name: The name of the group, if None all will be returned

        Returns:

        """
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def upload_secgroup(self, name=None):
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def add_secgroup(self, name=None, description=None):
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def add_secgroup_rule(
        self, name=None, port=None, protocol=None, ip_range=None  # group name
    ):
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
    def wait(self, vm=None, interval=None, timeout=None):
        """wais till the given VM can be logged into

        Args:
            vm: name of the vm
            interval: interval for checking
            timeout: timeout

        Returns:

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
        """gets the output from the console

        Args:
            vm: name of the VM

        Returns:

        """
        raise NotImplementedError
        return ""

    # DO NOT IMPLEMENT
    def log(self, vm=None):
        raise NotImplementedError
        return ""

    def info(self, **kwargs):
        """Lists the info on the cloud

        Returns:
            dict
        """
        result = self._info()
        return self.update_dict(result, kind="info")

    def _info(self):
        """an internal method that returns the info of all instances as a dict in
        multipass

        Returns:
            dict of all instances in multipass
        """
        result = Shell.run("multipass info --all --format=json")
        #
        # TODO: relpace with json.loads
        #
        result = eval(result)["info"]
        return result

    # implement
    def mount(self, name="cloudmesh", source=None, destination=None):
        """mounts the sourse into the instance at the given destination

        TODO: proper docstring
        """
        result = ""
        if (source is not None) and (source is not None) and (name is not None):
            result = Shell.run(f"multipass mount --name={name} {source} {destination}")
        else:
            Console.error("make sure to specify all attributes")
            return ""
        # TODO: this should return the newly mounted volume as cloudmesh json
        return result

    # implement
    def umount(self, name="cloudmesh", path=None):
        """Unmount a directory from an instance.

        TODO: propper docstring

        Returns:

        """
        raise NotImplementedError

    # implement
    def transfer(self, name="cloudmesh", source=None, destination=None, recursive=True):
        """copies files or entire directories into the instance

        TODO: proper docstring
        """
        # you may need to use glob for dirs (recursively)
        # just create a glob and put it in a list.
        result = ""
        if None not in (source, name):
            result = Shell.run(
                f"multipass transfer --name={name} {source} {destination}"
            )
        else:
            Console.error("make sure to specify all attributes")
            return ""
        # TODO: this should return the newly mounted volume as cloudmesh json
        return result


if __name__ == "__main__":
    # excellent-titmouse is multipass instance name
    p = Provider()  # name="cloudmesh"
    # p.vm()
    # p.start("testvm")
    # p.stop("testvm")
    # p.vm()
    # p.run("uname -r")
    # p.images()
    # p.delete("testvm")
    # p.vm()
    # p.list()
