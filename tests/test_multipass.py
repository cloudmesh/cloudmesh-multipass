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

Benchmark.debug()

cloud= "local"

@pytest.mark.incremental
class TestMultipass:

    def test_help(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute("cms help multipass", shell=True)
        Benchmark.Stop()
        VERBOSE(result)

        assert "quit" in result
        assert "clear" in result

    def test_images(self):
        HEADING()
        Benchmark.Start()
        result = Shell.execute("cms multipass images", shell=True)
        Benchmark.Stop()
        VERBOSE(result)

        assert "18.04" in result

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, tag=cloud)

    def test_info(self):
        HEADING()
        Benchmark.Start()
        result = Shell.execute("cms multipass info", shell=True)
        Benchmark.Stop()
        VERBOSE(result)
        assert result != None, "result cannot be null"
