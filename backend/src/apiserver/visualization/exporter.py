"""
exporter.py provides utility functions for generating NotebookNode objects and
converting those objects to HTML.
"""

# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
from enum import Enum
import json
from pathlib import Path
from typing import Text
from jupyter_client import KernelManager
from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor
from nbformat import NotebookNode
from nbformat.v4 import new_code_cell


# Visualization Template types:
# - Basic: Uses the basic.tpl file within the templates directory to generate
# a visualization that contains no styling and minimal HTML tags. This is ideal
# for testing as it reduces size of generated visualization. However, for usage
# with actual visualizations it is not ideal due to its lack of javascript and
# styling which can limit usability of a visualization.
# - Full: Uses the full.tpl file within the template directory to generate a
# visualization that can be viewed as a standalone web page. The full.tpl file
# utilizes the basic.tpl file for visualizations then wraps that output with
# additional tags for javascript and style support. This is ideal for generating
# visualizations that will be displayed via the frontend.
class TemplateType(Enum):
    BASIC = 'basic'
    FULL = 'full'


class Exporter:

    def __init__(
        self,
        timeout: int = 100,
        template_type: TemplateType = TemplateType.FULL
    ):
        self.timeout = timeout
        self.template_type = template_type
        # Create custom KernelManager.
        # This will circumvent issues where kernel is shutdown after
        # preprocessing. Due to the shutdown, latency would be introduced
        # because a kernel must be started per visualization.
        self.km = KernelManager()
        self.km.start_kernel()
        self.ep = ExecutePreprocessor(
            timeout=self.timeout,
            kernel_name='python3')

    def __del__(self):
        self.shutdown_kernel()

    # Takes provided command line arguments and creates a Notebook cell object
    # with the arguments as variables.
    #
    # Returns the generated Notebook cell.
    @staticmethod
    def create_cell_from_args(args: argparse.Namespace) -> NotebookNode:
        variables = ""
        args = json.loads(args)
        for key in sorted(args.keys()):
            # Check type of variable to maintain type when converting from JSON
            # to notebook cell
            if args[key] is None or isinstance(args[key], bool):
                variables += "{} = {}\n".format(key, args[key])
            else:
                variables += '{} = "{}"\n'.format(key, args[key])

        return new_code_cell(variables)

    # Reads a python file, then creates a Notebook cell object with the
    # lines of code from the python file.
    #
    # Returns the generated Notebook cell.
    @staticmethod
    def create_cell_from_file(filepath: Text) -> NotebookNode:
        with open(filepath, 'r') as f:
            code = f.read()

        return new_code_cell(code)

    # Exports a notebook to HTML and generates any required outputs.
    #
    # Returns the generated HTML as a string.
    def generate_html_from_notebook(self, nb: NotebookNode) -> Text:
        # HTML generator and exporter object
        html_exporter = HTMLExporter()
        template_file = "templates/{}.tpl".format(self.template_type.value)
        html_exporter.template_file = str(Path.cwd() / template_file)
        # Output generator
        self.ep.preprocess(nb, {"metadata": {"path": Path.cwd()}}, self.km)

        # Export all html and outputs
        body, _ = html_exporter.from_notebook_node(nb)
        return body

    def shutdown_kernel(self):
        self.km.shutdown_kernel()
