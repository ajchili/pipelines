# Before running this test you must pip install snapshottest and tensorflow==1.13.1

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

import importlib
import unittest
from nbformat.v4 import new_notebook, new_code_cell
import snapshottest

exporter = importlib.import_module("exporter")


class TestExporterMethods(snapshottest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.exporter = exporter.Exporter(100, exporter.TemplateType.BASIC)

    def test_create_cell_from_args_with_no_args(self):
        args = {}
        cell = exporter.create_cell_from_args(args)
        self.assertMatchSnapshot(cell.source)

    def test_create_cell_from_args_with_one_arg(self):
        args = {"source": "gs://ml-pipeline/data.csv"}
        cell = exporter.create_cell_from_args(args)
        self.assertMatchSnapshot(cell.source)

    # Test generates html to avoid issues with Python 3.5 where dict objects
    # do not retain order upon object creation. Due to this, we test that the
    # provided arguments exist and equal the provided value.
    def test_create_cell_from_args_with_multiple_args(self):
        nb = new_notebook()
        args = {
            "source": "gs://ml-pipeline/data.csv",
            "target_lambda": "lambda x: (x['target'] > x['fare'] * 0.2)"
        }
        code = [
            "print(variables.get('source'))",
            "print(variables.get('target_lambda'))"
        ]
        nb.cells.append(exporter.create_cell_from_args(args))
        nb.cells.append(exporter.create_cell_from_custom_code(code))
        html = self.exporter.generate_html_from_notebook(nb)
        self.assertMatchSnapshot(html)

    def test_create_cell_from_file(self):
        cell = exporter.create_cell_from_file("types/tfdv.py")
        self.assertMatchSnapshot(cell.source)

    def test_create_cell_from_custom_code(self):
        code = [
            "x = 2",
            "print(x)"
        ]
        cell = exporter.create_cell_from_custom_code(code)
        self.assertMatchSnapshot(cell.source)

    # Tests to ensure output is generated for custom visualizations.
    def test_generate_custom_visualization_html_from_notebook(self):
        nb = new_notebook()
        args = {"x": 2}
        code = ["print(variables.get('x'))"]
        nb.cells.append(exporter.create_cell_from_args(args))
        nb.cells.append(exporter.create_cell_from_custom_code(code))
        html = self.exporter.generate_html_from_notebook(nb)
        self.assertMatchSnapshot(html)

    def test_generate_roc_curve_visualization(self):
        nb = new_notebook()
        source = "gs://ml-pipeline-dataset/python-based-visualizations-test-data/roc.csv"
        args = {"is_generated": True}
        nb.cells.append(new_code_cell('source = "{}"'.format(source)))
        nb.cells.append(exporter.create_cell_from_args(args))
        nb.cells.append(exporter.create_cell_from_file("types/roc_curve.py"))
        html = self.exporter.generate_html_from_notebook(nb)
        # Ensure that no error is encountered by checking that the
        # "output_error" class does not exist in the html.
        self.assertTrue("output_error" not in html)
        # Tests that both source and variables variable are accessible within
        # the generated HTML by validating they are defined.
        self.assertTrue("&#39;source&#39; is not defined" not in html)
        self.assertTrue("&#39;variables&#39; is not defined" not in html)

    def test_generate_table_visualization(self):
        nb = new_notebook()
        source = "gs://ml-pipeline-dataset/python-based-visualizations-test-data/table.csv"
        args = {}
        nb.cells.append(new_code_cell('source = "{}"'.format(source)))
        nb.cells.append(exporter.create_cell_from_args(args))
        nb.cells.append(exporter.create_cell_from_file("types/table.py"))
        html = self.exporter.generate_html_from_notebook(nb)
        # Ensure that no error is encountered by checking that the
        # "output_error" class does not exist in the html.
        self.assertTrue("output_error" not in html)
        # Tests that both source and variables variable are accessible within
        # the generated HTML by validating they are defined.
        self.assertTrue("&#39;source&#39; is not defined" not in html)
        self.assertTrue("&#39;variables&#39; is not defined" not in html)

    def test_generate_tfdv_visualization(self):
        nb = new_notebook()
        # A tfdv.csv file exists in the ml-pipeline-dataset bucekt but it
        # appears to currently have issues downloading. The TFDV and Table
        # visualization data is also identical so no issues with either
        # visualization should arise.
        source = "gs://ml-pipeline-dataset/python-based-visualizations-test-data/table.csv"
        args = {}
        nb.cells.append(new_code_cell('source = "{}"'.format(source)))
        nb.cells.append(exporter.create_cell_from_args(args))
        nb.cells.append(exporter.create_cell_from_file("types/tfdv.py"))
        html = self.exporter.generate_html_from_notebook(nb)
        # Ensure that no error is encountered by checking that the
        # "output_error" class does not exist in the html.
        self.assertTrue("output_error" not in html)
        # Tests that both source and variables variable are accessible within
        # the generated HTML by validating they are defined.
        self.assertTrue("&#39;source&#39; is not defined" not in html)
        self.assertTrue("&#39;variables&#39; is not defined" not in html)


if __name__ == "__main__":
    unittest.main()
