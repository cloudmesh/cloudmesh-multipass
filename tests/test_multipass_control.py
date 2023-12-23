###############################################################
# pytest -v --capture=no tests
# pytest -v --capture=no tests/test_multipass_general.py
# pytest -v  tests/test_multipass_general.py
# pytest -v --capture=no  tests/test_multipass_general.py::Test_Multipass::<METHODNAME>
###############################################################
import pytest
from cloudmesh.common.Shell import Shell
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.multipass.Provider import Provider

Benchmark.debug()

cloud = "local"
instance = "cloudmesh-test"

# THIS DOES NOT INCLUDE ALL MISSING TEST JUST ONE SO GREGOR KNOWS THIS HAS NOT
# BEEN DONE

"""
multipass mount SOURCE DESTINATION [--dryrun]
      multipass umount SOURCE [--dryrun]
      multipass transfer SOURCE DESTINATION [--dryrun]
      multipass set key=VALUE [--dryrun]
      multipass get [key] [--dryrun]
"""


@pytest.mark.incremental
class TestMultipass:
    vm_name_prefix = "cloudmeshvm"  # Note: multipass does not allow - or _ in vm name.

    def test_multipass(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute("cms help", shell=True)
        Benchmark.Stop()
        VERBOSE(result)

        assert "multipass" in result
        Benchmark.Status(True)

    def test_provider_version(self):
        HEADING()

        self.provider = Provider()

        Benchmark.Start()
        result = self.provider.version()
        Benchmark.Stop()
        VERBOSE(result)

        result = str(result)

        print("AAA", result, "BBB")

        assert "multipass" in result
        assert "multipassd" in result
        assert ":" in result
        assert "." in result
        assert "}" in result
        assert "{" in result

        Benchmark.Status(True)

    def test_cms_set(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute("cms set cloud=multipass", shell=True)
        Benchmark.Stop()
        VERBOSE(result)

        assert "cloud" in result
        assert "multipass" in result
        Benchmark.Status(True)

    # def test_provider_set(self):
    #     HEADING()

    #     self.provider = Provider()

    #     Benchmark.Start()
    #     result = self.provider.set()
    #     Benchmark.Stop()
    #     VERBOSE(result)

    #     result = str(result)
    #     print (result)

    #     assert "missing" in result
    #     Benchmark.Status(True)

    def test_cms_get(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute("cms get", shell=True)
        Benchmark.Stop()
        VERBOSE(result)

        assert "missing" in result
        Benchmark.Status(True)

    # def test_provider_get(self):
    #     HEADING()

    #     self.provider = Provider()

    #     Benchmark.Start()
    #     result = self.provider.get()
    #     Benchmark.Stop()
    #     VERBOSE(result)

    #     result = str(result)

    #     assert "missing" in result
    #     Benchmark.Status(True)

    # def test_cms_mount(self):
    #     HEADING()

    #     Benchmark.Start()
    #     result = Shell.execute("cms mount", shell=True)
    #     Benchmark.Stop()
    #     VERBOSE(result)

    #     assert "missing" in result
    #     Benchmark.Status(True)

    # def test_provider_mount(self):
    #     HEADING()

    #     self.provider = Provider()

    #     Benchmark.Start()
    #     result = self.provider.mount()
    #     Benchmark.Stop()
    #     VERBOSE(result)

    #     result = str(result)

    #     assert "missing" in result
    #     Benchmark.Status(True)

    # def test_cms_transfer(self):
    #     HEADING()

    #     Benchmark.Start()
    #     result = Shell.execute("cms transfer", shell=True)
    #     Benchmark.Stop()
    #     VERBOSE(result)

    #     assert "missing" in result
    #     Benchmark.Status(True)

    # def test_provider_transfer(self):
    #     HEADING()

    #     self.provider = Provider()

    #     Benchmark.Start()
    #     result = self.provider.transfer()
    #     Benchmark.Stop()
    #     VERBOSE(result)

    #     result = str(result)

    #     assert "missing" in result
    #     Benchmark.Status(True)

    #
    # NOTHING BELOW THIS LINE
    #

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, tag=cloud)
