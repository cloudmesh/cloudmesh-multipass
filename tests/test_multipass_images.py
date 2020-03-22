###############################################################
# pytest -v --capture=no tests/test_multipass_image.py
# pytest -v  tests/test_multipass_image.py
# pytest -v --capture=no  tests/test_multipass_image.py::Test_Multipass::<METHODNAME>
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


    def test_provider_init(self):
        HEADING()
        Benchmark.Start()
        self.provider = Provider()
        Benchmark.Stop()
        assert True
        Benchmark.Status(True)

    def test_provider_images(self):
        HEADING()

        self.provider = Provider()

        Benchmark.Start()
        result = self.provider.images()
        Benchmark.Stop()
        VERBOSE(result)

        result = str(result)

        assert "18.04" in result
        Benchmark.Status(True)

    def test_cms_images(self):
        HEADING()
        Benchmark.Start()
        result = Shell.execute("cms multipass images", shell=True)
        Benchmark.Stop()
        VERBOSE(result)
        result = str(result)

        assert "18.04" in result
        Benchmark.Status(True)



    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, tag=cloud)
