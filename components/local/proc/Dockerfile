# Copyright 2019 The Kubeflow Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM ml-pipeline-local-base

RUN mkdir /usr/licenses && \
    /ml/license.sh /ml/third_party_licenses.csv /usr/licenses

RUN pip install traitlets
RUN pip install nbconvert
RUN pip install nbformat

COPY ./src /pipelines/component/src

ENTRYPOINT [ "python", "/pipelines/component/src/proc.py" ]