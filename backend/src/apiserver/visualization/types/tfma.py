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

import tensorflow_model_analysis as tfma

eval_shared_model = tfma.default_eval_shared_model(eval_saved_model_path=source)
eval_result = tfma.run_model_analysis(
    eval_shared_model=eval_shared_model,
    data_location=source,
    file_format='tfrecords')

if variables.get("slicing_column", False) == False:
    tfma.view.render_slicing_metrics(eval_result)
else:
    tfma.view.render_slicing_metrics(eval_result,
                                     slicing_column=variables.get("slicing_column"))


