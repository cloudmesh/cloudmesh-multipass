###############################################################
# pytest -v --capture=no tests/test_multipass.py
# pytest -v  tests/test_multipass.py
# pytest -v --capture=no  tests/test_multipass.py:Test_Multipass.<METHODNAME>
###############################################################
import pytest
from cloudmesh.common.Shell import Shell
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.multipass.Provider import Provider

Benchmark.debug()

cloud= "local"

@pytest.mark.incremental
class TestMultipass:

    def test_cms_help(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute("cms help multipass", shell=True)
        Benchmark.Stop()
        VERBOSE(result)

        assert "quit" in result
        assert "clear" in result

    def test_cms_images(self):
        HEADING()
        Benchmark.Start()
        result = Shell.execute("cms multipass images", shell=True)
        Benchmark.Stop()
        VERBOSE(result)

        assert "18.04" in result

    def test_provider_init(self):
        HEADING()
        Benchmark.Start()
        self.provider = Provider()
        Benchmark.Stop()
        assert True


    def test_provider_images(self):
        HEADING()

        Benchmark.Start()
        result = self.provider.images()
        Benchmark.Stop()
        VERBOSE(result)

        assert "18.04" in result

    def test_provider_run_os(self):
        HEADING()

        Benchmark.Start()
        result = self.provider.run(command="uname -a", executor="os")
        Benchmark.Stop()
        VERBOSE(result)

        # find a good assertion

        assert "18.04" in result

    def test_provider_run_live(self):
        HEADING()

        Benchmark.Start()
        result = self.provider.run(command="uname -a", executor="live")
        Benchmark.Stop()
        VERBOSE(result)

        # find a good assertion

        assert "18.04" in result

    def test_provider_run_buffer(self):
        HEADING()

        Benchmark.Start()
        result = self.provider.run(command="uname -a", executor="buffer")
        Benchmark.Stop()
        VERBOSE(result)

        # find a good assertion

        assert "18.04" in result
        
    def test_cms_vm(self):
        HEADING()
        
        Benchmark.Start()
        result = Shell.execute("cms multipass vm", shell=True)
        Benchmark.Stop()
        VERBOSE(result)
        
        assert "18.04" in result
        
    def test_provider_vm(self):
        HEADING()
        
        Benchmark.Start()
        result = self.provider.vm()
        Benchmark.Stop()
        VERBOSE(result)
        
        assert "18.04" in result

    def test_cms_shell(self):
        HEADING()
        
        Benchmark.Start()
        result = Shell.execute("cms multipass shell", shell=True)
        Benchmark.Stop()
        VERBOSE(result)
        
    def test_provider_shell(self):
        HEADING()
        
        Benchmark.Start()
        result = self.provider.shell()
        Benchmark.Stop()
        VERBOSE(result)

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, tag=cloud)
