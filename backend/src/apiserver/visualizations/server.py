import argparse
import os
import shlex

import tornado.ioloop
import tornado.web
import exporter
from nbformat.v4 import new_notebook


dirname = os.path.dirname(__file__)

parser = argparse.ArgumentParser(description='Visualization Generator')
parser.add_argument('--type', type=str, default='roc',
                    help='Type of visualization to be generated.')
parser.add_argument('--trueclass', type=str, default='true',
                    help='The name of the class as true value. If' +
                         'missing, assuming it is binary classification ' +
                         'and default to "true".')
parser.add_argument('--predictions', type=str,
                    help='GCS path of prediction file pattern.')
parser.add_argument('--target_lambda', type=str,
                    help='a lambda function as a string to determine ' +
                         'positive or negative. For example, "lambda x: ' +
                         'x[\'a\'] and x[\'b\']".')
parser.add_argument('--true_score_column', type=str, default='true',
                    help='The name of the column for positive probability.')


class VisualizationHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("alive")

    def post(self):
        args = parser.parse_args(shlex.split(
            self.get_body_argument("arguments")))
        nb = new_notebook()
        nb.cells.append(exporter.create_cell_from_args(args))
        nb.cells.append(exporter.create_cell_from_file(
            os.path.join(dirname, '{}.py'.format(args.type))))
        html = exporter.generate_html_from_notebook(nb)
        self.write(html)


if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/", VisualizationHandler),
    ])
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()