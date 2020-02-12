import os

from cloudmesh.common.util import banner
from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
import sys
import json
from pprint import pprint
from cloudmesh.common.DateTime import DateTime
from cloudmesh.common.Printer import Printer
from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC


# can be installed with pip install cloudmesh-common

class Provider(ComputeNodeABC):
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
    }

    def __init__(self, name="cloudmesh", cloud="multipass"):
        """

        :param cloud: The name of the cloud, by default multipass
        :param name: The name of the vm, by default, multipass
        """
        self.cloudtype = "multipass"
        self.cloud = cloud
        self.name = name # This is the name of the cloud and not the name of the instance

    # noinspection PyPep8Naming
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
        result = Shell.run("multipass find --format=json")
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
        result = Shell.run("multipass list --format=json")
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
        banner(f"delete {name}")

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
        banner("list")
        os.system("multipass ls")
        print('\n')

    # IMPLEMENT
    def shell(self, name="cloudmesh"):
        banner("shell")
        os.system(f"multipass shell {name}")
        print('\n')

    # IMPLEMENT
    def run(self, name="cloudmesh", command=None, executor="cloudmesh"):
        banner(f"run {name} {command}")
        # improve next line
        if executor == "cloudmesh":
            r = Shell.run(f"multipass exec {name} --  {command}")
        elif executor == "os":
            os.system(f"multipass exec {name} --  {command}")
            print('\n')
            result = ""
        else:
            Console.error("run: executor must be cloudmesh or os, found: {executor}")
        return result

    # IMPLEMENT
    def stop(self, name=None):
        """
        stops the node with the given name

        :param name:
        :return: The dict representing the node including updated status
        """

        banner(f"stop {name}")
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
        raise NotImplementedError

    # IMPLEMENT
    def suspend(self, name=None):
        """
        suspends the node with the given name

        :param name: the name of the node
        :return: The dict representing the node
        """
        raise NotImplementedError

    # IMPLEMENT
    def resume(self, name=None):
        """
        resume the named node

        :param name: the name of the node
        :return: the dict of the node
        """
        raise NotImplementedError

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

        banner(f"create {name}")
        os.system(f"multipass launch --name {name}")

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
    def rename(self, name=None, destination=None):
        """
        rename a node

        :param destination:
        :param name: the current name
        :return: the dict with the new name
        """
        # if destination is None, increase the name counter and use the new name
        raise NotImplementedError

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

        if (dict_result["status"] in "Stopped Suspended"):
            #If the status is stopped or suspended then attempt to start.
            dict_result = self.start(name)
        else:
            #Something wrong..
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
    def list_secgroup_rules(self, name='default'):
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
    def upload_secgroup(self, name=None):
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def add_rules_to_secgroup(self, name=None, rules=None):
        raise NotImplementedError

    # DO NOT IMPLEMENT
    def remove_rules_from_secgroup(self, name=None, rules=None):
        raise NotImplementedError

    # IMPLEMENT
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


if __name__ == "__main__":
    # excellent-titmouse is multipass instance name
    p = Provider() #name="cloudmesh"
    p.vm()
    p.start()
    p.list()
    p.run("uname -r")
    p.images()
    p.delete()
    p.list()

