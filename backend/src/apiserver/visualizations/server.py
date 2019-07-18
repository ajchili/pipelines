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
parser.add_argument('--arguments', type=str, default='{}',
                    help='JSON string of arguments to be provided to ' +
                         'visualizations.')


class VisualizationHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("alive")

    def post(self):
        args = parser.parse_args(shlex.split(
            self.get_body_argument("arguments")))
        nb = new_notebook()
        nb.cells.append(exporter.create_cell_from_args(args.arguments))
        print("generating visualization of type {}".format(args.type))
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