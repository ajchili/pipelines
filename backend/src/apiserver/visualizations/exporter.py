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

import os
from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor
from nbformat.v4 import new_code_cell, new_notebook
from jupyter_client import KernelManager

# Create custom KernelManager
# This will circumvent issues where kernel is shutdown after preprocessing. Due
# to the shutdown, latency is introduced because a kernel must be started per
# visualization.
km = KernelManager()
km.start_kernel()
ep = ExecutePreprocessor(timeout=300, kernel_name='python3')
# Warm up preprocessor
ep.preprocess(new_notebook(), {'metadata': {'path': os.getcwd()}}, km)


# Takes provided command line arguments and creates a Notebook cell object with
# the arguments as variables.
#
# Returns the generated Notebook cell
def create_cell_from_args(args):
    variables = ""
    args = vars(args)
    for key in args:
        if isinstance(args[key], (type(None), bool)):
            variables += "{} = {}\n".format(key, args[key])
        else:
            variables += "{} = \"{}\"\n".format(key, args[key])

    return new_code_cell(variables)


# Reads a python file, then creates a Notebook cell object with the
# lines of code from the python file.
#
# Returns the generated Notebook cell
def create_cell_from_file(filepath):
    with open(filepath, 'r') as f:
        code = f.read()

    return new_code_cell(code)


# Exports a notebook to HTML and generates any required outputs.
#
# Returns the generated HTML as a string
def generate_html_from_notebook(nb):
    # HTML generator and exporter object
    html_exporter = HTMLExporter()
    dirname = os.path.dirname(__file__)
    html_exporter.template_file = os.path.join(dirname,
                                               'templates/full.tpl')
    # Output generator object
    ep.preprocess(nb, {'metadata': {'path': os.getcwd()}}, km)

    # Export all html and outputs
    (body, _) = html_exporter.from_notebook_node(nb)
    return body.replace('contentWindow.document.write', 'srcdoc=')


def shutdown_kernel():
    km.shutdown_kernel()
