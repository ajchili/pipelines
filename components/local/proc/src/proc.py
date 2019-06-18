import argparse
import json
import os
import urlparse
import pandas as pd
from sklearn.metrics import roc_curve, roc_auc_score
from tensorflow.python.lib.io import file_io
import exporter


def main(argv=None):
    parser = argparse.ArgumentParser(description='ML Trainer')
    parser.add_argument('--predictions', type=str,
                        help='GCS path of prediction file pattern.')
    parser.add_argument('--trueclass', type=str, default='true',
                        help='The name of the class as true value. If missing, assuming it is ' +
                             'binary classification and default to "true".')
    parser.add_argument('--true_score_column', type=str, default='true',
                        help='The name of the column for positive prob. If missing, assuming it is ' +
                             'binary classification and defaults to "true".')
    parser.add_argument('--target_lambda', type=str,
                        help='a lambda function as a string to determine positive or negative.' +
                             'For example, "lambda x: x[\'a\'] and x[\'b\']". If missing, ' +
                             'input must have a "target" column.')
    parser.add_argument('--output', type=str,
                        help='GCS path of the output directory.')
    args = parser.parse_args()

    storage_service_scheme = urlparse.urlparse(args.output).scheme
    on_cloud = True if storage_service_scheme else False
    if not on_cloud and not os.path.exists(args.output):
        os.makedirs(args.output)

    html_file = os.path.join(args.output, '/pipelines/component/src/test.html')
    nb = exporter.code_to_notebook('/pipelines/component/src/test.py')
    body = exporter.generate_html_from_notebook(nb)
    os.open(html_file, 'w')
    os.write(body)


    metadata = {
        'outputs': [{
            'storage': 'gcs',
            'source': html_file,
            'type': 'web-app'
        }]
    }
    with file_io.FileIO('/mlpipeline-ui-metadata.json', 'w') as f:
        json.dump(metadata, f)


if __name__ == "__main__":
    main()
