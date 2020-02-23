###############################################################
# pytest -v --capture=no tests/test_multipass.py
# pytest -v  tests/test_multipass.py
# pytest -v --capture=no  tests/test_multipass.py::Test_Multipass::<METHODNAME>
###############################################################
import pytest
from cloudmesh.common.Shell import Shell
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.multipass.Provider import Provider

Benchmark.debug()

cloud= "local"
instance="cloudmesh-test"

@pytest.mark.incremental
class TestMultipass:

    vm_name_prefix = "cloudmeshvm" #Note: multipass does not allow - or _ in vm name.

    def test_cms_help(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute("cms help multipass", shell=True)
        Benchmark.Stop()
        VERBOSE(result)

        assert " multipass create NAMES" in result
        Benchmark.Status(True)

    def test_cms_images(self):
        HEADING()
        Benchmark.Start()
        result = Shell.execute("cms multipass images", shell=True)
        Benchmark.Stop()
        VERBOSE(result)

        assert "18.04" in result
        Benchmark.Status(True)

    def test_provider_init(self):
        HEADING()
        Benchmark.Start()
        self.provider = Provider()
        Benchmark.Stop()
        assert True
        Benchmark.Status(True)

    def test_provider_images(self):
        HEADING()

        assert self.provider is not None

        Benchmark.Start()
        result = self.provider.images()
        Benchmark.Stop()
        VERBOSE(result)

        assert "18.04" in result
        Benchmark.Status(True)

    def test_provider_run_os(self):
        HEADING()

        assert self.provider is not None

        Benchmark.Start()
        result = self.provider.run(command="uname -a", executor="os")
        Benchmark.Stop()
        VERBOSE(result)

        # find a good assertion

        assert "18.04" in result
        Benchmark.Status(True)

    def test_provider_run_live(self):
        HEADING()

        assert self.provider is not None

        Benchmark.Start()
        result = self.provider.run(command="uname -a", executor="live")
        Benchmark.Stop()
        VERBOSE(result)

        # find a good assertion

        assert "18.04" in result
        Benchmark.Status(True)

    def test_provider_run_buffer(self):
        HEADING()

        assert self.provider is not None

        Benchmark.Start()
        result = self.provider.run(command="uname -a", executor="buffer")
        Benchmark.Stop()
        VERBOSE(result)

        # find a good assertion

        assert "18.04" in result
        Benchmark.Status(True)

    def test_cms_vm(self):
        HEADING()

        assert self.provider is not None

        Benchmark.Start()
        result = Shell.execute("cms multipass vm", shell=True)
        Benchmark.Stop()
        VERBOSE(result)
        
        assert "18.04" in result
        Benchmark.Status(True)

    def test_provider_vm(self):
        HEADING()

        assert self.provider is not None

        Benchmark.Start()
        result = self.provider.vm()
        Benchmark.Stop()
        VERBOSE(result)
        
        assert "18.04" in result
        Benchmark.Status(True)

    def test_cms_shell(self):
        HEADING()
        
        Benchmark.Start()
        Shell.execute(f"cms multipass launch --name={instance}", shell=True)
        result = Shell.execute(f"cms multipass shell {instance}", shell=True)
        Shell.execute(f"cms multipass delete {instance}",shell=True)
        Shell.execute(f"cms multipass purge",shell=True)
        Benchmark.Stop()
        VERBOSE(result)
        # assertion missing
        Benchmark.Status(True)

    def test_provider_shell(self):
        HEADING()
        
        Benchmark.Start()
        Shell.execute(f"cms multipass launch --name={instance}", shell=True)
        result = self.provider.shell(name=instance)
        Shell.execute(f"cms multipass delete {instance}",shell=True)
        Shell.execute(f"cms multipass purge",shell=True)
        Benchmark.Stop()
        VERBOSE(result)
        # assertion missing
        Benchmark.Status(True)

    def test_info(self):
        HEADING()
        Benchmark.Start()
        result = Shell.execute("cms multipass info", shell=True)
        Benchmark.Stop()
        VERBOSE(result)
        assert result != None, "result cannot be null"
        Benchmark.Status(True)

    def test_create(self):
        HEADING()
        vm_name = f"{self.vm_name_prefix}1"

        Benchmark.Start()
        result = Shell.execute(f"cms multipass create {vm_name}", shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert f'Launched: {vm_name}' in result, "Error creating instance"
        Benchmark.Status(True)

    def test_provider_create(self):
        HEADING()

        assert self.provider is not None

        vm_name = f"{self.vm_name_prefix}2"

        provider = Provider(vm_name)

        Benchmark.Start()
        result = provider.create(vm_name)
        Benchmark.Stop()
        VERBOSE(result)

        assert 'Running' in result['status'], "Error creating instance"
        Benchmark.Status(True)


    def test_create_with_options(self):
        HEADING()

        vm_name = f"{self.vm_name_prefix}3"

        Benchmark.Start()
        result = Shell.execute(f"cms multipass create {vm_name} --cpus=2 --size=3G --image=bionic --mem=1G", shell=True)
        Benchmark.Stop()
        VERBOSE(result)

        assert f'Launched: {vm_name}' in result, "Error creating instance"
        Benchmark.Status(True)

    def test_stop(self):
        HEADING()
        #Using 2 VMs to test_created usingn test_create* methods.
        vm_names = f"{self.vm_name_prefix}1,{self.vm_name_prefix}3"

        Benchmark.Start()
        result = Shell.execute(f"cms multipass stop {vm_names}", shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert 'Stopped' in result, "Error stopping instance"
        Benchmark.Status(True)

    def test_provider_stop(self):
        HEADING()

        assert self.provider is not None

        vm_name = f"{self.vm_name_prefix}2"
        provider = Provider(vm_name)

        Benchmark.Start()
        result = provider.stop(vm_name)
        Benchmark.Stop()

        VERBOSE(result)

        assert 'Stopped' in result['status'], "Error stopping instance"
        Benchmark.Status(True)

    def test_start(self):
        HEADING()
        #Using 2 VMs to test_created usingn test_create* methods.
        vm_names = f"{self.vm_name_prefix}1,{self.vm_name_prefix}3"

        Benchmark.Start()
        result = Shell.execute(f"cms multipass start {vm_names}", shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert 'Running' in result, "Error starting instance"
        Benchmark.Status(True)

    def test_provider_start(self):
        HEADING()

        assert self.provider is not None

        vm_name = f"{self.vm_name_prefix}2"
        provider = Provider(vm_name)

        Benchmark.Start()
        result = provider.start(vm_name)
        Benchmark.Stop()

        VERBOSE(result)

        assert 'Running' in result['status'], "Error starting instance"
        Benchmark.Status(True)

    def test_reboot(self):
        HEADING()

        assert self.provider is not None

        #Using 2 VMs to test_created usingn test_create* methods.
        vm_names = f"{self.vm_name_prefix}1,{self.vm_name_prefix}3"

        Benchmark.Start()
        result = Shell.execute(f"cms multipass reboot {vm_names}", shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert 'Running' in result, "Error rebooting instance"

    def test_provider_reboot(self):
        HEADING()

        assert self.provider is not None

        vm_name = f"{self.vm_name_prefix}2"
        provider = Provider(vm_name)

        Benchmark.Start()
        result = provider.reboot(vm_name)
        Benchmark.Stop()

        VERBOSE(result)

        assert 'Running' in result['status'], "Error rebooting instance"
        Benchmark.Status(True)

    def test_delete(self):
        HEADING()
        #Using 2 VMs to test_created usingn test_create* methods.
        vm_names = f"{self.vm_name_prefix}1,{self.vm_name_prefix}3"

        Benchmark.Start()
        result = Shell.execute(f"cms multipass delete {vm_names}", shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert 'deleted' in result, "Error deleting instance"
        Benchmark.Status(True)

    def test_provider_delete(self):
        HEADING()

        assert self.provider is not None

        vm_name = f"{self.vm_name_prefix}2"
        provider = Provider(vm_name)

        Benchmark.Start()
        result = provider.delete(vm_name)
        Benchmark.Stop()

        VERBOSE(result)

        assert 'deleted' in result['status'], "Error deleting instance"
        Benchmark.Status(True)

    def test_destroy(self):
        HEADING()
        #Using 2 VMs to test_created usingn test_create* methods.
        vm_names = f"{self.vm_name_prefix}1,{self.vm_name_prefix}3"

        Benchmark.Start()
        result = Shell.execute(f"cms multipass destroy {vm_names}", shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert 'destroyed' in result, "Error destroying instance"
        Benchmark.Status(True)

    def test_provider_destroy(self):
        HEADING()

        assert self.provider is not None

        vm_name = f"{self.vm_name_prefix}2"
        provider = Provider(vm_name)

        Benchmark.Start()
        result = provider.destroy(vm_name)
        Benchmark.Stop()

        VERBOSE(result)

        assert 'destroyed' in result['status'], "Error destroying instance"
        Benchmark.Status(True)

    #
    # NOTHING BELOW THIS LINE
    #

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, tag=cloud)
