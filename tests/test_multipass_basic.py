###############################################################
# pytest -v --capture=no tests
# pytest -v --capture=no tests/test_multipass_basic.py
# pytest -v  tests/test_multipass_basic.py
# pytest -v --capture=no  tests/test_multipass_.py::Test_Multipass::<METHODNAME>
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


    def test_provider_init(self):
        HEADING()
        Benchmark.Start()
        self.provider = Provider()
        Benchmark.Stop()
        assert True
        Benchmark.Status(True)

    def test_provider_run_os(self):
        HEADING()

        self.provider = Provider()

        Benchmark.Start()
        result = self.provider.run(command="uname -a", executor="os")
        Benchmark.Stop()
        VERBOSE(result)

        # find a good assertion

        result = str(result)

        assert "18.04" in result
        Benchmark.Status(True)

    def test_provider_run_live(self):
        HEADING()

        self.provider = Provider()

        Benchmark.Start()
        result = self.provider.run(command="uname -a", executor="live")
        Benchmark.Stop()
        VERBOSE(result)

        # find a good assertion

        result = str(result)

        assert "18.04" in result
        Benchmark.Status(True)

    def test_provider_run_buffer(self):
        HEADING()

        self.provider = Provider()

        Benchmark.Start()
        result = self.provider.run(command="uname -a", executor="buffer")
        Benchmark.Stop()
        VERBOSE(result)

        # find a good assertion
        result = str(result)

        assert "18.04" in result
        Benchmark.Status(True)

    def test_info(self):
        HEADING()
        Benchmark.Start()
        result = Shell.execute("cms multipass info", shell=True)
        Benchmark.Stop()
        VERBOSE(result)
        assert result != None, "result cannot be null"
        Benchmark.Status(True)


    #
    # NOTHING BELOW THIS LINE
    #

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, tag=cloud)
