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
# limitations under the License

import os
import json

from tensorflow.python.lib.io import file_io
import pandas as pd
from sklearn.metrics import confusion_matrix
from bokeh.layouts import row
from bokeh.plotting import figure
from bokeh.io import show
from bokeh.models import HoverTool
import gcsfs


if is_generated is False:
    schema_file = os.path.join(os.path.dirname(predictions), 'schema.json')
    schema = json.loads(file_io.read_file_to_string(schema_file))
    names = [x['name'] for x in schema]
    dfs = []
    files = file_io.get_matching_files(predictions)
    for file in files:
        with file_io.FileIO(file, 'r') as f:
            dfs.append(pd.read_csv(f, names=names))

    df = pd.concat(dfs)
    if target_lambda:
        df['target'] = df.apply(eval(target_lambda), axis=1)

    vocab = list(df['target'].unique())
    cm = confusion_matrix(df['target'], df['predicted'], labels=vocab)
    data = []
    for target_index, target_row in enumerate(cm):
        for predicted_index, count in enumerate(target_row):
            data.append((vocab[target_index], vocab[predicted_index], count))

    source = pd.DataFrame(data, columns=['target', 'predicted', 'count'])
else:
    source = pd.read_csv(predictions, header=None, names=['target', 'predicted',
                                                          'count'])

print(source)
