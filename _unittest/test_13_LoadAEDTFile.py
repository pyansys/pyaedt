# Setup paths for module imports
from _unittest.conftest import local_path, scratch_path, desktop_version

# Import required modules
from pyaedt.generic.filesystem import Scratch
from pyaedt.generic.LoadAEDTFile import load_entire_aedt_file
from pyaedt import Hfss
import base64
import filecmp
import os
import sys
import gc


def _write_jpg(design_info, scratch):
    """writes the jpg Image64 property of the design info
    to a temporary file and returns the filename"""
    filename = os.path.join(scratch, design_info["DesignName"] + ".jpg")
    image_data_str = design_info["Image64"]
    with open(filename, "wb") as f:
        if sys.version_info.major == 2:
            bytes = bytes(image_data_str).decode("base64")
        else:
            bytes = base64.decodebytes(image_data_str.encode("ascii"))
        f.write(bytes)
    return filename


class TestHFSSProjectFile:
    def setup_class(self):
        with Scratch(scratch_path) as self.local_scratch:
            hfss_file = os.path.join(local_path, "example_models", "Coax_HFSS.aedt")
            self.project_dict = load_entire_aedt_file(hfss_file)

    def teardown_class(self):
        self.local_scratch.remove()

    def test_01_check_top_level_keys(self):
        assert list(self.project_dict.keys()) == ["AnsoftProject", "AllReferencedFilesForProject", "ProjectPreview"]

    def test_02_check_design_info(self):
        design_info = self.project_dict["ProjectPreview"]["DesignInfo"]
        # there is one design in this aedt file, so DesignInfo will be a dict
        assert isinstance(design_info, dict)
        assert design_info["Factory"] == "HFSS"
        assert design_info["DesignName"] == "HFSSDesign"
        assert design_info["IsSolved"] == False
        jpg_file = _write_jpg(design_info, self.local_scratch.path)
        assert filecmp.cmp(jpg_file, os.path.join(local_path, "example_models", "Coax_HFSS.jpg"))


class TestProjectFileWithBinaryContent:
    def test_01_check_can_load_aedt_file_with_binary_content(self):
        aedt_file = os.path.join(local_path, "example_models", "assembly.aedt")
        # implicitly this will test to make sure no exception is thrown by load_entire_aedt_file
        self.project_dict = load_entire_aedt_file(aedt_file)


class TestProjectFileWithMultipleDesigns:
    def setup_class(self):
        with Scratch(scratch_path) as self.local_scratch:
            aedt_file = os.path.join(local_path, "example_models", "Cassegrain.aedt")
            self.project_dict = load_entire_aedt_file(aedt_file)
            self.design_info = self.project_dict["ProjectPreview"]["DesignInfo"]

    def teardown_class(self):
        self.local_scratch.remove()

    def test_01_check_design_type(self):
        # there are multiple designs in this aedt file, so DesignInfo will be a list
        assert isinstance(self.design_info, list)

    def test_02_check_design_names(self):
        design_names = [design["DesignName"] for design in self.design_info]
        assert ["Cassegrain_Hybrid", "feeder", "Cassegrain_"] == design_names

    def test_03_check_first_design_jpg(self):
        jpg_file = _write_jpg(self.design_info[0], self.local_scratch.path)
        assert filecmp.cmp(jpg_file, os.path.join(local_path, "example_models", "Cassegrain_Hybrid.jpg"))


class TestProjectFileWithCoordinateSystems:
    def setup_class(self):
        with Scratch(scratch_path) as self.local_scratch:
            aedt_file = os.path.join(local_path, "example_models", "Coordinate_System.aedt")
            self.test_project = self.local_scratch.copyfile(aedt_file)
            aedt_file = os.path.join(local_path, "example_models", "Coordinate_System1.aedt")
            self.test_project1 = self.local_scratch.copyfile(aedt_file)
            aedt_file = os.path.join(local_path, "example_models", "Coordinate_System2.aedt")
            self.test_project2 = self.local_scratch.copyfile(aedt_file)
            aedt_file = os.path.join(local_path, "example_models", "Coordinate_System3.aedt")
            self.test_project3 = self.local_scratch.copyfile(aedt_file)
            self.aedtapp = Hfss(specified_version=desktop_version)

    def teardown_class(self):
        self.aedtapp._desktop.ClearMessages("", "", 3)
        assert self.aedtapp.release_desktop
        self.local_scratch.remove()
        gc.collect()

    def test_01_check_can_load_aedt_file_with_multiple_coord_systems(self):
        # implicitly this will test to make sure no exception is thrown by load_entire_aedt_file
        assert load_entire_aedt_file(self.test_project)

    def test_02_check_coordinate_system_retrival(self):
        self.aedtapp.load_project(self.test_project, close_active_proj=True)
        cs = self.aedtapp.modeler.coordinate_systems
        assert cs
        self.aedtapp.load_project(self.test_project1, close_active_proj=True)
        cs = self.aedtapp.modeler.coordinate_systems
        assert cs
        self.aedtapp.load_project(self.test_project2, close_active_proj=True)
        cs = self.aedtapp.modeler.coordinate_systems
        assert cs
        self.aedtapp.load_project(self.test_project3, close_active_proj=True)
        cs = self.aedtapp.modeler.coordinate_systems
        assert cs
