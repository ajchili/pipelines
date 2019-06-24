# Copyright 2018 Google LLC
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


# TODO: add description

import argparse
import json
import os
from tensorflow.python.lib.io import file_io
from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)
import exporter


def ensure_bucket_exists_or_raise(minio_client=None):
    if minio_client is None:
        raise Exception("A minio client must be provided!")
    try:
        minio_client.make_bucket(
            "mlpipeline-visualizations", location="us-west-1")
    except BucketAlreadyOwnedByYou as err:
        pass
    except BucketAlreadyExists as err:
        pass
    except ResponseError as err:
        raise


def main(argv=None):
    # minio client use these to retrieve minio objects/artifacts
    minio_access_key = "minio"
    minio_secret_key = "minio123"
    minio_host = os.getenv("MINIO_SERVICE_SERVICE_HOST", "0.0.0.0")
    minio_port = os.getenv("MINIO_SERVICE_SERVICE_PORT", "9000")
    # construct minio endpoint from host and namespace (optional)
    minio_endpoint = "{}:{}".format(minio_host, minio_port)

    minio_client = Minio(minio_endpoint,
                         access_key=minio_access_key,
                         secret_key=minio_secret_key,
                         secure=False)

    ensure_bucket_exists_or_raise(minio_client=minio_client)
    nb = exporter.code_to_notebook('/src/visualization.py')
    exporter.generate_html_from_notebook(nb)
    try:
        with open(os.path.join(os.getcwd(), 'output.html'), 'rb') as file_data:
            file_stat = os.stat(os.path.join(os.getcwd(), 'output.html'))
            # add some sort of id to the visualization html file
            minio_client.put_object('mlpipeline-visualizations', 'object.html', file_data,
                                    file_stat.st_size, content_type='text/html')
    except ResponseError as err:
        raise


if __name__ == "__main__":
    main()
