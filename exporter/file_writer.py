"""
file_writer.py

Common file and directory utilities for the exporter.
"""

import os
import shutil
from ..utils.logger import Logger


class FileWriter:

    def __init__(self, base_directory):

        self.base_directory = os.path.abspath(base_directory)
        
        # Validate that base directory can be created/written
        self._validate_path()

    # =====================================================
    # Path Validation
    # =====================================================

    def _validate_path(self):
        """Validate that the export path is writable."""
        try:
            # Try to create the directory if it doesn't exist
            os.makedirs(self.base_directory, exist_ok=True)
            
            # Try to write a test file to verify writability
            test_file = os.path.join(self.base_directory, ".write_test")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            
        except OSError as e:
            raise RuntimeError(
                f"Export directory '{self.base_directory}' is not writable: {str(e)}"
            )
        except Exception as e:
            raise RuntimeError(
                f"Cannot access export directory '{self.base_directory}': {str(e)}"
            )

    # =====================================================
    # Directory Functions
    # =====================================================

    def create_directory(self, *folders):

        """
        Create a directory relative to the base directory.

        Example:
            create_directory("robot_description", "urdf")
        """

        path = os.path.join(
            self.base_directory,
            *folders
        )

        os.makedirs(path, exist_ok=True)

        return path

    # =====================================================
    # File Functions
    # =====================================================

    def write_file(self, relative_path, content):

        """
        Write text to a file.

        Example:
            write_file(
                "package.xml",
                xml_string
            )
        """

        filepath = os.path.join(
            self.base_directory,
            relative_path
        )

        directory = os.path.dirname(filepath)

        os.makedirs(directory, exist_ok=True)

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(content)

        return filepath

    def append_file(self, relative_path, content):

        """
        Append text to a file.
        """

        filepath = os.path.join(
            self.base_directory,
            relative_path
        )

        directory = os.path.dirname(filepath)

        os.makedirs(directory, exist_ok=True)

        with open(
            filepath,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(content)

        return filepath

    def read_file(self, relative_path):

        """
        Read a text file.
        """

        filepath = os.path.join(
            self.base_directory,
            relative_path
        )

        with open(
            filepath,
            "r",
            encoding="utf-8"
        ) as file:

            return file.read()

    # =====================================================
    # Template Functions
    # =====================================================

    def copy_file(self, source, destination):

        """
        Copy a file into the export directory.
        """

        destination_path = os.path.join(
            self.base_directory,
            destination
        )

        os.makedirs(
            os.path.dirname(destination_path),
            exist_ok=True
        )

        shutil.copy2(
            source,
            destination_path
        )

        return destination_path

    def copy_directory(self, source, destination):

        """
        Copy an entire directory.
        """

        destination_path = os.path.join(
            self.base_directory,
            destination
        )

        shutil.copytree(
            source,
            destination_path,
            dirs_exist_ok=True
        )

        return destination_path

    # =====================================================
    # Utility Functions
    # =====================================================

    def exists(self, relative_path):

        return os.path.exists(
            os.path.join(
                self.base_directory,
                relative_path
            )
        )

    def remove_file(self, relative_path):

        filepath = os.path.join(
            self.base_directory,
            relative_path
        )

        if os.path.isfile(filepath):

            os.remove(filepath)

    def remove_directory(self, relative_path):

        directory = os.path.join(
            self.base_directory,
            relative_path
        )

        if os.path.isdir(directory):

            shutil.rmtree(directory)

    def get_absolute_path(self, relative_path=""):

        return os.path.join(
            self.base_directory,
            relative_path
        )