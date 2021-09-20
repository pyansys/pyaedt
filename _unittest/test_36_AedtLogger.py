try:
    import pytest
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest
# Setup paths for module imports
from _unittest.conftest import scratch_path
import gc

# Import required modules
from pyaedt import Hfss
from pyaedt.generic.filesystem import Scratch


class TestClass:
    def setup_class(self):
        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            self.aedtapp = Hfss(new_desktop_session=True)

    def teardown_class(self):
        assert self.aedtapp.close_project(self.aedtapp.project_name)
        self.local_scratch.remove()
        gc.collect()

    def test_01_Desktop(self):
        logger = self.aedtapp.logger
        #The default logger level is DEBUGGING.
        logger.global_logger.info("Debug message for testing.")
        logger.global_logger.info("Info message for testing.")
        logger.global_logger.warning("Warning message for testing.")
        logger.global_logger.error("Error message for testing.")
        logger.global_logger.info("Critical message for testing.")
        assert logger.get_messages() == "Warning"
        logger.clear_messages()
        assert logger.get_messages() == ""
        assert True
