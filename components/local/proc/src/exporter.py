import sys
import os
from traitlets.config import Config
from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor
from nbformat.v4 import new_notebook, new_code_cell


# Reads a python file, then creates a Notebook object with the
# lines of code from the python file.
#
# Returns the generated Notebook
def code_to_notebook(filename):
    filename = os.path.join(os.getcwd(), filename)
    nb = new_notebook()
    with open(filename, 'r') as f:
        code = f.read()

    nb.cells.append(new_code_cell(code))
    return nb


# Exports a notebook to HTML and generates any required outputs.
def generate_html_from_notebook(nb, type='full'):
    # HTML gernerator and exporter object
    html_exporter = HTMLExporter()
    html_exporter.template_file = type

    # Output generator object
    ep = ExecutePreprocessor(timeout=300, kernel_name='python3')
    # If the directory does not exist this will fail
    ep.preprocess(nb, {'metadata': {'path': '/'}})

    # Export all html and outputs
    (body, _) = html_exporter.from_notebook_node(nb)
    return str(body)
